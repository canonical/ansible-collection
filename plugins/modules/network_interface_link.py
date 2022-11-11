#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
module: network_interface_link

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Manages network interfaces on a specific machine.
description: Connects, updates or disconnects an existing network interface on a specified machine.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  machine:
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
  subnet:
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
- name: Create subnet link on VM new-machine-3.test-domain with network interface enp5s0
  canonical.maas.network_interface_link:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine: new-machine-3.test-domain
    state: present
    mode: STATIC
    network_interface: enp5s0
    subnet: 10.10.10.0/24
    ip_address: 10.10.10.4
    default_gateway: True
  register: nic_info

- name: Delete subnet link on VM new-machine-3.test-domain with network interface enp5s0
  canonical.maas.network_interface_link:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine: new-machine-3.test-domain
    state: absent
    mode: STATIC
    network_interface: enp5s0
    subnet: 10.10.10.0/24
    ip_address: 10.10.10.4
    default_gateway: True
  register: nic_info
"""

RETURN = r"""
record:
  description:
    - Created or deleted subnet link.
  returned: success
  type: dict
  sample:
    id: 166
    mode: auto
    subnet:
      active_discovery: false
      allow_dns: true
      allow_proxy: true
      cidr: 10.10.10.0/24
      description: ''
      disabled_boot_architectures: []
      dns_servers: []
      gateway_ip: 10.10.10.1
      id: 2
      managed: true
      name: 10.10.10.0/24
      rdns_mode: 2
      resource_uri: /MAAS/api/2.0/subnets/2/
      space: undefined
      vlan:
        dhcp_on: true
        external_dhcp: null
        fabric: fabric-1
        fabric_id: 1
        id: 5002
        mtu: 1500
        name: untagged
        primary_rack: kwxmgm
        relay_vlan: null
        resource_uri: /MAAS/api/2.0/vlans/5002/
        secondary_rack: null
        space: undefined
        vid: 0
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.network_interface import NetworkInterface
from ..module_utils import arguments, errors
from ..module_utils.state import NicState, MachineTaskState
from ..module_utils.machine import Machine
from ..module_utils.utils import is_changed
from ..module_utils.cluster_instance import get_oauth1_client


def ensure_present(module, client, machine_obj):
    # Creates an alias not an actual physical nic.
    before = None
    after = None
    existing_nic_obj = machine_obj.find_nic_by_name(module.params["network_interface"])
    new_nic_obj = NetworkInterface.from_ansible(module.params)
    if not existing_nic_obj:
        raise errors.MaasError(
            f"Network interface with name - {module.params['network_interface']} - not found"
        )
    existing_linked_alias = existing_nic_obj.find_linked_alias_by_cidr(module)
    if existing_linked_alias and NetworkInterface.alias_needs_update(
        client, existing_linked_alias, module
    ):
        # The only way to update alias is to delete it and make new. API endpoint is missing.
        before = existing_linked_alias
        existing_nic_obj.send_unlink_subnet_request(
            client, machine_obj, existing_linked_alias["id"]
        )
        new_nic_obj.send_link_subnet_request(
            client,
            machine_obj,
            new_nic_obj.payload_for_link_subnet(client, existing_nic_obj.fabric),
            existing_nic_obj.id,
        )
        updated_machine_obj = Machine.get_by_fqdn(
            module, client, must_exist=True, name_field_ansible="machine"
        )
        updated_nic_obj = updated_machine_obj.find_nic_by_name(new_nic_obj.name)
        after = updated_nic_obj.find_linked_alias_by_cidr(module)
    elif not existing_linked_alias:
        new_nic_obj.send_link_subnet_request(
            client,
            machine_obj,
            new_nic_obj.payload_for_link_subnet(client, existing_nic_obj.fabric),
            existing_nic_obj.id,
        )
        updated_machine_obj = Machine.get_by_fqdn(
            module, client, must_exist=True, name_field_ansible="machine"
        )
        updated_nic_obj = updated_machine_obj.find_nic_by_name(new_nic_obj.name)
        after = updated_nic_obj.find_linked_alias_by_cidr(module)
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(module, client, machine_obj):
    # Deletes an alias not an actual physical nic.
    before = None
    after = None
    nic_to_delete_obj = machine_obj.find_nic_by_name(module.params["network_interface"])
    if nic_to_delete_obj:
        linked_alias_to_delete = nic_to_delete_obj.find_linked_alias_by_cidr(module)
        if linked_alias_to_delete:
            before = linked_alias_to_delete
            nic_to_delete_obj.send_unlink_subnet_request(
                client, machine_obj, linked_alias_to_delete["id"]
            )
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
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
        changed, record, diff = ensure_present(module, client, machine_obj)
    else:
        changed, record, diff = ensure_absent(module, client, machine_obj)
    return changed, record, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            machine=dict(
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
        client = get_oauth1_client(module.params)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
