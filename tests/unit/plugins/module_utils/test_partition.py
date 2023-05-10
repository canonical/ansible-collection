# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.maas.maas.plugins.module_utils import errors
from ansible_collections.maas.maas.plugins.module_utils.client import Response
from ansible_collections.maas.maas.plugins.module_utils.partition import (
    Partition,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        partition_maas_dict = dict(
            id=5014,
            system_id="machine-id",
            device_id=12,
            bootable=True,
            tags=["my-tag", "my-tag2"],
            size=100000,
            filesystem=dict(
                fstype="ext4",
                label="media",
                mount_point="/media",
                mount_options="options",
            ),
        )
        partition = Partition(
            partition_maas_dict["id"],
            partition_maas_dict["system_id"],
            partition_maas_dict["device_id"],
            partition_maas_dict["size"],
            partition_maas_dict["bootable"],
            partition_maas_dict["tags"],
            partition_maas_dict["filesystem"]["fstype"],
            partition_maas_dict["filesystem"]["label"],
            partition_maas_dict["filesystem"]["mount_point"],
            partition_maas_dict["filesystem"]["mount_options"],
        )
        results = Partition.from_maas(partition_maas_dict)
        assert results == partition


class TestGet:
    def test_get_by_id_200(self, client, mocker):
        id = 5
        machine_id = "machine-id"
        block_device_id = 10
        client.get.return_value = Response(
            200,
            '{"id":5, "system_id":"machine-id","device_id":10, "bootable":true, "tags":[], "size":100000,\
                 "filesystem":{"fstype":"ext4", "label":"media", "mount_point": "/media", "mount_options":"options"}}',
        )
        partition = Partition(
            id=5,
            machine_id="machine-id",
            block_device_id=10,
            size=100000,
            bootable=True,
            tags=[],
            fstype="ext4",
            label="media",
            mount_point="/media",
            mount_options="options",
        )
        results = Partition.get_by_id(
            id, client, machine_id, block_device_id, must_exist=False
        )

        client.get.assert_called_with(
            "/api/2.0/nodes/machine-id/blockdevices/10/partition/5",
        )
        assert results == partition

    def test_get_by_id_404(self, client, mocker):
        id = 5
        machine_id = "machine-id"
        block_device_id = 10
        client.get.return_value = Response(404, "{}")
        results = Partition.get_by_id(
            id, client, machine_id, block_device_id, must_exist=False
        )

        client.get.assert_called_with(
            "/api/2.0/nodes/machine-id/blockdevices/10/partition/5",
        )
        assert results is None

    def test_get_by_id_404_must_exist(self, client, mocker):
        id = 5
        machine_id = "machine-id"
        block_device_id = 10
        client.get.return_value = Response(404, "{}")

        with pytest.raises(errors.PartitionNotFound) as exc:
            Partition.get_by_id(
                id, client, machine_id, block_device_id, must_exist=True
            )

        assert "Partition - 5 - not found" in str(exc.value)
