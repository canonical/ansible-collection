# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible_collections.canonical.maas.plugins.module_utils.network_interface import (
    NetworkInterface,
)

__metaclass__ = type

import sys

import pytest

import json
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
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.from_maas"
        ).return_value = None
        client.get.return_value = Response(200, "{}")
        results = Machine.get_by_id(id, client)
        assert results is None

    def test_get_by_name(self, create_module, mocker, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                fqdn="my_instance.maas",
                hostname="my_instance",
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
            fqdn="my_instance.maas",
            hostname="my_instance",
            system_id="system_id",
            memory=2000,
            cpu_count=2,
            interface_set=None,
            blockdevice_set=None,
            status_name="Ready",
            osystem="ubuntu",
            distro_series="jammy",
            domain=dict(id=3),
            pool=dict(id=1),
            zone=dict(id=2),
            tag_names=["my_tag"],
            hwe_kernel="my_kernel",
            min_hwe_kernel="min_kernel",
            power_type="lxd",
            architecture="amd64",
        )

        assert Machine.get_by_name(module, client, True) == Machine(
            fqdn="my_instance.maas",
            hostname="my_instance",
            id="system_id",
            pool=1,
            zone=2,
            memory=2000,
            cores=2,
            network_interfaces=[],
            disks=[],
            status="Ready",
            osystem="ubuntu",
            distro_series="jammy",
            tags=["my_tag"],
            hwe_kernel="my_kernel",
            min_hwe_kernel="min_kernel",
            domain=3,
            power_type="lxd",
            architecture="amd64",
        )

    def test_get_by_fqdn(self, create_module, mocker, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                fqdn="my_instance.maas",
                hostname="my_instance",
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
            fqdn="my_instance.maas",
            hostname="my_instance",
            system_id="system_id",
            memory=2000,
            cpu_count=2,
            interface_set=None,
            blockdevice_set=None,
            status_name="Ready",
            osystem="ubuntu",
            distro_series="jammy",
            domain=dict(id=3),
            pool=dict(id=1),
            zone=dict(id=2),
            tag_names=["my_tag"],
            hwe_kernel="my_kernel",
            min_hwe_kernel="min_kernel",
            power_type="lxd",
            architecture="amd64",
        )

        assert Machine.get_by_name(module, client, True) == Machine(
            fqdn="my_instance.maas",
            hostname="my_instance",
            id="system_id",
            pool=1,
            zone=2,
            memory=2000,
            cores=2,
            network_interfaces=[],
            disks=[],
            status="Ready",
            osystem="ubuntu",
            distro_series="jammy",
            tags=["my_tag"],
            hwe_kernel="my_kernel",
            min_hwe_kernel="min_kernel",
            domain=3,
            power_type="lxd",
            architecture="amd64",
        )


class TestPayloadForCompose:
    def test_payload_for_compose_with_interface_and_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(
            interfaces=[
                dict(
                    label_name="test",
                    name="esp0",
                    subnet_cidr="subnet",
                    fabric="fabric-1",
                    vlan="vlan-1",
                    ip_address="ip",
                )
            ],
            storage=[dict(size=5), dict(size=10)],
        )
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {
            "interfaces": "test:subnet_cidr=subnet,ip=ip,fabric=fabric-1,vlan=vlan-1,name=esp0",
            "storage": "label:5,label:10",
        }

    def test_payload_for_compose_without_interface_and_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict()
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {}

    def test_payload_for_compose_with_storage_without_interface(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(storage=[dict(size=5), dict(size=10)])
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {"storage": "label:5,label:10"}

    def test_payload_for_compose_with_interface_without_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(
            interfaces=[dict(label_name="test", name="esp0", subnet_cidr="ip")]
        )
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {"interfaces": "test:subnet_cidr=ip,name=esp0"}


class TestWaitForState:
    def test_wait_for_state(self, client, mocker):
        system_id = "system_id"

        client.get.return_value = Response(
            200,
            json.dumps(
                dict(
                    hostname="my_instance",
                    system_id="system_id",
                    status_name="Commissioning",
                ),
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.from_maas"
        ).return_value = Machine(
            id="system_id", hostname="my_instance", status="Commissioning"
        )

        machine = Machine.wait_for_state(
            system_id, client, False, "Ready", "Commissioning"
        )

        assert machine.status == "Commissioning"


class TestCommission:
    def test_commission(self, client):
        machine = Machine(
            hostname="my_instance",
            id=123,
        )

        machine.commission(client)

        client.post.assert_called_with(
            "/api/2.0/machines/123/", query={"op": "commission"}, data={}
        )


class TestDeploy:
    def test_deploy(self, client):
        machine = Machine(
            hostname="my_instance",
            id=123,
        )
        payload = {"osystem": "ubuntu"}
        timeout = 20

        machine.deploy(client, payload, timeout)

        client.post.assert_called_with(
            "/api/2.0/machines/123/",
            query={"op": "deploy"},
            data={"osystem": "ubuntu"},
            timeout=20,
        )


class TestDelete:
    def test_delete(self, client):
        machine = Machine(
            hostname="my_instance",
            id=123,
        )

        machine.delete(client)

        client.delete.assert_called_with(
            "/api/2.0/machines/123/",
        )


class TestRelease:
    def test_release(self, client):
        machine = Machine(
            hostname="my_instance",
            id=123,
        )

        machine.release(client)

        client.post.assert_called_with(
            "/api/2.0/machines/123/",
            query={"op": "release"},
            data={},
        )


class TestFindNic:
    @staticmethod
    def get_nic():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=["tag1", "tag2"],
            effective_mtu=1500,
            ip_address="this-ip",
            subnet_cidr="this-subnet",
            vlan=None,
            links=[],
        )

    @staticmethod
    def get_machine():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=[
                dict(
                    name="this-nic",
                    id=123,
                    mac_address="this-mac",
                    system_id=123,
                    tags=["tag1", "tag2"],
                    effective_mtu=1500,
                    ip_address="this-ip",
                    subnet_cidr="this-subnet",
                    vlan=None,
                    links=[],
                )
            ],
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_machine_no_nic():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=None,
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    def test_find_nic_by_mac_when_nic_found(self):
        nic_dict = self.get_nic()
        nic_obj = NetworkInterface.from_maas(nic_dict)
        machine_dict = self.get_machine()
        machine_obj = Machine.from_maas(machine_dict)
        mac_address = "this-mac"
        expected = nic_obj
        results = machine_obj.find_nic_by_mac(mac_address)
        assert results == expected

    def test_nic_by_mac_when_nic_not_found(self):
        machine_dict = self.get_machine_no_nic()
        machine_obj = Machine.from_maas(machine_dict)
        mac_address = "this-mac"
        expected = None
        results = machine_obj.find_nic_by_mac(mac_address)
        assert results == expected

    def test_find_nic_by_name_when_nic_found(self):
        nic_dict = self.get_nic()
        nic_obj = NetworkInterface.from_maas(nic_dict)
        machine_dict = self.get_machine()
        machine_obj = Machine.from_maas(machine_dict)
        nic_name = "this-nic"
        expected = nic_obj
        results = machine_obj.find_nic_by_name(nic_name)
        assert results == expected

    def test_nic_by_name_when_nic_not_found(self):
        machine_dict = self.get_machine_no_nic()
        machine_obj = Machine.from_maas(machine_dict)
        nic_name = "this-nic"
        expected = None
        results = machine_obj.find_nic_by_name(nic_name)
        assert results == expected


# TODO: test mapper, when more values are added.
