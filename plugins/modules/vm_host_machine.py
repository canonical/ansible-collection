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
short_description: Return info about vm hosts.
description:
  - Create VM on a specified host.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.instance
seealso: []
options:
  vm_host:
    description:
      - Name of the host.
    type: str
    required: True
  cores:
    description:
      - Number of CPUs.
    type: int
  memory:
    description:
      - Physical memory.
    type: int
  storage_disks:
    description:
      - Storage disks.
    type: list
    elements: dict
    suboptions:
      size_gigabytes:
        type: int
        description:
          - Disk size in gigabytes.
  network_interfaces:
    description:
      - Network interface.
    type: dict
    elements: dict
    suboptions:
      name:
        type: str
        description:
          - Used to identify.
      subnet_cidr:
        type: str
        description:
          - Subnet mask.
"""

EXAMPLES = r"""
- name: Create new machine
  hosts: localhost
  tasks:
  - name: Create new machine on sunny-raptor host
    canonical.maas.vm_host_machine:
      instance:
        host: 'some host address'
        token_key: 'token key'
        token_secret: 'token secret'
        client_key: 'client key'
      vm_host: sunny-raptor
      cores: 2
      memory: 2048
      network_interfaces:
        name: my_new
        subnet_cidr: "10.10.10.0/24"
      storage_disks:
        - size_gigabytes: 3
        - size_gigabytes: 5
    register: machines

  - debug:
      var: machines
"""

RETURN = r"""
records:
  description:
    - The created record of a machine.
  returned: success
  type: list
  sample:
    - id: machine-id
      name: 'this-machine'
      memory: 2046
      cores: 2
      network_interfaces:
        - name: 'this-interface'
          subnet_cidr: 10.0.0.0/24
      storage:
        - size_gigabytes: 5
        - size_gigabytes: 10
      
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.state import HostState
from ..module_utils.client import Client
from ..module_utils.vmhost import VMHost
from ..module_utils.machine import Machine
from ..module_utils.utils import is_changed


def prepare_network_data(module):
    # This is a workaround since compose only supports one network interface.
    tmp = module.params["network_interfaces"]
    module.params["network_interfaces"] = []
    module.params["network_interfaces"].append(tmp)


def ensure_ready(module, client, vm_host_obj):
    before = []
    after = []
    machine_obj = Machine.from_ansible(module)
    payload = machine_obj.payload_for_compose(module)
    task = vm_host_obj.send_compose_request(module, client, payload)
    after.append(
        (Machine.get_by_id(task["system_id"], client, must_exist=True)).to_ansible()
    )
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
    vm_host_obj = VMHost.get_by_name(
        module, client, must_exist=True, name_field_ansible="vm_host"
    )
    if module.params["network_interfaces"]:
        prepare_network_data(module)
    changed, records, diff = ensure_ready(module, client, vm_host_obj)
    return changed, records, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("instance"),
            vm_host=dict(
                type="str",
                required=True,
            ),
            cores=dict(
                type="int",
            ),
            memory=dict(
                type="int",
            ),
            network_interfaces=dict(
                type="dict",
                options=dict(
                    name=dict(
                        type="str",
                        required=True,
                    ),
                    subnet_cidr=dict(
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
