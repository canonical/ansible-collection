#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: network_interface_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Gets information about network interfaces on a specific device.
description:
  - Get information from a specific device, can also filter based on mac_address.
  - Returns information about physical and linked network interfaces.
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
"""

EXAMPLES = r"""
- name: List nics from instance machine
  maas.maas.network_interface_physical_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine: instance.maas
    mac_address: 00:16:3e:46:25:e3
  register: nic_info
- ansible.builtin.debug:
    var: nic_info
"""

RETURN = r"""
record:
  description:
    - Get information from nic.
  returned: success
  type: dict
  sample:
    children: []
    discovered: []
    effective_mtu: 1500
    enabled: true
    firmware_version: null
    id: 208
    interface_speed: 0
    link_connected: true
    link_speed: 0
    links:
    - id: 1152
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
    mac_address: 00:16:3e:46:25:e3
    name: my_first
    numa_node: 0
    params: ''
    parents: []
    product: null
    resource_uri: /MAAS/api/2.0/nodes/ks7wsq/interfaces/208/
    sriov_max_vf: 0
    system_id: ks7wsq
    tags: []
    type: physical
    vendor: null
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

from ..module_utils import arguments, errors
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.machine import Machine


def run(module, client):
    machine_obj = Machine.get_by_fqdn(module, client, must_exist=True)
    if module.params["mac_address"]:
        nic_obj = machine_obj.find_nic_by_mac(module.params["mac_address"])
        if nic_obj:
            response = client.get(
                f"/api/2.0/nodes/{machine_obj.id}/interfaces/{nic_obj.id}/",
            ).json
    else:
        response = client.get(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/",
        ).json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            machine=dict(
                type="str",
                required=True,
            ),
            mac_address=dict(
                type="str",
            ),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
