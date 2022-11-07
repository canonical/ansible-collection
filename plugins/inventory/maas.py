# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: maas
author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Inventory source for Canonical MAAS.
description:
  - Builds an inventory containing VMs on Canonical MAAS.
  - Does not support caching.
version_added: 1.0.0
seealso: []
options:
  plugin:
    description:
      - The name of the MAAS Inventory Plugin.
      - This should always be C(canonical.maas.maas).
    required: true
    type: str
    choices: [ canonical.maas.maas ]
  status:
    description:
      - If missing, all VMs are included into inventory.
      - If set, then only VMs with selected status are included into inventory.
    type: str
    choices: [ ready, broken, new ]
"""
EXAMPLES = r"""
# A trivial example that creates a list of all VMs.
# No groups will be created - all the resulting hosts are ungrouped.

plugin: canonical.maas.maas

# `ansible-inventory -i examples/hypercore_inventory.yaml --graph` output:
#@all:
#  |--@grp0:
#  |  |--ci-inventory-vm4
#  |  |--ci-inventory-vm6
#  |--@grp1:
#  |  |--ci-inventory-vm5
#  |  |--ci-inventory-vm6
#  |--@ungrouped:
#  |  |--ci-inventory-vm2
#  |  |--ci-inventory-vm3


# Example with all available parameters and how to set them.
# A group "my-group" is created where all the VMs with "ansbile_enable" tag are added.
# For VM "ci-inventory-vm6" we added values for host and user, every other VM has default values.

plugin: canonical.maas.maas

status: ready

# `ansible-inventory -i hypercore_inventory.yaml --list` output:
#{
#    "_meta": {
#        "hostvars": {
#            "ci-inventory-vm2": {
#                "ansible_host": "10.0.0.2",
#               "ansible_port": 22,
#                "ansible_user": "root"
#            },
#            "ci-inventory-vm3": {
#               "ansible_host": "10.0.0.3",
#               "ansible_port": 22,
#               "ansible_user": "root"
#            },
#            "ci-inventory-vm4": {
#               "ansible_host": "10.0.0.4",
#               "ansible_port": 22,
#               "ansible_user": "root"
#            },
#            "ci-inventory-vm5": {
#               "ansible_host": "ci-inventory-vm5",
#               "ansible_port": 22,
#               "ansible_user": "root"
#            },
#            "ci-inventory-vm6": {
#               "ansible_host": "ci-inventory-vm6",
#               "ansible_port": 22,
#               "ansible_user": "root"
#           }
#       }
#    },
#    "all": {
#        "children": [
#           "grp0",
#           "grp1",
#           "ungrouped"
#        ]
#    },
#   "grp0": {
#        "hosts": [
#           "ci-inventory-vm4",
#           "ci-inventory-vm6"
#        ]
#   },
#    "grp1": {
#        "hosts": [
#            "ci-inventory-vm5",
#            "ci-inventory-vm6"
#        ]
#    },
#    "ungrouped": {
#        "hosts": [
#            "ci-inventory-vm2",
#           "ci-inventory-vm3"
#        ]
#   }
#}


"""
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
import yaml
import logging
from ..module_utils import errors
from ..module_utils.client import Client
import os

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class LdapBaseException(Exception):
    pass


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "maas"  # used internally by Ansible, it should match the file name but not required

    @classmethod
    def read_config_data(cls, path, env):
        """
        Reads and validates the inventory source file and environ,
        storing the provided configuration as options.
        """
        with open(path, "r") as inventory_src:
            cfg = yaml.safe_load(inventory_src)
        return cfg

    def verify_file(self, path):
        """
        return true/false if this is possibly a valid file for this plugin to consume
        """
        # only check file is yaml, and contains magic plugin key with correct value.
        with open(path, "r") as inventory_src:
            config_contents = yaml.safe_load(inventory_src)
        plugin = config_contents.get("plugin")
        if not plugin:
            return False
        if plugin not in [self.NAME, "canonical.maas.maas"]:
            return False
        return True

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path)
        cfg = self.read_config_data(path, os.environ)

        # Try getting variables from env
        try:
            host = os.getenv("MAAS_HOST")
            token_key = os.getenv("MAAS_TOKEN_KEY")
            token_secret = os.getenv("MAAS_TOKEN_SECRET")
            customer_key = os.getenv("MAAS_CUSTOMER_KEY")
        except KeyError:
            raise errors.MaasError(
                "Missing parameters: MAAS_HOST, MAAS_TOKEN_KEY, MAAS_TOKEN_SECRET, MAAS_CUSTOMER_KEY."
            )
        client = Client(host, token_key, token_secret, customer_key)

        vms = client.get("/api/2.0/machines/")

        for vm in vms:
            groups = []
            ansible_user = None
            ansible_port = None
            ansible_ssh_private_key_file = None
            include = True
            tags = vm["tags"].split(",")
            if (
                "look_for_ansible_enable" in cfg
                and cfg["look_for_ansible_enable"]
                and "look_for_ansible_disable" in cfg
                and cfg["look_for_ansible_disable"]
            ):
                include = False
                if "ansible_enable" in tags:
                    include = True
                if "ansible_disable" in tags:
                    include = False
            elif "look_for_ansible_enable" in cfg and cfg["look_for_ansible_enable"]:
                include = False
                if "ansible_enable" in tags:
                    include = True
            elif "look_for_ansible_disable" in cfg and cfg["look_for_ansible_disable"]:
                include = True
                if "ansible_disable" in tags:
                    include = False
            for tag in tags:
                if (
                    tag.startswith("ansible_group__")
                    and tag[len("ansible_group__") :] not in groups
                ):
                    groups.append(tag[len("ansible_group__") :])
                elif tag.startswith("ansible_user__"):
                    ansible_user = tag[len("ansible_user__") :]
                elif tag.startswith("ansible_port__"):
                    ansible_port = int(tag[len("ansible_port__") :])
                elif tag.startswith("ansible_ssh_private_key_file"):
                    ansible_ssh_private_key_file = tag[
                        len("ansible_ssh_private_key_file__") :
                    ]
            if include:
                # Group
                inventory = self.add_group(inventory, groups, vm["name"])
                ansible_host = vm["name"]
                # Find ansible_host
                # For time being, just use the very first IP address.
                # Later - get smarter. Use IP address from specific VLAN maybe.
                # But end user is always most smart - use tag ansible_host if it is set;
                # this will allow use of arbitrary IP or even DNS name.
                for nic in vm["netDevs"]:
                    if nic["ipv4Addresses"]:
                        ansible_host = nic["ipv4Addresses"][0]
                        break
                for tag in tags:
                    if tag.startswith("ansible_host__"):
                        ansible_host = tag[len("ansible_host__") :]
                # Host
                inventory = self.add_host(inventory, ansible_host, vm["name"])
