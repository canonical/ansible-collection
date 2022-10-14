# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from threading import stack_size

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import vm_nic_physical
from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.module_utils.vmhost import VMHost
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
            state="present"
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
        )

    @staticmethod
    def get_machine_state_allocating():
        return dict(
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
        )

    @staticmethod
    def get_machine_state_ready():
        return dict(
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
        )

    def test_run_with_present_with_machine_wrong_state(self, create_module, client, mocker):
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
    
    def test_run_with_present_with_waiting_on_machine_state(self, create_module, client, mocker):
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
