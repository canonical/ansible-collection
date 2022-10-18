#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_host_machine

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Creates a virtual machine on a specified host.
description:
  - Create VM on a specified host.
  - Does not support update or delete, only create.
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
  cores:
    description: The number of CPU cores.
    type: int
    default: 1
  pinned_cores:
    description:
      - List of host CPU cores to pin the VM to.
      - pinned_cores and cores are mutually exclusive.
    type: int
  zone:
    description: The ID of the zone in which to put the newly composed machine.
    type: int
  pool:
    description: The ID of the pool in which to put the newly composed machine.
    type: int
  domain:
    description: The ID of the domain in which to put the newly composed machine.
    type: int
  memory:
    description:  The VM host machine RAM memory, specified in MB.
    type: int
    default: 2048
  storage_disks:
    description:
      - Storage disks.
    type: list
    elements: dict
    suboptions:
      size_gigabytes:
        type: int
        description: Disk size in gigabytes.
        required: true
  network_interfaces:
    description:
      - Network interface.
    type: dict
    suboptions:
      label_name:
        type: str
        description:
          - The network interface label name.
          - Network interface label name as shown in the web aplication.
        required: true
      name:
        type: str
        description:
          - The network interface name.
          - Matches an interface with the specified name. (For example, "eth0".)
      subnet_cidr:
        type: str
        description:
          - The subnet CIDR for the network interface.
          - Matches an interface attached to the specified subnet CIDR. (For example, "192.168.0.0/24".)
      ip_address:
        type: str
        description:
          - Ip address.
          - Matches an interface whose VLAN is on the subnet implied by the given IP address.
      fabric:
        type: str
        description:
          - The fabric for the network interface.
          - Matches an interface attached to the specified fabric.
      vlan:
        type: str
        description:
          - The VLAN for the network interface.
          - Matches an interface on the specified VLAN.
"""

EXAMPLES = r"""
- name: Create machine with compose
  hosts: localhost
  tasks:
  - name: Create new machine on sunny-raptor host
    canonical.maas.vm_host_machine:
      cluster_instance:
        host: host-ip
        token_key: token-key
        token_secret: token-secret
        customer_key: customer-key
      vm_host: sunny-raptor
      hostname: new-machine-3
      cores: 2
      memory: 2048
      zone: 1
      pool: 0
      domain: 0
      network_interfaces:
        label_name: my-net
        subnet_cidr: "10.10.10.0/24"
      storage_disks:
        - size_gigabytes: 3
        - size_gigabytes: 5
    register: machine

  - debug:
      var: machine
"""

RETURN = r"""
record:
  description:
    - Created virtual machine on a specified host.
  returned: success
  type: dict
  sample:
    cores: 2
    distro_series: focal
    hostname: new-machine
    hwe_kernel: ga-22.04
    id: 6h4fn6
    memory: 2048
    network_interfaces:
    - fabric: fabric-1
      id: 277
      ip_address: 10.10.10.190
      name: my-net
      subnet_cidr: 10.10.10.0/24
      vlan: untagged
    osystem: ubuntu
    pool: default
    power_type: lxd
    status: Commissioning
    storage_disks:
    - id: 288
      name: sda
      size_gigabytes: 3
    - id: 289
      name: sdb
      size_gigabytes: 5
    tags:
      - pod-console-logging
      - my-tag
    zone: default
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vmhost import VMHost
from ..module_utils.machine import Machine
from ..module_utils.utils import is_changed, required_one_of


def prepare_network_data(module):
    # This is a workaround since compose only supports one network interface.
    tmp = module.params["network_interfaces"]
    module.params["network_interfaces"] = []
    module.params["network_interfaces"].append(tmp)


def ensure_ready(module, client, vm_host_obj):
    before = None
    after = None
    if module.params["hostname"]:
        vm_obj = Machine.get_by_name_and_host(module, client)
        if vm_obj:
            return (
                is_changed(before, after),
                vm_obj.to_ansible(),
                dict(before=before, after=after),
            )
    machine_obj = Machine.from_ansible(module)
    payload = machine_obj.payload_for_compose(module)
    task = vm_host_obj.send_compose_request(module, client, payload)
    after = (Machine.get_by_id(task["system_id"], client)).to_ansible()
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
    vm_host_obj = VMHost.get_by_name(
        module, client, must_exist=True, name_field_ansible="vm_host"
    )
    if module.params["network_interfaces"]:
        prepare_network_data(module)
    changed, record, diff = ensure_ready(module, client, vm_host_obj)
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
            ),
            cores=dict(
                type="int",
                default=1,
            ),
            pinned_cores=dict(
                type="int",
            ),
            zone=dict(
                type="int",
            ),
            pool=dict(
                type="int",
            ),
            domain=dict(
                type="int",
            ),
            memory=dict(
                type="int",
                default=2048,
            ),
            network_interfaces=dict(
                type="dict",
                options=dict(
                    label_name=dict(
                        type="str",
                        required=True,
                    ),
                    name=dict(
                        type="str",
                    ),
                    subnet_cidr=dict(
                        type="str",
                    ),
                    fabric=dict(
                        type="str",
                    ),
                    vlan=dict(
                        type="str",
                    ),
                    ip_address=dict(
                        type="str",
                    ),
                ),
            ),
            storage_disks=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    size_gigabytes=dict(
                        type="int",
                        required=True,
                    ),
                ),
            ),
        ),
        mutually_exclusive=[("cores", "pinned_cores")],
    )

    try:
        required_one_of(
            module,
            option="network_interfaces",
            list_suboptions=["name", "subnet_cidr", "fabric", "vlan", "ip_address"],
        )

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
