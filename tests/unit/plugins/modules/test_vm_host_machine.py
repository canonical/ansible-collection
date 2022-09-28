# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import vm_host_machine
from ansible_collections.canonical.maas.plugins.module_utils.vmhost import VMHost
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://my.host.name",
                client_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            state="ready",
            vm_host="this_host",
        )

        success, results = run_main(vm_host_machine, params)
        print(success, results)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://my.host.name",
                client_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            state="ready",
            vm_host="this_host",
            cores=3,
            memory=2048,
            network_interfaces={"name": "my_interface", "subnet_cidr": "10.10.10.0/24"},
            storage_disks=[{"size_gigabytes": 15}, {"size_gigabytes": 10}],
        )

        success, results = run_main(vm_host_machine, params)
        print(success, results)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }

class TestRun:
    @staticmethod
    def _get_empty_host_dict():
        return dict(name="test_name", id="1234")

    def test_run_when_state_ready_and_net_interface_and_storage(
        self, create_module, client, mocker
    ):
        host_dict = self._get_empty_host_dict()
        host_obj = VMHost.from_ansible(host_dict)
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="ready",
                vm_host="test_name",
                cores=2,
                memory=5000,
                network_interfaces=None,
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.vmhost.VMHost.get_by_name"
        ).return_value = host_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.vm_host_machine.ensure_ready"
        ).return_value = (
            True,
            [{"machine_name": "some_name", "id": "new_id", "memory": 5000, "cores": 2}],
            {
                "before": [],
                "after": [
                    {
                        "machine_name": "some_name",
                        "id": "new_id",
                        "memory": 5000,
                        "cores": 2,
                    }
                ],
            },
        )
        results = vm_host_machine.run(module, client)
        print(results)
        assert results == (
            True,
            [{"machine_name": "some_name", "id": "new_id", "memory": 5000, "cores": 2}],
            {
                "before": [],
                "after": [
                    {
                        "machine_name": "some_name",
                        "id": "new_id",
                        "memory": 5000,
                        "cores": 2,
                    }
                ],
            },
        )

    def test_run_when_state_ready_and_no_net_interface_and_no_storage(
        self, create_module, client, mocker
    ):
        host_dict = self._get_empty_host_dict()
        host_obj = VMHost.from_ansible(host_dict)
        after = [
            {
                "machine_name": "some_name",
                "id": "new_id",
                "memory": 5000,
                "cores": 2,
                "network_interfaces": [{"name": "this_name", "subnet_cidr": "some_ip"}],
                "storage_disks": [{"size_gigabytes": 5}, {"size_gigabytes": 6}],
            }
        ]
        before = []
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="ready",
                vm_host="test_name",
                cores=2,
                memory=5000,
                network_interfaces={"name": "this_name", "subnet_cidr": "some_ip"},
                storage_disks=[{"size_gigabytes": 5}, {"size_gigabytes": 6}],
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.vmhost.VMHost.get_by_name"
        ).return_value = host_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.vm_host_machine.ensure_ready"
        ).return_value = (True, after, dict(before=before, after=after))
        results = vm_host_machine.run(module, client)
        print(results)
        assert results == (True, after, dict(before=before, after=after))

class TestPrepareNetworkData:
    def test_prepare_network_data(self, create_module):
        network_interfaces = {"name": "this_name", "subnet_cidr": "some_ip"}
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="ready",
                vm_host="test_name",
                cores=2,
                memory=5000,
                network_interfaces=network_interfaces,
                storage_disks=[{"size_gigabytes": 5}, {"size_gigabytes": 6}],
            )
        )
        vm_host_machine.prepare_network_data(module)
        print(module.params["network_interfaces"])
        assert module.params["network_interfaces"] == [network_interfaces]

class TestEnsureReady:
    @staticmethod
    def _get_empty_host_dict():
        return dict(name="test_name", id="1234")

    @staticmethod
    def _get_empty_machine_dict():
        return dict(hostname="machine_1", cpu_count=2, memory=5000, system_id="123", interface_set=None, blockdevice_set=None)

    @staticmethod
    def _get_machine_dict():
        return dict(hostname="machine_2", cpu_count=2, memory=5000, system_id="123", interface_set=[{"id": "123", "name": "this_name", "links": [{"subnet": {"cidr": "some_ip"}}], "system_id": 1}], blockdevice_set=[{"size":5, "name": "1", "id":"1"}, {"size":5, "name":"2", "id":"2"}])

    def test_ensure_ready_without_storaga_and_net_interfaces(self, create_module, client, mocker):
        before = []
        after = [{'hostname': 'machine_1', 'cpu_count': 2, 'memory': 5000, 'system_id': '123', 'interface_set': None, 'blockdevice_set': None}]
        task = {"system_id": "1234", "resource_uri": "https://www.something-somewhere.com"}
        payload = {"payload": ""}
        host_dict = self._get_empty_host_dict()
        host_obj = VMHost.from_maas(host_dict)
        machine_dict = self._get_empty_machine_dict()
        machine_obj = Machine.from_maas(machine_dict)
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="ready",
                vm_host="test_name",
                cores=2,
                memory=5000,
                network_interfaces=None,
                storage_disks=None,
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.from_ansible"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.payload_for_compose"
        ).return_value = payload
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.vmhost.VMHost.send_compose_request"
        ).return_value = task
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_id"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_ansible"
        ).return_value = machine_dict
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.utils.is_changed"
        ).return_value = True
        results = vm_host_machine.ensure_ready(module, client, host_obj)
        print(results)
        assert results == (True, after, dict(before=before, after=after))

    def test_ensure_ready_with_storage_and_net_interfaces(self, create_module, client, mocker):
        before = []
        after = [{'hostname': 'machine_2', 'cpu_count': 2, 'memory': 5000, 'system_id': '123', 'interface_set': [{'id': '123', 'name': 'this_name', 'links': [{'subnet': {'cidr': 'some_ip'}}], 'system_id': 1}], 'blockdevice_set': [{'size': 5, 'name': '1', 'id': '1'}, {'size': 5, 'name': '2', 'id': '2'}]}]
        task = {"system_id": "1234", "resource_uri": "https://www.something-somewhere.com"}
        payload = {"payload": ""}
        network_interfaces = {"name": "this_name", "subnet_cidr": "some_ip"}
        storage_disks = [{"size_gigabytes": 5},{"size_gigabytes": 5}]
        host_dict = self._get_empty_host_dict()
        host_obj = VMHost.from_maas(host_dict)
        machine_dict = self._get_machine_dict()
        machine_obj = Machine.from_maas(machine_dict)
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="ready",
                vm_host="test_name",
                cores=2,
                memory=5000,
                network_interfaces=network_interfaces,
                storage_disks=storage_disks,
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.from_ansible"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.payload_for_compose"
        ).return_value = payload
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.vmhost.VMHost.send_compose_request"
        ).return_value = task
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_id"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_ansible"
        ).return_value = machine_dict
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.utils.is_changed"
        ).return_value = True
        results = vm_host_machine.ensure_ready(module, client, host_obj)
        print(results, "----------------------------", (True, after, dict(before=before, after=after)))
        assert results == (True, after, dict(before=before, after=after))
