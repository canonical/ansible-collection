# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import block_device
from ansible_collections.canonical.maas.plugins.module_utils.block_device import (
    BlockDevice,
)
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine
from ansible_collections.canonical.maas.plugins.module_utils.state import (
    MachineTaskState,
)


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            machine_fqdn="block-device-test.maas",
            name="my-block-device",
            new_name="my-block-device-updated",
            state="present",
            # id_path="/dev/vdb",
            size_gigabytes=27,
            tags=["ssd"],
            block_size=512,
            is_boot_device=True,
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
            model="model",
            serial="serial",
        )

        success, result = run_main(block_device, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            machine_fqdn="block-device-test.maas",
            name="my-block-device",
            state="present",
        )

        success, result = run_main(block_device, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(block_device)

        assert success is False
        assert "missing required arguments: machine_fqdn, name, state" in result["msg"]

    def test_required_together(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            machine_fqdn="block-device-test.maas",
            name="my-block-device",
            state="present",
            model="model",
        )
        success, result = run_main(block_device, params)

        assert success is False
        assert "parameters are required together: model, serial" in result["msg"]

    def test_mutually_exclusive(self, run_main):
        params = dict(
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
            model="model",
            serial="serial",
        )
        success, result = run_main(block_device, params)

        assert success is False
        assert (
            "parameters are mutually exclusive: model|id_path, serial|id_path"
            in result["msg"]
        )


class TestDataForCreateBlockDevice:
    def test_data_for_create_block_device(self, create_module):
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
                is_boot_device=True,
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
                tags=["ssd"],
                block_size=600,
                model="model",
                serial="serial",
            )
        )
        data = block_device.data_for_create_block_device(module)

        assert data == dict(
            name="my-block-device",
            id_path="/dev/vdb",
            size=27 * 1000000,
            block_size=600,
            model="model",
            serial="serial",
        )

    def test_data_for_create_block_device_default(self, create_module):
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
                size_gigabytes=27,
                block_size=None,
                model=None,
                serial=None,
                id_path=None,
            )
        )
        data = block_device.data_for_create_block_device(module)

        assert data == dict(
            name="my-block-device",
            size=27 * 1000000,
            block_size=512,
        )


class TestDataForCreatePartition:
    def test_data_for_create_partition(self):
        partition = dict(
            size_gigabytes=10,
            fs_type="ext4",
            label="media",
            mount_point="/media",
            bootable=True,
        )

        data = block_device.data_for_create_partition(partition)

        assert data == dict(
            size=10 * 1000000,
            bootable=True,
        )


class TestDataForUpdateBlockDevice:
    def test_data_for_update_block_device(self, create_module):
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
                new_name="my-block-device-updated",
                state="present",
                id_path="/dev/vdb",
                size_gigabytes=27,
                is_boot_device=True,
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
                ],  # partitions need id to be updated
                tags=["ssd"],
                block_size=600,
                model="new_model",
                serial="new_serial",
            )
        )
        old_block_device = BlockDevice(
            name="my-block-device",
            model="old_model",
            serial="old_serial",
            id_path="old_path",
            block_size=512,
            size=12000000,
        )
        machine = Machine(status=MachineTaskState.ready.value)
        data = block_device.data_for_update_block_device(
            module, old_block_device, machine
        )

        assert data == dict(
            name="my-block-device-updated",
            model="new_model",
            serial="new_serial",
            id_path="/dev/vdb",
            block_size=600,
            size=27000000,
        )

    def test_data_for_update_block_device_machine_not_ready(self, create_module):
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
                new_name="my-block-device-updated",
                state="present",
                id_path="/dev/vdb",
                size_gigabytes=27,
                is_boot_device=True,
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
                ],  # partitions need id to be updated
                tags=["ssd"],
                block_size=600,
                model="new_model",
                serial="new_serial",
            )
        )
        old_block_device = BlockDevice(
            name="my-block-device",
            model="old_model",
            serial="old_serial",
            id_path="old_path",
            block_size=512,
            size=12000000,
        )
        machine = Machine(status=MachineTaskState.failed_comissioning.value)
        data = block_device.data_for_update_block_device(
            module, old_block_device, machine
        )

        assert data == dict(
            name="my-block-device-updated",
            model="new_model",
            serial="new_serial",
            id_path="/dev/vdb",
        )
