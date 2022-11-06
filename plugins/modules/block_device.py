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
  - If I(state) is C(present) and I(name) is not found, creates new block device.
  - If I(state) is C(present) and I(name) is found, updates an existing block device.
  - If I(state) is C(absent) selected block device is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the block device.
    choices: [ present, absent ]
    type: str
    required: True
  machine_fqdn:
    description:
      - Fully qualified domain name of the machine that owns the block device.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
    required: True
  name:
    description:
      - The name of a block device to be created, updated or deleted.
    type: str
    required: True
  new_name:
    description:
      - Updated name of a selected block device.
    type: str
  size_gigabytes:
    description:
      - The size of the block device (in GB).
    type: int
    required: True
  block_size:
    description:
      - The block size of the block device. Defaults to 512.
    type: int
  is_boot_device:
    description:
      - Indicates if the block device is set as the boot device.
    type: bool
  partitions:
    description:
      - List of partition resources created for the new block device.
      - It is computed if it's not given.
    type: list #CHECK
    elements: dict #CHECK
    suboptions:
      size_gigabytes:
        description:
          - The partition size (in GB).
        type: int
        required: True
      bootable:
        description:
          - Indicates if the partition is set as bootable.
        type: bool
      tags:
        description:
          - The tags assigned to the new block device partition.
        type: str
      fs_type:
        description:
          - The file system type (e.g. ext4).
          - If this is not set, the partition is unformatted.
        type: str
      label:
        description:
          - The label assigned if the partition is formatted.
        type: str
      mount_point:
        description:
          - The mount point used.
          - If this is not set, the partition is not mounted.
          - This is used only the partition is formatted.
        type: str
      mount_options:
        description:
          - The options used for the partition mount.
        type: str
    model:
      description:
        - Model of the block device.
        - Required together with I(serial).
        - Mutually exclusive with I(id_path).
        - This argument is computed if it's not given.
      type: str
    serial:
      description:
        - Serial number of the block device.
        - Required together with with I(model).
        - Mutually exclusive with I(id_path).
        - This argument is computed if it's not given.
      type: str
    id_path:
      description:
        - Only used if I(model) and I(serial) cannot be provided.
        - This should be a path that is fixed and doesn't change depending on the boot order or kernel version.
        - This argument is computed if it's not given.
      type: path
    tags:
      description:
        - A set of tag names assigned to the new block device.
        - This argument is computed if it's not given.
      type: list # OR STR??
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
    - Created or updated machine's block device.
  returned: success
  type: dict
  sample:
  - firmware_version: null
    system_id: y7388k
    block_size: 102400
    available_size: 1000000000
    model: fakemodel
    serial: 123
    used_size: 0
    tags: []
    partition_table_type: null
    partitions: []
    path: /dev/disk/by-dname/newblockdevice
    size: 1000000000
    id_path: ""
    filesystem: null
    storage_pool: null
    name: newblockdevice
    used_for: Unused
    id: 73
    type: physical
    uuid: null
    resource_uri: /MAAS/api/2.0/nodes/y7388k/blockdevices/73/
"""


import json
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine


# POST /MAAS/api/2.0/nodes/{system_id}/blockdevices/:
# {system_id} (String): Required. The machine system_id.
# name (String): Required. Name of the block device.
# model (String): Optional. Model of the block device.
# serial (String): Optional. Serial number of the block device.
# id_path (String): Optional. Only used if model and serial cannot be provided. This should be a path that is fixed and doesn't change depending on the boot order or kernel version.
# size (String): Required. Size of the block device.
# block_size (String): Required. Block size of the block device.


# PUT /MAAS/api/2.0/nodes/{system_id}/blockdevices/{id}/
# {system_id} (String): Required. The machine system_id.
# {id} (String): Required. The block device's id.
# name (String): Optional. (Physical devices) Name of the block device.
# model (String): Optional. (Physical devices) Model of the block device.
# serial (String): Optional. (Physical devices) Serial number of the block device.
# id_path (String): Optional. (Physical devices) Only used if model and serial cannot be provided. This should be a path that is fixed and doesn't change depending on the boot order or kernel version.
# size (String): Optional. (Physical devices) Size of the block device.
# block_size (String): Optional. (Physical devices) Block size of the block device.
# name (String): Optional. (Virtual devices) Name of the block device.
# uuid (String): Optional. (Virtual devices) UUID of the block device.
# size (String): Optional. (Virtual devices) Size of the block device. (Only allowed for logical volumes.)


# POST /MAAS/api/2.0/nodes/{system_id}/blockdevices/{id}/?op=set_boot_disk
# Set a block device as the boot disk for the machine.


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
