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
    type: list
    elements: dict
    suboptions:
      size_gigabytes:
        description:
          - The partition size (in GB).
          - If not specified, all available space will be used.
        type: int
      bootable:
        description:
          - Indicates if the partition is set as bootable.
        type: bool
      tags:
        description:
          - The tags assigned to the new block device partition.
        type: list
        elements: str
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
          - This is used only if the partition is formatted.
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
      - Required together with I(model).
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
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Create and attach block device to machine
  canonical.maas.block_device:
    machine_fqdn: some_machine_name.project
    name: vdb
    state: present
    id_path: /dev/vdb
    size_gigabytes: 27
    tags:
      - ssd
    block_size: 512
    is_boot_device: false
    partitions:
      - size_gigabytes: 10
        fs_type: ext4
        label: media
        mount_point: /media
      - size_gigabytes: 15
        fs_type: ext4
        mount_point: /storage
        bootable: false
        tags: my_partition

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
    available_size: 0
    block_size: 512
    filesystem: null
    firmware_version: 2.5
    id: 146
    id_path: /dev/disk/by-id/scsi-SQEMU_QEMU_HARDDISK_lxd_root
    model: QEMU HARDDISK
    name: sda
    numa_node: 0
    partition_table_type: GPT
    partitions:
    - bootable: true
      device_id: 146
      filesystem:
        fstype: fat32
        label: efi
        mount_options: null
        mount_point: /boot/efi
        uuid: 42901672-60cb-44a3-bb8d-14f3314869c2
      id: 83
      path: /dev/disk/by-dname/sda-part1
      resource_uri: /MAAS/api/2.0/nodes/grydgf/blockdevices/146/partition/83
      size: 536870912
      system_id: grydgf
      tags: []
      type: partition
      used_for: fat32 formatted filesystem mounted at /boot/efi
      uuid: 6f3259e0-7aba-442b-9c31-5b6bafb4796a
    - bootable: false
      device_id: 146
      filesystem:
        fstype: ext4
        label: root
        mount_options: null
        mount_point: /
        uuid: f74d9bc7-a2f1-4078-991c-68696794ee27
      id: 84
      path: /dev/disk/by-dname/sda-part2
      resource_uri: /MAAS/api/2.0/nodes/grydgf/blockdevices/146/partition/84
      size: 7457472512
      system_id: grydgf
      tags: []
      type: partition
      used_for: ext4 formatted filesystem mounted at /
      uuid: eeba59a0-be8a-4be3-be15-e2858afa8487
    path: /dev/disk/by-dname/sda
    resource_uri: /MAAS/api/2.0/nodes/grydgf/blockdevices/146/
    serial: lxd_root
    size: 8000004096
    storage_pool: default
    system_id: grydgf
    tags:
      rotary
      1rpm
    type: physical
    used_for: GPT partitioned with 2 partitions
    used_size: 7999586304
    uuid: null
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine
from ..module_utils.partition import Partition
from ..module_utils.block_device import BlockDevice


def create_partitions(module, client, block_device):
    if module.params["partitions"]:
        for partition in module.params["partitions"]:
            data = {}
            if partition["size_gigabytes"]:
                data["size"] = partition["size_gigabytes"] * 1024 * 1024 * 1024
            if partition["bootable"]:
                data["bootable"] = partition["bootable"]
            new_partition = Partition.create(client, block_device, data)
            if partition["fs_type"]:
                data = {}
                data["fstype"] = partition["fs_type"]
                if partition["label"]:
                    data["label"] = partition["label"]
                new_partition.format(client, data)
                if partition[
                    "mount_point"
                ]:  # This is used only if the partition is formatted
                    data = {}
                    data["mount_point"] = partition["mount_point"]
                    if partition["mount_options"]:
                        data["mount_options"] = partition["mount_options"]
                    new_partition.mount(client, data)
            if partition["tags"]:
                for tag in partition["tags"]:
                    new_partition.add_tag(client, tag)


def create_tags(module, client, block_device):
    if module.params["tags"]:
        for tag in module.params["tags"]:
            block_device.add_tag(client, tag)


def set_boot_disk(module, client, block_device):
    if module.params["is_boot_device"]:
        block_device.set_boot_disk(client)


def data_for_create_block_device(module):
    data = {}
    data["name"] = module.params["name"]  # required
    data["size"] = module.params["size_gigabytes"] * 1024 * 1024 * 1024  # required
    data["block_size"] = 512  # default
    if module.params["block_size"]:
        data["block_size"] = module.params["block_size"]
    if module.params["model"]:
        data["model"] = module.params["model"]
    if module.params["serial"]:
        data["serial"] = module.params["serial"]
    if module.params["id_path"]:
        data["id_path"] = module.params["id_path"]
    return data


def create_block_device(module, client: Client, machine_id):
    data = data_for_create_block_device(module)
    block_device = BlockDevice.create(client, machine_id, data)
    create_partitions(module, client, block_device)
    create_tags(module, client, block_device)
    set_boot_disk(module, client, block_device)
    block_device_maas_dict = block_device.get(client)
    return (
        True,
        block_device_maas_dict,
        dict(before={}, after=block_device_maas_dict),
    )


def must_update_partitions(module, block_device):
    n = 0
    if len(module.params["partitions"]) != len(block_device.partitions):
        return True
    for partition in module.params["partitions"]:
        if (
            block_device.partitions[n].size
            != partition["size_gigabytes"] * 1024 * 1024 * 1024
        ):
            return True
        if block_device.partitions[n].bootable != partition["bootable"]:
            return True
        if block_device.partitions[n].tags != partition["tags"]:
            return True
        if block_device.partitions[n].fstype != partition["fs_type"]:
            return True
        if block_device.partitions[n].label != partition["label"]:
            return True
        if block_device.partitions[n].mount_point != partition["mount_point"]:
            return True
        if block_device.partitions[n].mount_options != partition["mount_options"]:
            return True
        n += 1


def delete_partitions(client, block_device):
    if block_device.partitions:  # if partitions exist, delete them
        for partition in block_device.partitions:
            client.delete(
                f"/api/2.0/nodes/{block_device.machine_id}/blockdevices/{block_device.id}/partition/{partition.id}"
            )


def update_partitions(module, client, block_device):
    if module.params["partitions"]:
        if must_update_partitions(module, block_device):
            delete_partitions(client, block_device)
            create_partitions(module, client, block_device)


def delete_tags(client, block_device):
    if block_device.tags:
        for tag in block_device.tags:
            block_device.remove_tag(client, tag)


def update_tags(module, client, block_device):
    if module.params["tags"]:
        if module.params["tags"] != block_device.tags:
            delete_tags(client, block_device)
            for tag in module.params["tags"]:
                block_device.add_tag(client, tag)


def data_for_update_block_device(module, block_device):
    data = {}
    if module.params["new_name"]:
        if block_device.name != module.params["new_name"]:
            data["name"] = module.params["new_name"]
    if module.params["model"]:
        if block_device.model != module.params["model"]:
            data["model"] = module.params["model"]
    if module.params["serial"]:
        if block_device.serial != module.params["serial"]:
            data["serial"] = module.params["serial"]
    if module.params["id_path"]:
        if block_device.id_path != module.params["id_path"]:
            data["id_path"] = module.params["id_path"]
    if module.params["block_size"]:
        if block_device.block_size != module.params["block_size"]:
            data["block_size"] = module.params["block_size"]
    if module.params["size_gigabytes"]:
        if block_device.size != module.params["size_gigabytes"] * 1024 * 1024 * 1024:
            data["size"] = module.params["size_gigabytes"] * 1024 * 1024 * 1024
    return data


def update_block_device(module, client: Client, block_device):
    block_device_maas_dict = block_device.get(client)
    data = data_for_update_block_device(module, block_device)
    if data:
        block_device.update(client, data)
    update_tags(module, client, block_device)
    set_boot_disk(module, client, block_device)  # we don't get this in return
    update_partitions(module, client, block_device)
    updated_block_device_maas_dict = block_device.get(client)
    if updated_block_device_maas_dict == block_device_maas_dict:
        return (
            False,
            block_device_maas_dict,
            dict(before=block_device_maas_dict, after=block_device_maas_dict),
        )
    return (
        True,
        updated_block_device_maas_dict,
        dict(before=block_device_maas_dict, after=updated_block_device_maas_dict),
    )


def delete_block_device(client: Client, block_device):
    if block_device:
        block_device_maas_dict = block_device.get(client)
        block_device.delete(client)
        return True, dict(), dict(before=block_device_maas_dict, after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    machine = Machine.get_by_fqdn(
        module, client, must_exist=True, name_field_ansible="machine_fqdn"
    )
    block_device = BlockDevice.get_by_name(module, client, machine.id)
    if module.params["state"] == "present":
        if block_device:
            return update_block_device(module, client, block_device)
        else:
            return create_block_device(module, client, machine.id)
    if module.params["state"] == "absent":
        return delete_block_device(client, block_device)


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
            machine_fqdn=dict(type="str", required=True),
            name=dict(type="str", required=True),
            new_name=dict(type="str"),
            block_size=dict(type="int"),
            size_gigabytes=dict(type="int"),
            is_boot_device=dict(type="bool"),
            model=dict(type="str"),
            serial=dict(type="str"),
            id_path=dict(type="path"),
            tags=dict(type="list", elements="str"),
            partitions=dict(
                type="list",
                elements="dict",
                options=dict(
                    size_gigabytes=dict(type="int"),
                    bootable=dict(type="bool"),
                    tags=dict(type="list", elements="str"),
                    fs_type=dict(type="str"),
                    label=dict(type="str"),
                    mount_point=dict(type="str"),
                    mount_options=dict(type="str"),
                ),
            ),
        ),
        required_together=[("model", "serial")],
        mutually_exclusive=[("model", "id_path"), ("serial", "id_path")],
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
