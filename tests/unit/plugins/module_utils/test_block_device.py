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
    def test_get_by_id_200(self, client):
        id = 5
        machine_id = "machine-id"
        client.get.return_value = Response(
            200,
            '{"name":"my-block-device", "id":5, "system_id":"sgt3546", "model":"model", "serial":"serial", "id_path":"/dev/tmp",\
                "block_size":512, "size":4000000, "tags":["tag1", "tag2"]}',
        )
        block_device = BlockDevice(
            name="my-block-device",
            id=5,
            machine_id="sgt3546",
            model="model",
            serial="serial",
            id_path="/dev/tmp",
            block_size=512,
            size=4000000,
            tags=["tag1", "tag2"],
        )
        results = BlockDevice.get_by_id(id, client, machine_id, must_exist=False)

        client.get.assert_called_with(
            "/api/2.0/nodes/machine-id/blockdevices/5/",
        )
        assert results == block_device

    def test_get_by_id_404(self, client):
        id = 5
        machine_id = "machine-id"
        client.get.return_value = Response(404, "{}")
        results = BlockDevice.get_by_id(id, client, machine_id, must_exist=False)

        client.get.assert_called_with(
            "/api/2.0/nodes/machine-id/blockdevices/5/",
        )
        assert results is None

    def test_get_by_vid_404_must_exist(self, client):
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
                partitions=[
                    dict(
                        size_gigabytes=10,
                        fs_type="ext4",
                        label="media",
                        mount_point="/media",
                        bootable=True,
                    ),
                    dict(
                        size_gigabytes=15,
                        fs_type="ext4",
                        mount_point="storage",
                        bootable=False,
                        tags="/dev/vdb",
                    ),
                ],
            ),
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.block_device.RestClient.get_record"
        ).return_value = dict(
            firmware_version=None,
            system_id="y7388k",
            block_size=102400,
            available_size=1000000000,
            model="fakemodel",
            serial=123,
            used_size=0,
            tags=["tag-BGt1BR", "tag-1Fm39m", "tag-Hqbbak"],
            partition_table_type=None,
            partitions=[
                dict(
                    uuid="95f5d47d-0abd-408b-b3f1-c3f4df152609",
                    size=7994343424,
                    bootable=False,
                    tags=[],
                    path="/dev/disk/by-dname/vda-part1",
                    system_id="ccrfnk",
                    used_for="ext4 formatted filesystem mounted at /",
                    filesystem=dict(
                        fstype="ext4",
                        label="root",
                        uuid="f698b5ee-d53c-4538-86cf-ee4b23d37db6",
                        mount_point="/",
                        mount_options=None,
                    ),
                    id=1,
                    type="partition",
                    device_id=1,
                    resource_uri="/MAAS/api/2.0/nodes/ccrfnk/blockdevices/1/partition/1",
                ),
            ],
            path="/dev/disk/by-dname/newblockdevice",
            size=1000000000,
            id_path="/dev/tmp",
            filesystem=None,
            storage_pool=None,
            name="newblockdevice",
            used_for="Unused",
            id=73,
            type="physical",
            uuid=None,
            resource_uri="/MAAS/api/2.0/nodes/y7388k/blockdevices/73/",
        )

        assert BlockDevice.get_by_name(module, client, machine_id, True) == BlockDevice(
            name="newblockdevice",
            id=73,
            machine_id="y7388k",
            model="fakemodel",
            serial=123,
            id_path="/dev/tmp",
            block_size=102400,
            size=1000000000,
            tags=["tag-BGt1BR", "tag-1Fm39m", "tag-Hqbbak"],
        )
