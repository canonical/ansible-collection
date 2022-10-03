#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from socket import AF_ECONET

from ansible_collections.canonical.maas.plugins.module_utils.network_interface import NetworkInterface

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_nic_physical

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Creates a network interface on a specified virtual machine.
description:
  - Create VM on a specified host.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.instance
seealso: []
options:
  machine_name:
    description: Name of the virtual machine.
    type: str
    required: True
  mac_address:
    description:
      - Mac address of the network interface.
      - Required when creating network interface.
    type: str
  vlan:
    description: Virtual LAN.
    type: str
    default: untagged
  name:
    description:
      - Network interface name.
      - Used for identification.
    type: str
    required: true
  state:
    description: State of the network interface.
    type: str
    choices: [ present, absent ]
    required: true
  mtu:
    description: Maximum transmission unit.
    type: int
  tags:
    description: List of tags.
    type: list
    elements: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
records:  
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.state import NicState
from ..module_utils.client import Client
from ..module_utils.machine import Machine
from ..module_utils.network_interface import NetworkInterface
from ..module_utils.utils import is_changed


def ensure_present(module, client, machine_obj):
    before = []
    after = []
    new_nic_obj = NetworkInterface.from_ansible(module.params)
    existing_nic = machine_obj.find_nic_by_name(new_nic_obj.name)
    if existing_nic:
        if existing_nic.needs_update(new_nic_obj):
            before.append(existing_nic)
            new_nic_obj.send_update_request(new_nic_obj.payload_for_update())
            after.append()
    else:
        new_nic_obj.send_create_request(new_nic_obj.payload_for_create())
        after.append()
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(module, client, machine_obj):
    before = []
    after = []
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
    machine_obj = Machine.get_by_name(module, client, must_exist=True)
    if module.params["state"] == NicState.present:
        changed, records, diff = ensure_present(module, client, machine_obj)
    else:
        changed, records, diff = ensure_absent(module, client, machine_obj)
    return changed, records, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("instance"),
            machine_name=dict(
                type="str",
                required=True,
            ),
            mac_address=dict(
                type="str",
            ),
            state=dict(
                type="str",
                choices=["present", "absent"],
            ),
            vlan=dict(
                type="str",
            ),
            name=dict(
                type="str",
                required=True,
            ),
            mtu=dict(
                type="int",
            ),
            tags=dict(
                type="list",
                elements="str",
            ),
        ),
        required_if=[
            ("state", "present", ("mac_address",)),
        ],
    )

    try:
        host = module.params["instance"]["host"]
        client_key = module.params["instance"]["client_key"]
        token_key = module.params["instance"]["token_key"]
        token_secret = module.params["instance"]["token_secret"]

        client = Client(host, token_key, token_secret, client_key)
        changed, records, diff = run(module, client)
        module.exit_json(changed=changed, records=records, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
