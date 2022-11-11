#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: machine_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: Return info about virtual machines.
description:
  - Plugin returns information about all virtual machines or specific virtual machine in a cluster.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  fqdn:
    description:
      - Fully qualified domain name of the specific machine to be listed.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
"""

EXAMPLES = r"""
- name: Get list of all machines
  canonical.maas.machine_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key

- name: Get info about a specific machine
  canonical.maas.machine_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    fqdn: solid-fish
"""

RETURN = r"""
records:
  description:
    - Machine info list.
  returned: success
  type: list
  sample:
    - address_ttl: null
      architecture: amd64/generic
      bcaches: []
      bios_boot_method: uefi
      blockdevice_set:
      - available_size: 0
        block_size: 512
        filesystem: null
        firmware_version: 2.5+
        id: 136
        id_path: /dev/disk/by-id/scsi-SQEMU_QEMU_HARDDISK_lxd_root
        model: QEMU HARDDISK
        name: sda
        numa_node: 0
        partition_table_type: GPT
        partitions:
        - bootable: true
          device_id: 136
          filesystem:
            fstype: fat32
            label: efi
            mount_options: null
            mount_point: /boot/efi
            uuid: b20d4817-e14f-45dd-ab0c-247435b32086
          id: 117
          path: /dev/disk/by-dname/sda-part1
          resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/partition/117
          size: 536870912
          system_id: wswynq
          tags: []
          type: partition
          used_for: fat32 formatted filesystem mounted at /boot/efi
          uuid: 607adea3-43e8-4ef3-8883-421cb5cbae1f
        - bootable: false
          device_id: 136
          filesystem:
            fstype: ext4
            label: root
            mount_options: null
            mount_point: /
            uuid: 2e8328d7-2c3c-40f1-9004-5c12ceb4288e
          id: 118
          path: /dev/disk/by-dname/sda-part2
          resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/partition/118
          size: 7457472512
          system_id: wswynq
          tags: []
          type: partition
          used_for: ext4 formatted filesystem mounted at /
          uuid: 9489f89c-556e-4a58-b9de-81d208f1009a
        path: /dev/disk/by-dname/sda
        resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/
        serial: lxd_root
        size: 8000004096
        storage_pool: default
        system_id: wswynq
        tags:
        - rotary
        - 1rpm
        type: physical
        used_for: GPT partitioned with 2 partitions
        used_size: 7999586304
        uuid: null
      boot_disk:
        available_size: 0
        block_size: 512
        filesystem: null
        firmware_version: 2.5+
        id: 136
        id_path: /dev/disk/by-id/scsi-SQEMU_QEMU_HARDDISK_lxd_root
        model: QEMU HARDDISK
        name: sda
        numa_node: 0
        partition_table_type: GPT
        partitions:
        - bootable: true
          device_id: 136
          filesystem:
            fstype: fat32
            label: efi
            mount_options: null
            mount_point: /boot/efi
            uuid: b20d4817-e14f-45dd-ab0c-247435b32086
          id: 117
          path: /dev/disk/by-dname/sda-part1
          resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/partition/117
          size: 536870912
          system_id: wswynq
          tags: []
          type: partition
          used_for: fat32 formatted filesystem mounted at /boot/efi
          uuid: 607adea3-43e8-4ef3-8883-421cb5cbae1f
        - bootable: false
          device_id: 136
          filesystem:
            fstype: ext4
            label: root
            mount_options: null
            mount_point: /
            uuid: 2e8328d7-2c3c-40f1-9004-5c12ceb4288e
          id: 118
          path: /dev/disk/by-dname/sda-part2
          resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/partition/118
          size: 7457472512
          system_id: wswynq
          tags: []
          type: partition
          used_for: ext4 formatted filesystem mounted at /
          uuid: 9489f89c-556e-4a58-b9de-81d208f1009a
        path: /dev/disk/by-dname/sda
        resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/
        serial: lxd_root
        size: 8000004096
        storage_pool: default
        system_id: wswynq
        tags:
        - rotary
        - 1rpm
        type: physical
        used_for: GPT partitioned with 2 partitions
        used_size: 7999586304
        uuid: null
      boot_interface:
        children:
        - br-enp5s0
        discovered: []
        effective_mtu: 1500
        enabled: true
        firmware_version: null
        id: 160
        interface_speed: 0
        link_connected: true
        link_speed: 0
        links: []
        mac_address: 00:16:3e:f6:de:1b
        name: enp5s0
        numa_node: 0
        params: ''
        parents: []
        product: null
        resource_uri: /MAAS/api/2.0/nodes/wswynq/interfaces/160/
        sriov_max_vf: 0
        system_id: wswynq
        tags: []
        type: physical
        vendor: Red Hat, Inc.
        vlan:
          dhcp_on: true
          external_dhcp: null
          fabric: fabric-1
          fabric_id: 1
          id: 5002
          mtu: 1500
          name: untagged
          primary_rack: d6car8
          relay_vlan: null
          resource_uri: /MAAS/api/2.0/vlans/5002/
          secondary_rack: null
          space: undefined
          vid: 0
      cache_sets: []
      commissioning_status: 2
      commissioning_status_name: Passed
      cpu_count: 1
      cpu_speed: 1100
      cpu_test_status: -1
      cpu_test_status_name: Unknown
      current_commissioning_result_id: 253
      current_installation_result_id: 256
      current_testing_result_id: 254
      default_gateways:
        ipv4:
          gateway_ip: 10.10.10.1
          link_id: null
        ipv6:
          gateway_ip: null
          link_id: null
      description: ''
      disable_ipv4: false
      distro_series: focal
      domain:
        authoritative: true
        id: 0
        is_default: true
        name: maas
        resource_record_count: 302
        resource_uri: /MAAS/api/2.0/domains/0/
        ttl: null
      fqdn: new-weasel.maas
      hardware_info:
        chassis_serial: Unknown
        chassis_type: Other
        chassis_vendor: QEMU
        chassis_version: pc-q35-7.1
        cpu_model: Intel(R) Core(TM) i7-10710U CPU
        mainboard_firmware_date: 02/06/2015
        mainboard_firmware_vendor: EFI Development Kit II / OVMF
        mainboard_firmware_version: 0.0.0
        mainboard_product: LXD
        mainboard_serial: Unknown
        mainboard_vendor: Canonical Ltd.
        mainboard_version: pc-q35-7.1
        system_family: Unknown
        system_product: Standard PC (Q35 + ICH9, 2009)
        system_serial: Unknown
        system_sku: Unknown
        system_vendor: QEMU
        system_version: pc-q35-7.1
      hardware_uuid: 2449b1dd-aa0e-47db-8cbf-4023e49b341a
      hostname: new-weasel
      hwe_kernel: ga-20.04
      interface_set:
      - children:
        - br-enp5s0
        discovered: []
        effective_mtu: 1500
        enabled: true
        firmware_version: null
        id: 160
        interface_speed: 0
        link_connected: true
        link_speed: 0
        links: []
        mac_address: 00:16:3e:f6:de:1b
        name: enp5s0
        numa_node: 0
        params: ''
        parents: []
        product: null
        resource_uri: /MAAS/api/2.0/nodes/wswynq/interfaces/160/
        sriov_max_vf: 0
        system_id: wswynq
        tags: []
        type: physical
        vendor: Red Hat, Inc.
        vlan:
          dhcp_on: true
          external_dhcp: null
          fabric: fabric-1
          fabric_id: 1
          id: 5002
          mtu: 1500
          name: untagged
          primary_rack: d6car8
          relay_vlan: null
          resource_uri: /MAAS/api/2.0/vlans/5002/
          secondary_rack: null
          space: undefined
          vid: 0
      - children: []
        discovered: null
        effective_mtu: 1500
        enabled: true
        firmware_version: null
        id: 162
        interface_speed: 0
        link_connected: true
        link_speed: 0
        links:
        - id: 505
          ip_address: 10.10.10.3
          mode: auto
          subnet:
            active_discovery: true
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
              primary_rack: d6car8
              relay_vlan: null
              resource_uri: /MAAS/api/2.0/vlans/5002/
              secondary_rack: null
              space: undefined
              vid: 0
        mac_address: 00:16:3e:f6:de:1b
        name: br-enp5s0
        numa_node: null
        params:
          bridge_fd: 15
          bridge_stp: false
          bridge_type: standard
        parents:
        - enp5s0
        product: null
        resource_uri: /MAAS/api/2.0/nodes/wswynq/interfaces/162/
        sriov_max_vf: 0
        system_id: wswynq
        tags: []
        type: bridge
        vendor: null
        vlan:
          dhcp_on: true
          external_dhcp: null
          fabric: fabric-1
          fabric_id: 1
          id: 5002
          mtu: 1500
          name: untagged
          primary_rack: d6car8
          relay_vlan: null
          resource_uri: /MAAS/api/2.0/vlans/5002/
          secondary_rack: null
          space: undefined
          vid: 0
      interface_test_status: -1
      interface_test_status_name: Unknown
      ip_addresses:
      - 10.10.10.3
      last_sync: null
      locked: false
      memory: 2048
      memory_test_status: -1
      memory_test_status_name: Unknown
      min_hwe_kernel: ''
      netboot: true
      network_test_status: -1
      network_test_status_name: Unknown
      next_sync: null
      node_type: 0
      node_type_name: Machine
      numanode_set:
      - cores:
        - 0
        hugepages_set: []
        index: 0
        memory: 2048
      osystem: ubuntu
      other_test_status: -1
      other_test_status_name: Unknown
      owner: admin
      owner_data: {}
      physicalblockdevice_set:
      - available_size: 0
        block_size: 512
        filesystem: null
        firmware_version: 2.5+
        id: 136
        id_path: /dev/disk/by-id/scsi-SQEMU_QEMU_HARDDISK_lxd_root
        model: QEMU HARDDISK
        name: sda
        numa_node: 0
        partition_table_type: GPT
        partitions:
        - bootable: true
          device_id: 136
          filesystem:
            fstype: fat32
            label: efi
            mount_options: null
            mount_point: /boot/efi
            uuid: b20d4817-e14f-45dd-ab0c-247435b32086
          id: 117
          path: /dev/disk/by-dname/sda-part1
          resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/partition/117
          size: 536870912
          system_id: wswynq
          tags: []
          type: partition
          used_for: fat32 formatted filesystem mounted at /boot/efi
          uuid: 607adea3-43e8-4ef3-8883-421cb5cbae1f
        - bootable: false
          device_id: 136
          filesystem:
            fstype: ext4
            label: root
            mount_options: null
            mount_point: /
            uuid: 2e8328d7-2c3c-40f1-9004-5c12ceb4288e
          id: 118
          path: /dev/disk/by-dname/sda-part2
          resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/partition/118
          size: 7457472512
          system_id: wswynq
          tags: []
          type: partition
          used_for: ext4 formatted filesystem mounted at /
          uuid: 9489f89c-556e-4a58-b9de-81d208f1009a
        path: /dev/disk/by-dname/sda
        resource_uri: /MAAS/api/2.0/nodes/wswynq/blockdevices/136/
        serial: lxd_root
        size: 8000004096
        storage_pool: default
        system_id: wswynq
        tags:
        - rotary
        - 1rpm
        type: physical
        used_for: GPT partitioned with 2 partitions
        used_size: 7999586304
        uuid: null
      pod:
        id: 1
        name: sunny-raptor
        resource_uri: /MAAS/api/2.0/pods/1/
      pool:
        description: Default pool
        id: 0
        name: default
        resource_uri: /MAAS/api/2.0/resourcepool/0/
      power_state: 'on'
      power_type: lxd
      raids: []
      resource_uri: /MAAS/api/2.0/machines/wswynq/
      special_filesystems: []
      status: 11
      status_action: mark_failed
      status_message: Marking node failed - Node operation 'Deploying' timed out after 240 minutes.
      status_name: Failed deployment
      storage: 8000.004096
      storage_test_status: 2
      storage_test_status_name: Passed
      swap_size: null
      sync_interval: null
      system_id: wswynq
      tag_names:
      - virtual
      - pod-console-logging
      testing_status: 2
      testing_status_name: Passed
      virtualblockdevice_set: []
      virtualmachine_id: 96
      volume_groups: []
      workload_annotations: {}
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
from ..module_utils.cluster_instance import get_oauth1_client


def run(module, client: Client):
    if module.params["fqdn"]:
        machine = Machine.get_by_fqdn(module, client, must_exist=True)
        response = [client.get(f"/api/2.0/machines/{machine.id}/").json]
    else:
        response = client.get("/api/2.0/machines/").json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            fqdn=dict(type="str"),
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
