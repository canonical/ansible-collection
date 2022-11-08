# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.block_device import (
    BlockDevice,
)
from ansible_collections.canonical.maas.plugins.module_utils.client import Response
from ansible_collections.canonical.maas.plugins.module_utils import errors

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        block_device_maas_dict = dict(
            name="my-block-device",
            id=5014,
            system_id="sgt3546",
            model="model",
            serial="serial",
            id_path="/dev/tmp",
            block_size=512,
            size=1024,
            tags=["tag1", "tag2"],
        )
        block_device = BlockDevice(
            block_device_maas_dict["name"],
            block_device_maas_dict["id"],
            block_device_maas_dict["system_id"],
            block_device_maas_dict["model"],
            block_device_maas_dict["serial"],
            block_device_maas_dict["id_path"],
            block_device_maas_dict["block_size"],
            block_device_maas_dict["size"],
            block_device_maas_dict["tags"],
        )
        results = BlockDevice.from_maas(block_device_maas_dict)
        assert results == block_device


class TestGet:
    def test_get_by_id_200(self, client, mocker):
        id = 5
        machine_id = "machine-id"
        client.get.return_value = Response(
            200,
            '{"name":"my-block-device", "id":5, "system_id":"sgt3546", "model":"model", "serial":"serial", "id_path":"/dev/tmp",\
                "block_size":512, "size":1024, "tags":"tag1, tag2"}',  # HOW IS LIST PRESENTED IN RESPONSE???
        )
        block_device = BlockDevice(
            name="my-block-device",
            id=5014,
            machine_id="machine-id",
            model="model",
            serial="serial",
            id_path="/dev/tmp",
            block_size=512,
            size=1024,
            tags=["tag1", "tag2"],
        )
        results = BlockDevice.get_by_id(id, client, machine_id, must_exist=False)

        client.get.assert_called_with(
            "/api/2.0/nodes/machine-id/blockdevices/5/",
        )
        assert results == block_device

    def test_get_by_id_404(self, client, mocker):
        id = 5
        machine_id = "machine-id"
        client.get.return_value = Response(404, "{}")
        results = BlockDevice.get_by_id(id, client, machine_id, must_exist=False)

        client.get.assert_called_with(
            "/api/2.0/nodes/machine-id/blockdevices/5/",
        )
        assert results is None

    def test_get_by_vid_404_must_exist(self, client, mocker):
        id = 5
        machine_id = "machine-id"
        client.get.return_value = Response(404, "{}")

        with pytest.raises(errors.BlockDeviceNotFound) as exc:
            BlockDevice.get_by_id(id, client, machine_id, must_exist=True)

        assert "Block device - 5 - not found" in str(exc.value)

    def test_get_by_name(self, create_module, mocker, client):
        machine_id = "machine-id"
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                machine_fqdn="block-device-test.maas",
                name="my-block-device",
                state="present",
                id_path="/dev/vdb",
                size_gigabytes=27,
                tags=["ssd"],
                block_size=512,
                is_boot_device=True,  # where in return is this seen?
                partitions=dict(
                    size_gigabytes=10,
                    fs_type="ext4",
                    label="media",
                    mount_point="/media",
                    bootable=True,
                ),
                size_gigabytes=dict(
                    size_gigabytes=15,
                    fs_type="ext4",
                    mount_point="storage",
                    bootable=False,
                    tags="/dev/vdb",
                ),
            )
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = dict(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )

        assert BlockDevice.get_by_name(module, client, machine_id, True) == BlockDevice(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )
