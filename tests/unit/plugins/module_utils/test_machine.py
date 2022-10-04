# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine
from ansible_collections.canonical.maas.plugins.module_utils.client import (
    Response,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestGet:
    def test_get_by_id(self, client, mocker):
        id = 123
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = dict(
            hostname="my_instance",
            system_id=123,
            memory=2000,
            cpu_count=2,
            interface_set=None,
            blockdevice_set=None,
            status_name="Ready",
            osystem="ubuntu",
            distro_series="jammy",
        )

        assert Machine.get_by_id(id, client) == Machine(
            machine_name="my_instance",
            id=123,
            memory=2000,
            cores=2,
            network_interfaces=[],
            disks=[],
            status="Ready",
            osystem="ubuntu",
            distro_series="jammy",
        )

    def test_get_by_name(self, create_module, mocker, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                name="my_instance",
                state="absent",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = dict(
            hostname="my_instance",
            system_id="sytem_id",
            memory=2000,
            cpu_count=2,
            interface_set=None,
            blockdevice_set=None,
            status_name="Ready",
            osystem="ubuntu",
            distro_series="jammy",
        )

        assert Machine.get_by_name(module, client, True) == Machine(
            machine_name="my_instance",
            id="sytem_id",
            memory=2000,
            cores=2,
            network_interfaces=[],
            disks=[],
            status="Ready",
            osystem="ubuntu",
            distro_series="jammy",
        )


class TestPayloadForCompose:
    def test_payload_for_compose_with_interface_and_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(
            interfaces=[dict(name="test", subnet_cidr="ip")],
            storage=[dict(size=5), dict(size=10)],
        )
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        print(results)
        assert results == {
            "interfaces": "test:subnet_cidr=ip",
            "storage": "label:5,label:10",
        }

    def test_payload_for_compose_without_interface_and_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict()
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        print(results)
        assert results == {}

    def test_payload_for_compose_with_storage_without_interface(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(storage=[dict(size=5), dict(size=10)])
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        print(results)
        assert results == {"storage": "label:5,label:10"}

    def test_payload_for_compose_with_interface_without_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(interfaces=[dict(name="test", subnet_cidr="ip")])
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        print(results)
        assert results == {"interfaces": "test:subnet_cidr=ip"}


# TODO: test mapper, when more values are added.
