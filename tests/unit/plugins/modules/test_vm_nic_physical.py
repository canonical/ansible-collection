# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import vm_nic_physical
from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.module_utils.network_interface import (
    NetworkInterface,
)
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            vm_host="this_host",
            hostname="this-machine",
            mac_address="this-mac",
            state="present",
        )

        success, results = run_main(vm_nic_physical, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            vm_host="this_host",
            hostname="this-machine",
            mac_address="this-mac",
            state="present",
            vlan="this-vlan",
            name="this-interface",
            mtu=1500,
            tags=["tag1", "tag2"],
        )

        success, results = run_main(vm_nic_physical, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }


class TestRun:
    @staticmethod
    def get_machine_state_new():
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

    @staticmethod
    def get_machine_state_allocating():
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
            status_name="Allocating",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_machine_state_ready():
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
            status_name="Ready",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-pwoertype",
            architecture="this-architecture",
        )

    def test_run_with_present_with_machine_wrong_state(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = machine_obj
        with pytest.raises(
            errors.MaasError,
            match=f"Machine {machine_obj.hostname} is not in the right state, needs to be in Ready, Allocated or Broken.",
        ):
            vm_nic_physical.run(module, client)

    def test_run_with_present_with_waiting_on_machine_state(
        self, create_module, client, mocker
    ):
        expected = (False, {}, {"before": {}, "after": {}})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        machine_dict = self.get_machine_state_allocating()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.wait_for_state"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.vm_nic_physical.ensure_present"
        ).return_value = (False, {}, {"before": {}, "after": {}})
        results = vm_nic_physical.run(module, client)
        assert results == expected

    def test_run_with_present_ensure_present(self, create_module, client, mocker):
        expected = (False, {}, {"before": {}, "after": {}})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        machine_dict = self.get_machine_state_ready()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.vm_nic_physical.ensure_present"
        ).return_value = (False, {}, {"before": {}, "after": {}})
        results = vm_nic_physical.run(module, client)
        assert results == expected

    def test_run_with_absent_ensure_absent(self, create_module, client, mocker):
        expected = (False, {}, {"before": {}, "after": {}})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        machine_dict = self.get_machine_state_ready()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.vm_nic_physical.ensure_absent"
        ).return_value = (False, {}, {"before": {}, "after": {}})
        results = vm_nic_physical.run(module, client)
        assert results == expected


class TestEnsurePresent:
    @staticmethod
    def get_machine_state_new():
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

    @staticmethod
    def get_machine_updated():
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
                    tags=None,
                    effective_mtu=2000,
                    ip_address="this-ip",
                    cidr="this-cidr",
                    vlan=dict(name="this-vlan", fabric="this-fabric"),
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
    def get_nic():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=None,
            effective_mtu=2000,
            ip_address="this-ip",
            cidr="this-cidr",
            vlan=dict(name="this-vlan", fabric="this-fabric"),
        )

    @staticmethod
    def get_nic_existing():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=None,
            effective_mtu=1500,
            ip_address="this-ip",
            cidr="this-cidr",
            vlan=dict(name="this-vlan", fabric="this-fabric"),
        )

    def test_ensure_present_when_create_new_nic(self, create_module, client, mocker):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        updated_machine_dict = self.get_machine_updated()
        updated_machine_obj = Machine.from_maas(updated_machine_dict)
        nic_dict = self.get_nic()
        nic_obj = NetworkInterface.from_maas(nic_dict)
        expected = (
            True,
            nic_obj.to_ansible(),
            {"before": None, "after": nic_obj.to_ansible()},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = nic_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_mac"
        ).side_effect = [None, nic_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_create_request"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.payload_for_create"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = updated_machine_obj
        results = vm_nic_physical.ensure_present(module, client, machine_obj)
        assert results == expected

    def test_ensure_present_when_update_existing_nic(
        self, create_module, client, mocker
    ):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        updated_machine_dict = self.get_machine_updated()
        updated_machine_obj = Machine.from_maas(updated_machine_dict)
        nic_dict = self.get_nic()
        nic_obj = NetworkInterface.from_maas(nic_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        expected = (
            True,
            nic_obj.to_ansible(),
            {"before": existing_nic_obj.to_ansible(), "after": nic_obj.to_ansible()},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
                mtu=2000,
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = nic_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_mac"
        ).side_effect = [existing_nic_obj, nic_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.needs_update"
        ).return_value = True
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_update_request"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.payload_for_update"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = updated_machine_obj
        results = vm_nic_physical.ensure_present(module, client, machine_obj)
        assert results == expected

    def test_ensure_present_when_no_changes_nic(self, create_module, client, mocker):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        updated_machine_dict = self.get_machine_updated()
        updated_machine_obj = Machine.from_maas(updated_machine_dict)
        nic_dict = self.get_nic_existing()
        nic_obj = NetworkInterface.from_maas(nic_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        expected = (False, None, {"before": None, "after": None})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
                mtu=2000,
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = nic_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_mac"
        ).side_effect = [existing_nic_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.needs_update"
        ).return_value = False
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = updated_machine_obj
        results = vm_nic_physical.ensure_present(module, client, machine_obj)
        assert results == expected


class TestEsnureAbsent:
    @staticmethod
    def get_machine_state_new():
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
            power_type="this-power-type",
            architecture="this-architecture"
        )

    @staticmethod
    def get_machine_updated():
        return dict(
            fqdn = "this-machine-fqdn",
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
                    tags=None,
                    effective_mtu=2000,
                    ip_address="this-ip",
                    cidr="this-cidr",
                    vlan=dict(name="this-vlan", fabric="this-fabric"),
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
        )
    
    @staticmethod
    def get_nic_existing():
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
        )

    def test_ensure_absent_when_delete_existing_nic(
        self, create_module, client, mocker
    ):
        machine_dict = self.get_machine_updated()
        machine_obj = Machine.from_maas(machine_dict)
        updated_machine_dict = self.get_machine_state_new()
        updated_machine_obj = Machine.from_maas(updated_machine_dict)
        nic_dict = self.get_nic()
        nic_obj = NetworkInterface.from_maas(nic_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        expected = (
            True,
            None,
            {"before": existing_nic_obj.to_ansible(), "after": None},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = nic_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_mac"
        ).side_effect = [existing_nic_obj, None]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.needs_update"
        ).return_value = True
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_update_request"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.payload_for_update"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_name_and_host"
        ).return_value = updated_machine_obj
        results = vm_nic_physical.ensure_absent(module, client, machine_obj)
        print(results)
        assert results == expected

    def test_ensure_absent_when_no_changes_nic(self, create_module, client, mocker):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        expected = (False, None, {"before": None, "after": None})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                vm_host="this-host",
                hostname="this-machine",
                mac_address="this-mac",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_mac"
        ).return_value = None
        results = vm_nic_physical.ensure_absent(module, client, machine_obj)
        assert results == expected

    def test_ensure_absent_when_delete_existing_nic_but_no_changes(self):
        pass
