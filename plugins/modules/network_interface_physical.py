#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: network_interface_physical

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Creates a network interface on a specified virtual machine.
description:
  - Create VM on a specified host.
version_added: 1.0.0
extends_documentation_fragment:
  - maas.maas.cluster_instance
seealso: []
options:
  machine:
    description:
      - Fully qualified domain name of the machine to be deleted, deployed or released.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
    required: True
  mac_address:
    description: Mac address of the network interface.
    type: str
    required: true
  vlan:
    description:
      - Virtual LAN id.
      - If not provided, network interface is considered disconnected.
    type: str
  name:
    description: Network interface name.
    type: str
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
- name: Create new nic on sunny-raptor host with machine calm-guinea
  maas.maas.network_interface_physical:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine: calm-guinea
    state: present
    mac_address: '00:16:3e:ae:78:75'
    vlan: 5002
    name: new_nic
    mtu: 1700
    tags:
      - first
      - second
  register: nic_info

- debug:
    var: nic_info

- name: Delete nic from machine calm-guinea on host sunny-raptor
  maas.maas.network_interface_physical:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine: calm-guinea
    state: absent
    mac_address: '00:16:3e:ae:78:75'
  register: nic_info

- debug:
    var: nic_info
"""

RETURN = r"""
record:
  description:
    - Crated or deleted network interface.
  returned: success
  type: dict
  sample:
    fabric: fabric-1
    id: 327
    ip_address: 10.10.10.190
    mac: 00:16:3e:ae:78:75
    mtu: 1700
    name: new_nic
    subnet_cidr: 10.10.10.0/24
    tags:
      - first
      - second
    vlan: vlan-5
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.machine import Machine
from ..module_utils.network_interface import NetworkInterface
from ..module_utils.state import MachineTaskState, NicState
from ..module_utils.utils import is_changed


def ensure_present(module, client, machine_obj):
    before = None
    after = None
    new_nic_obj = NetworkInterface.from_ansible(module.params)
    existing_nic = machine_obj.find_nic_by_mac(new_nic_obj.mac_address)
    if existing_nic and existing_nic.needs_update(new_nic_obj):
        before = existing_nic.to_ansible()
        new_nic_obj.send_update_request(
            client,
            machine_obj,
            new_nic_obj.payload_for_update(),
            existing_nic.id,
        )
    elif not existing_nic:
        new_nic_obj.send_create_request(
            client, machine_obj, new_nic_obj.payload_for_create()
        )
    else:
        return (
            is_changed(before, after),
            after,
            dict(before=before, after=after),
        )
    updated_machine_obj = Machine.get_by_fqdn(
        module, client, must_exist=True, name_field_ansible="machine"
    )
    after = updated_machine_obj.find_nic_by_mac(
        new_nic_obj.mac_address
    ).to_ansible()
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(module, client, machine_obj):
    before = None
    after = None
    nic_to_delete_obj = machine_obj.find_nic_by_mac(
        module.params["mac_address"]
    )
    if nic_to_delete_obj:
        before = nic_to_delete_obj.to_ansible()
        nic_to_delete_obj.send_delete_request(
            client, machine_obj, nic_to_delete_obj.id
        )
        # Check if nic was actually deleted, if not failed = True in playbook.
        updated_machine_obj = Machine.get_by_fqdn(
            module, client, must_exist=True, name_field_ansible="machine"
        )
        if updated_machine_obj.find_nic_by_mac(nic_to_delete_obj.mac_address):
            raise errors.MaasError(
                f"Delete network interface task failed with mac: {nic_to_delete_obj.mac_address}"
            )
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
    # Machine needs to be allocated, broken or ready.
    machine_obj = Machine.get_by_fqdn(
        module, client, must_exist=True, name_field_ansible="machine"
    )
    if machine_obj.status not in [
        MachineTaskState.ready,
        MachineTaskState.allocated,
        MachineTaskState.allocating,
        MachineTaskState.broken,
        MachineTaskState.comissioning,
    ]:
        raise errors.MaasError(
            f"Machine {machine_obj.hostname} is not in the right state, needs to be in Ready, Allocated or Broken."
        )
    if machine_obj.status in [
        MachineTaskState.allocating,
        MachineTaskState.comissioning,
    ]:
        Machine.wait_for_state(
            machine_obj.id,
            client,
            False,
            *[
                MachineTaskState.ready.value,
                MachineTaskState.broken.value,
                MachineTaskState.allocated.value,
            ],
        )
    if module.params["state"] == NicState.present:
        changed, records, diff = ensure_present(module, client, machine_obj)
    else:
        changed, records, diff = ensure_absent(module, client, machine_obj)
    return changed, records, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            machine=dict(
                type="str",
                required=True,
            ),
            mac_address=dict(
                type="str",
                required=True,
            ),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            vlan=dict(
                type="str",
            ),
            name=dict(
                type="str",
            ),
            mtu=dict(
                type="int",
            ),
            tags=dict(
                type="list",
                elements="str",
            ),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
