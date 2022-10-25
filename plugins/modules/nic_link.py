#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible_collections.canonical.maas.plugins.module_utils.network_interface import (
    NetworkInterface,
)

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
  fqdn:
    description:
      - Fully qualified domain name of the machine to be deleted, deployed or released.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
    required: True
  network_interface:
    description: Name of the network interface.
    type: str
    required: True
  state:
    description: Prefered state of the network interface.
    choices: [ present, absent ]
    type: str
    required: True
  subnet_cidr:
    description:
      - The subnet CIDR for the network interface.
      - Matches an interface attached to the specified subnet CIDR. (For example, "192.168.0.0/24".)
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
from ..module_utils.state import NicState
from ..module_utils.machine import Machine
from ..module_utils.utils import is_changed


def ensure_present(module, client, machine_obj):
    before = None
    after = None
    existing_nic_obj = machine_obj.find_nic_by_name(module.params["network_interface"])
    new_nic_obj = NetworkInterface.from_ansible(module.params)
    if not existing_nic_obj:
        raise errors.MaasError(
            f"Network interface with name - {module.params['network_interface']} - not found"
        )
    if existing_nic_obj.needs_update(new_nic_obj):
        before = existing_nic_obj.to_ansible()
        new_nic_obj.send_link_subnet_request(
            client,
            machine_obj,
            new_nic_obj.payload_for_link_subnet(),
            existing_nic_obj.id,
        )
        updated_machine_obj = Machine.get_by_fqdn(module, client, must_exist=True)
        after = updated_machine_obj.find_nic_by_name(new_nic_obj.name).to_ansible()
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(module, client, machine_obj):
    before = None
    after = None
    nic_to_delete_obj = machine_obj.find_nic_by_name(module.params["network_interface"])
    if nic_to_delete_obj:
        nic_to_delete_obj.send_unlink_subnet_request(
            client,
            machine_obj,
            nic_to_delete_obj.payload_for_unlink_subnet(),
            nic_to_delete_obj.id,
        )
        updated_machine_obj = Machine.get_by_fqdn(module, client, must_exist=True)
        after = updated_machine_obj.find_nic_by_name(nic_to_delete_obj.name).to_ansible()
    if after:
      raise errors.MaasError(
        f"Delete network interface task failed with name: {nic_to_delete_obj.name}"
      )
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
    machine_obj = Machine.get_by_fqdn(module, client, must_exist=True)
    if module.params["state"] == NicState.present:
        changed, record, diff = ensure_present(module, client, machine_obj)
    else:
        changed, record, diff = ensure_absent(module, client, machine_obj)
    return changed, record, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            fqdn=dict(
                type="str",
                required=True,
            ),
            network_interface=dict(
                type="str",
                required=True,
            ),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            subnet_cidr=dict(
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
