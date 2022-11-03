#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: block_device

author:
  - Polona Mihalič (@PolonaM)
short_description: Creates, updates or deletes MAAS machines' block devices.
description:
  - If I(state) is C(present) and I(hostname) is not provided or not found, adds an existing machine to the system.
  - If I(state) is C(present) and I(hostname) is found, updates an existing machine in the system.
  - If I(state) is C(absent) selected machine is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the machine.
    choices: [ present, absent ]
    type: str
    required: True
  power_type:
    description:
      - A power management type (e.g. ipmi).
      - In case of adding new machine to the system, this parameters is required.
    type: str
    choices: [ "amt", "apc", "dli", "eaton", "hmc", "ipmi", "manual", "moonshot", "mscm", "msftocs", "nova",
              "openbmc", "proxmox", "recs_box", "redfish", "sm15k", "ucsm", "vmware", "webhook", "wedge", "lxd", "virsh" ]
  power_parameters:
    description:
      - A dictionary with the parameters specific to the power_type.
      - See U(https://maas.io/docs/api#power-types) section for a list of available power parameters for each power type.
      - In case of adding new machine to the system, this parameters is required.
    type: dict
  pxe_mac_address:
    description:
      - The MAC address of the machine's PXE boot NIC.
      - In case of adding new machine to the system, this parameters is required.
      - Relevant only in case of adding new machine.
    type: str
  architecture:
    description:
      - The architecture type of the machine (for example, "i386/generic" or "amd64/generic").
      - Defaults to amd64/generic.
    type: str
  fqdn:
    description:
      - Fully qualified domain name of the machine to be updated or deleted.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
  hostname:
    description:
      - Name of the machine to be added. In case of updating the machine, this parameter is used for updating the name of the machine.
      - In case if new machine is added, the name is computed if it's not set.
    type: str
  domain:
    description:
      - The domain of the machine.
      - This is computed if it's not set.
    type: str
  zone:
    description:
      - The zone of the machine.
      - This is computed if it's not set.
    type: str
  pool:
    description:
      - The resource pool of the machine.
      - This is computed if it's not set.
    type: str
  min_hwe_kernel:
    description:
      - The minimum kernel version allowed to run on this machine.
      - Only used when deploying Ubuntu.
      - This is computed if it's not set.
    type: str




    machine - (Required) The machine identifier (system ID, hostname, or FQDN) that owns the block device.
    name - (Required) The block device name.
    size_gigabytes - (Required) The size of the block device (given in GB).
    block_size - (Optional) The block size of the block device. Defaults to 512.
    is_boot_device - (Optional) Boolean value indicating if the block device is set as the boot device.
    partitions - (Optional) List of partition resources created for the new block device. Parameters defined below. This argument is processed in attribute-as-blocks mode. And, it is computed if it's not given.
    model - (Optional) Model of the block device. Used in conjunction with serial argument. Conflicts with id_path. This argument is computed if it's not given.
    serial - (Optional) Serial number of the block device. Used in conjunction with model argument. Conflicts with id_path. This argument is computed if it's not given.
    id_path - (Optional) Only used if model and serial cannot be provided. This should be a path that is fixed and doesn't change depending on the boot order or kernel version. This argument is computed if it's not given.
    tags - (Optional) A set of tag names assigned to the new block device. This argument is computed if it's not given.


POST /MAAS/api/2.0/nodes/{system_id}/blockdevices/:

{system_id} (String): Required. The machine system_id.

name (String): Required. Name of the block device.

model (String): Optional. Model of the block device.

serial (String): Optional. Serial number of the block device.

id_path (String): Optional. Only used if model and serial cannot be provided. This should be a path that is fixed and doesn't change depending on the boot order or kernel version.

size (String): Required. Size of the block device.

block_size (String): Required. Block size of the block device.








"""

EXAMPLES = r"""
- name: Create and attach block device to machine 
  canonical.maas.block_device:
    machine_fqdn: some_machine_name.project
    name: vdb
    state: present
    id_path: /dev/vdb
    size_gigabytes: 27
    tags: "ssd"
    block_size: 512
    is_boot_device: false
    partitions:
      - size_gigabytes: 10
        fs_type: "ext4"
        label: "media"
        mount_point: "/media"
      - size_gigabytes: 15
        fs_type: "ext4"
        mount_point: "/storage"
        bootable: false
        tags: my_partition
    model:
    serial:
    id_path:

- name: Delete block device
  canonical.maas.block_device:
    machine_fqdn: some_machine_name.project
    name: vdb
    state: absent
"""

RETURN = r"""
record:
  description:
    - Added machine.
  returned: success
  type: dict
  sample:
    architecture: amd64/generic
    cores: 2
    distro_series: focal
    fqdn: new-machine.maas
    hostname: new-machine
    hwe_kernel: hwe-22.04
    id: 6h4fn6
    memory: 2048
    min_hwe_kernel: ga-22.04
    network_interfaces:
    - fabric: fabric-1
      id: 277
      ip_address: 10.10.10.190
      mac_address: 00:00:00:00:00:01
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


import json
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine


def data_for_add_machine(module):
    data = {}
    if (
        not module.params["power_type"]
        or not module.params["power_parameters"]
        or not module.params["pxe_mac_address"]
    ):
        raise errors.MissingValueAnsible(
            "power_type, power_parameters or pxe_mac_address"
        )
    data["power_type"] = module.params["power_type"]  # required
    data["power_parameters"] = json.dumps(module.params["power_parameters"])  # required
    data["mac_addresses"] = module.params["pxe_mac_address"]  # required
    data["architecture"] = "amd64/generic"  # default
    if module.params["architecture"]:
        data["architecture"] = module.params["architecture"]
    if module.params["hostname"]:
        data["hostname"] = module.params["hostname"]
    if module.params["domain"]:
        data["domain"] = module.params["domain"]
    if module.params["zone"]:
        data["zone"] = module.params["zone"]
    if module.params["pool"]:
        data["pool"] = module.params["pool"]
    if module.params["min_hwe_kernel"]:
        data["min_hwe_kernel"] = module.params["min_hwe_kernel"]
    return data


def add_machine(module, client: Client):
    data = data_for_add_machine(module)
    machine = Machine.create(client, data)
    return (
        True,
        machine.to_ansible(),
        dict(before={}, after=machine.to_ansible()),
    )


def data_for_update_machine(module, machine):
    data = {}
    if module.params["power_type"]:
        if machine.power_type != module.params["power_type"]:
            data["power_type"] = module.params["power_type"]
    if module.params["power_parameters"]:
        # Here we will not check for changes because some parameteres aren't returned
        data["power_parameters"] = json.dumps(module.params["power_parameters"])
    # pxe_mac_address can't be updated
    if module.params["architecture"]:
        if machine.architecture != module.params["architecture"]:
            data["architecture"] = module.params["architecture"]
    if module.params["hostname"]:
        if machine.hostname != module.params["hostname"]:
            data["hostname"] = module.params["hostname"]
    if module.params["domain"]:
        if machine.domain != module.params["domain"]:
            data["domain"] = module.params["domain"]
    if module.params["zone"]:
        if machine.zone != module.params["zone"]:
            data["zone"] = module.params["zone"]
    if module.params["pool"]:
        if machine.pool != module.params["pool"]:
            data["pool"] = module.params["pool"]
    if module.params["min_hwe_kernel"]:
        if machine.min_hwe_kernel != module.params["min_hwe_kernel"]:
            data["min_hwe_kernel"] = module.params["min_hwe_kernel"]
    return data


def update_machine(module, client: Client):
    machine = Machine.get_by_fqdn(module, client, must_exist=True)
    data = data_for_update_machine(module, machine)
    if data:
        updated_machine_maas_dict = machine.update(client, data)
        machine_after = Machine.from_maas(updated_machine_maas_dict)
        return (
            True,
            machine_after.to_ansible(),
            dict(before=machine.to_ansible(), after=machine_after.to_ansible()),
        )
    return (
        False,
        machine.to_ansible(),
        dict(before=machine.to_ansible(), after=machine.to_ansible()),
    )


def delete_machine(module, client: Client):
    machine = Machine.get_by_fqdn(module, client, must_exist=False)
    if machine:
        machine.delete(client)
        return True, dict(), dict(before=machine.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        if module.params["fqdn"]:
            return update_machine(module, client)
        else:
            return add_machine(module, client)
    if module.params["state"] == "absent":
        return delete_machine(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            fqdn=dict(type="str"),
            power_type=dict(
                type="str",
                choices=[
                    "amt",
                    "apc",
                    "dli",
                    "eaton",
                    "hmc",
                    "ipmi",
                    "manual",
                    "moonshot",
                    "mscm",
                    "msftocs",
                    "nova",
                    "openbmc",
                    "proxmox",
                    "recs_box",
                    "redfish",
                    "sm15k",
                    "ucsm",
                    "vmware",
                    "webhook",
                    "wedge",
                    "lxd",
                    "virsh",
                ],
            ),
            power_parameters=dict(type="dict"),
            pxe_mac_address=dict(type="str"),
            hostname=dict(type="str"),
            domain=dict(type="str"),
            zone=dict(type="str"),
            pool=dict(type="str"),
            min_hwe_kernel=dict(type="str"),
            architecture=dict(type="str"),
        ),
        required_if=[
            ("state", "absent", ("fqdn",), False),
        ],
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
