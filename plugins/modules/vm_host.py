#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_host

author:
  - Polona Mihalič (@PolonaM)
short_description: Create, update and delete VM host of allowed type (LXD and virsh).
description:
  - If I(state) value is C(absent) the selected VM host will be deleted.
  - If I(state) value is C(present), and I(machine) is provided, new VM host with the name I(vm_host_name) will be created from the machine.
  - If I(state) value is C(present), and I(vm_host_name) is found, an existing VM host will be updated.
  - If I(state) value is C(present), and I(vm_host_name) is not found, new VM host with the name I(vm_host_name) will be created.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the VM host.
    choices: [ absent, present ]
    type: str
    required: True
  vm_host_name:
    description:
      - The name of an VM host to be created, updated or deleted.
      - If I(state) value is C(absent), existing VM host will be deleted.
      - If I(state) value is C(present), and I(vm_host_name) is not provided or not found, a new VM host will be created.
      - If I(state) value is C(present), and I(vm_host_name) is found, an existing VM host will be updated.
      - This is computed if it's not set.
    required: True
    type: str
  machine:
    description:
      - The name of registered ready MAAS machine to be deployed and registered as a LXD VM host in MAAS.
      - Relevant only if I(state) value is C(present).
      - This option conflicts with I(power_parameters).
      - If machine is not found the task will FAIL.
    type: str
  power_parameters:
    description:
      - Power parameters used for creating new VM host or updating existing VM host.
      - If creating new VM host required parameters are I(type) and I(power_address).
        If I(type) value is C(virsh) the parameters I(power_user) and I(power_pass) are also required. # CHECK IF THIS IS REALLY TRUE
    type: dict
    suboptions:
      power_type:
        description:
          - The new VM host type.
          - This option conflicts with I(hostname).
          - This option is used only when creating new VM host. To change the type, the VM host must be deleted and re-added.
        choices: [ lxd, virsh ]
        type: str
      power_address:
        description:
          - Address that gives MAAS access to the VM host power control.
            For example, for C(virsh) "qemu+ssh://172.16.99.2/system", for C(lxd), this is just the address of the host.
          - The address given here must be reachable by the MAAS server.
        type: str
      power_user:
        description:
          - User name to use for power control of the VM host.
          - Required for C(virsh) VM hosts that do not have SSH set up for public-key authentication.
          - This option is used only when creating new VM host.
        type: str
      power_pass:
        description:
          - User password to use for power control of the VM host.
          - Required for C(virsh) VM hosts that do not have SSH set up for public-key authentication and for C(lxd)
            if the MAAS certificate is not registered already in the LXD server.
        type: str
  new_vm_host_name:
    description:
      - Update VM host name.
    type: str
  zone:
    description:
      - The new VM host zone name.
      - This is computed if it's not set.
    type: str
  pool:
    description:
      - The new VM host zone name.
      - This is computed if it's not set.
    type: str
  tags:
    description:
      - A tag or list of tags (comma delimited) to assign to the new VM host.
      - This is computed if it's not set.
    type: list  # CHECK IF THIS IS TRUE
    elements: str
  cpu_over_commit_ratio:
    description:
      - The new VM host CPU overcommit ratio (0-10).
      - This is computed if it's not set.
    type: int
  memory_over_commit_ratio:
    description:
      - The new VM host RAM memory overcommit ratio (0-10).
      - This is computed if it's not set.
    type: int
  default_macvlan_mode:
    description:
      - Default macvlan mode for VM hosts that use it.
      - This is computed if it's not set.
    choices: [ bridge, passthru, private, vepa ]
    type: str
"""


EXAMPLES = r"""
name: Register LXD VM host
canonical.maas.vm_host:
  state: present
  vm_host_name: new-lxd
  power_parameters:
    power_type: lxd
    power_address: 172.16.117.70:8443
  cpu_over_commit_ratio: 1
  memory_over_commit_ratio: 2
  default_macvlan_mode: bridge
  zone: my-zone
  pool: my-pool
  tags:
    - pod-console-logging
    - my-tag

name: Register VIRSH host
canonical.maas.vm_host:
  state: present
  vm_host_name: new-virsh
  power_parameters:
    power_type: virsh
    power_address: qemu+ssh://172.16.99.2/system
    power_user: user
    power_pass: pass
  cpu_over_commit_ratio: 1
  memory_over_commit_ratio: 2
  default_macvlan_mode: bridge
  zone: my-zone
  pool: my-pool
  tags:
    - pod-console-logging
    - my-tag

name: Register known allready allocated machine
canonical.maas.vm_host:
  state: present
  vm_host_name: new-vm-host-name
  machine: my_machine
  cpu_over_commit_ratio: 1
  memory_over_commit_ratio: 2
  default_macvlan_mode: bridge

name: Update VM host
canonical.maas.vm_host:
  state: present
  vm_host_name: my-virsh
  power_parameters:
    power_address: qemu+ssh://172.16.99.2/system
    power_pass: pass_updated
  new_vm_host_name: my-virsh-updated
  cpu_over_commit_ratio: 2
  memory_over_commit_ratio: 3
  default_macvlan_mode: bridge
  zone: new-zone
  pool: new-pool
  tags:
    - new-tag

name: Remove VM host
canonical.maas.vm_host:
  state: absent
  vm_host_name: sunny-raptor
"""

RETURN = r"""
record:
  description:
    - Created VM host.
  returned: success
  type: dict
  sample:
    - architectures:
      - amd64/generic
      available:
        cores: 1
        local_storage: 6884062720
        memory: 4144
      capabilities:
      - composable
      - dynamic_local_storage
      - over_commit
      - storage_pools
      cpu_over_commit_ratio: 1.0
      default_macvlan_mode: null
      host:
        __incomplete__: true
        system_id: d6car8
      id: 1
      memory_over_commit_ratio: 1.0
      name: sunny-raptor
      pool:
        description: Default pool
        id: 0
        name: default
        resource_uri: /MAAS/api/2.0/resourcepool/0/
      resource_uri: /MAAS/api/2.0/vm-hosts/1/
      storage_pools:
      - available: 6884062720
        default: true
        id: default
        name: default
        path: /var/snap/lxd/common/lxd/disks/default.img
        total: 22884062720
        type: zfs
        used: 16000000000
      tags:
      - pod-console-logging
      total:
        cores: 4
        local_storage: 22884062720
        memory: 8192
      type: lxd
      used:
        cores: 3
        local_storage: 16000000000
        memory: 4048
      version: '5.5'
      zone:
        description: ''
        id: 1
        name: default
        resource_uri: /MAAS/api/2.0/zones/default/
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine
from ..module_utils.vmhost import VMHost


def deploy_machine_as_vm_host(module, client):
    machine = Machine.get_by_name(
        module, client, must_exist=True, name_field_ansible="machine"
    )  # Replace with get_by_name_and_vm_host??
    data = {
        "install_rackd": True,  # If true, the rack controller will be installed on this machine.
        "install_kwm": True,  # If true, KVM will be installed on this machine and added to MAAS.
        "register_vmhost": True,  # TEST THE COMBINATION OF PARAMETERS
    }
    timeout = 30  # [s]
    machine.deploy(client, data, timeout)
    Machine.wait_for_state(
        machine.id, client, False, "Deployed"
    )  # Check if we wait for deployed state
    vm_host = VMHost.get_by_name(
        module, client, must_exist=True, name_field_ansible="vm_host_name"
    )
    return (
        True,
        vm_host,
        dict(before={}, after=vm_host),
    )


def create_vm_host(module, client: Client):
    data = {}
    data["type"] = module.params["power_parameters"]["power_type"]
    data["power_address"] = module.params["power_parameters"]["power_address"]
    if module.params["power_parameters"]["power_user"]:
        data["power_user"] = module.params["power_parameters"]["power_user"]
    if module.params["power_parameters"]["power_pass"]:
        data["power_pass"] = module.params["power_parameters"]["power_pass"]
    # CHECK IF FOR LOOP IS REALLY NOT NEEDED HERE
    if module.params["tags"]:
        data["tags"] = module.params["tags"]
    if module.params["zone"]:
        data["zone"] = module.params["zone"]
    if module.params["pool"]:
        data["pool"] = module.params["pool"]
    if module.params["vm_host_name"]:
        data["name"] = module.params["vm_host_name"]

    vm_host_obj, vm_host = VMHost.create(client, data)

    data = {}
    if module.params["cpu_over_commit_ratio"]:
        data["cpu_over_commit_ratio"] = module.params["cpu_over_commit_ratio"]
    if module.params["memory_over_commit_ratio"]:
        data["memory_over_commit_ratio"] = module.params["memory_over_commit_ratio"]
    if module.params["default_macvlan_mode"]:
        data["default_macvlan_mode"] = module.params["default_macvlan_mode"]
    if data:
        vm_host = vm_host_obj.update(data)

    return (
        True,
        vm_host,
        dict(before={}, after=vm_host),
    )


def update_vm_host(module, client: Client, vm_host_obj):
    data = {}
    if module.params["power_parameters"]["power_address"]:
        data["power_address"] = module.params["power_parameters"]["power_address"]
    if module.params["power_parameters"]["power_pass"]:
        data["power_pass"] = module.params["power_parameters"]["power_pass"]
    # CHECK IF FOR LOOP IS REALLY NOT NEEDED HERE
    if module.params["tags"]:
        if vm_host_obj.tags != module.params["tags"]:
            data["tags"] = module.params["tags"]
    if module.params["zone"]:
        if vm_host_obj.zone != module.params["zone"]:
            data["zone"] = module.params["zone"]
    if module.params["pool"]:
        if vm_host_obj.pool != module.params["pool"]:
            data["pool"] = module.params["pool"]
    if module.params["new_hostname"]:
        if vm_host_obj.name != module.params["new_vm_host_name"]:
            data["name"] = module.params["new_vm_host_name"]
    if module.params["cpu_over_commit_ratio"]:
        if vm_host_obj.cpu_over_commit_ratio != module.params["cpu_over_commit_ratio"]:
            data["cpu_over_commit_ratio"] = module.params["cpu_over_commit_ratio"]
    if module.params["memory_over_commit_ratio"]:
        if (
            vm_host_obj.memory_over_commit_ratio
            != module.params["memory_over_commit_ratio"]
        ):
            data["memory_over_commit_ratio"] = module.params["memory_over_commit_ratio"]
    if module.params["default_macvlan_mode"]:
        if vm_host_obj.default_macvlan_mode != module.params["default_macvlan_mode"]:
            data["default_macvlan_mode"] = module.params["default_macvlan_mode"]

    vm_host_before = vm_host_obj.get(client)

    if data:
        vm_host = vm_host_obj.update(client, data)
        return (
            True,
            vm_host,
            dict(before=vm_host_before, after=vm_host),
        )

    return (
        False,
        vm_host_before,
        dict(before=vm_host_before, after=vm_host_before),
    )


def delete_vm_host(module, client: Client):
    vm_host = VMHost.get_by_name(
        module, client, must_exist=False, name_field_ansible="vm_host_name"
    )
    if vm_host:
        vm_host.delete(client)
        return True, dict(), dict(before=vm_host.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        if module.params["machine"]:
            return deploy_machine_as_vm_host(module, client)
        else:
            if module.params["vm_host_name"]:
                vm_host_obj = VMHost.get_by_name(
                    module, client, must_exist=False, name_field_ansible="vm_host_name"
                )
                if vm_host_obj:
                    return update_vm_host(module, client, vm_host_obj)
            return create_vm_host(module, client)
    if module.params["state"] == "absent":
        return delete_vm_host(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            vm_host_name=dict(type="str", required=True),
            machine=dict(type="str"),
            state=dict(type="str", required=True, choices=["present", "absent"]),
            power_parameters=dict(
                type="dict",
                options=dict(
                    power_type=dict(type="str", choices=["lxd", "virsh"]),
                    power_address=dict(type="str"),
                    power_user=dict(type="str"),
                    power_pass=dict(type="str", no_log=True),
                ),
            ),
            cpu_over_commit_ratio=dict(type="int"),
            memory_over_commit_ratio=dict(type="int"),
            default_macvlan_mode=dict(
                type="str", choices=["bridge", "passthru", "private", "vepa"]
            ),
            new_vm_host_name=dict(type="str"),
            pool=dict(type="str"),
            zone=dict(type="str"),
            tags=dict(type="list", elements="str"),
        ),
    )

    try:
        cluster_instance = module.params["cluster_instance"]
        host = cluster_instance["host"]
        customer_key = cluster_instance["customer_key"]
        token_key = cluster_instance["token_key"]
        token_secret = cluster_instance["token_secret"]

        client = Client(host, token_key, token_secret, customer_key)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
