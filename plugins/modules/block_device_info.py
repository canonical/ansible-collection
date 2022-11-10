#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: block_device_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns info about MAAS machines' block devices.
description:
  - Plugin returns information about all block devices or specific block device if I(name) is provided.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  machine_fqdn:
    description:
      - Fully qualified domain name of the specific machine whose block devices will be listed.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
    required: true
  name:
    description:
      - Name of a block device.
      - Serves as unique identifier of the block device.
      - If block device is not found the task will FAIL.
    type: str
"""

EXAMPLES = r"""
- name: Get list of all block devices of a selected machine.
  canonical.maas.block_device_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine_fqdn: machine_name.project

- name: Get info about a specific block device of a selected machine.
  canonical.maas.block_device_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine_fqdn: machine_name.project
    name: newblockdevice
"""

RETURN = r"""
records:
  description:
    - Machine's block device info list.
  returned: success
  type: list
  sample:
  - available_size: 0
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
from ..module_utils.block_device import BlockDevice


def run(module, client: Client):
    machine = Machine.get_by_fqdn(
        module, client, must_exist=True, name_field_ansible="machine_fqdn"
    )
    if module.params["name"]:
        block_device = BlockDevice.get_by_name(
            module, client, machine.id, must_exist=True
        )
        response = [block_device.get(client)]
    else:
        response = client.get(f"/api/2.0/nodes/{machine.id}/blockdevices/").json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            machine_fqdn=dict(type="str", required=True),
            name=dict(type="str"),
        ),
    )

    try:
        cluster_instance = module.params["cluster_instance"]
        host = cluster_instance["host"]
        consumer_key = cluster_instance["customer_key"]
        token_key = cluster_instance["token_key"]
        token_secret = cluster_instance["token_secret"]

        client = Client(host, token_key, token_secret, consumer_key)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
