# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
name: inventory
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
      - This should always be C(canonical.maas.inventory).
    required: true
    type: str
    choices: [ canonical.maas.inventory ]
  status:
    description:
      - If missing, all VMs are included into inventory.
      - If set, then only VMs with selected status are included into inventory.
    type: str
    choices: [ ready, broken, new, allocated, deployed, commissioning, testing, failed commissioning, failed deployment ]
"""
EXAMPLES = r"""
# A trivial example that creates a list of all VMs.
# VMs are grouped based on their domains.
# In the example, two domains are being used: "maas" and "test".

plugin: canonical.maas.inventory

# `ansible-inventory -i examples/maas_inventory.yaml --graph` output:
#@all:
#  |--@maas:
#  |  |--first.maas
#  |--@test:
#  |  |--second.test
#  |--@ungrouped:

# `ansible-inventory -i maas_inventory.yaml --list` output:
#{
#    "_meta": {
#        "hostvars": {}
#    },
#    "all": {
#        "children": [
#            "maas",
#            "test",
#            "ungrouped"
#        ]
#    },
#    "maas": {
#        "hosts": [
#            "first.maas"
#        ]
#    },
#    "test": {
#        "hosts": [
#            "second.test"
#        ]
#    }
#}

# Example with all available parameters and how to set them.
# A group "test" is created based on the domain name "test".
# Only VMs with status "ready", are added to the group.

plugin: canonical.maas.inventory

status: ready

# `ansible-inventory -i examples/maas_inventory.yaml --graph` output:
#@all:
#  |--@test:
#  |  |--second.test
#  |--@ungrouped:

# `ansible-inventory -i maas_inventory.yaml --list` output:
#{
#    "_meta": {
#        "hostvars": {}
#    },
#    "all": {
#        "children": [
#            "test",
#            "ungrouped"
#        ]
#    },
#    "test": {
#        "hosts": [
#            "second.test"
#        ]
#    }
#}

"""
import logging
import os

from ansible.plugins.inventory import (
    BaseInventoryPlugin,
    Cacheable,
    Constructable,
)
import yaml

from ..module_utils import errors
from ..module_utils.client import Client

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class LdapBaseException(Exception):
    pass


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "inventory"  # used internally by Ansible, it should match the file name but not required

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
        if plugin not in [self.NAME, "canonical.maas.inventory"]:
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

        machine_list = client.get("/api/2.0/machines/").json

        for machine in machine_list:
            include = False
            if (
                "status" not in cfg
                or "status" in cfg
                and cfg["status"].lower() == machine["status_name"].lower()
            ):
                include = True
            if include:
                # Group
                inventory.add_group(machine["domain"]["name"])
                # Host
                inventory.add_host(
                    machine["fqdn"], group=machine["domain"]["name"]
                )
                # Variables
                inventory.set_variable(
                    machine["fqdn"], "ansible_host", machine["fqdn"]
                )
                inventory.set_variable(
                    machine["fqdn"], "ansible_group", machine["domain"]["name"]
                )
