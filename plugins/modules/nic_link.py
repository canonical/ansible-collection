#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: nic_link

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Manages network interfaces on a specific machine.
description: Connects, updates or disconnects an existing network interface on a specified machine.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  vm_host:
    description: Name of the host.
    type: str
    required: True
  hostname:
    description:
      - Name of the virtual machine.
      - Underscores are not supported.
    type: str
    required: True
  interface_name:
    description: Name of the network interface.
    type: str
    required: True
  subnet:
    description: The subnet CIDR or ID.
    type: str
    required: True
  default_gateway:
    description: The default gateway of the network interface
    type: bool
    default: False
  ip_address:
    description: Valid static IP address of the network interface.
    type: str
  mode:
    description: Connection mode to subnet.
    choices: [ AUTO, DHCP, STATIC, LINK_UP ]
    default: AUTO
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
record:
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vmhost import VMHost
from ..module_utils.machine import Machine
from ..module_utils.utils import is_changed, required_one_of


def run(module, client):
    return changed, record, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_host=dict(
                type="str",
                required=True,
            ),
            hostname=dict(
                type="str",
                required=True,
            ),
            interface_name=dict(
                type="str",
                required=True,
            ),
            subnet=dict(
                type="str",
                required=True,
            ),
            mode=dict(
                type="str",
                choices=["AUTO", "DHCP", "STATIC", "LINK_UP"],
                default="AUTO",
            ),
            default_gateway=dict(
                type="bool",
                default=False,
            ),
            ip_address=dict(
                type="str",
            ),
        ),
    )

    try:
        cluster_instance = module.params["cluster_instance"]
        host = cluster_instance["host"]
        consumer_key = cluster_instance["customer_key"]
        token_key = cluster_instance["token_key"]
        token_secret = cluster_instance["token_secret"]

        client = Client(host, token_key, token_secret, consumer_key)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
