# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

# from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.modules import vm_host
from ansible_collections.canonical.maas.plugins.module_utils.vmhost import VMHost
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine

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
            vm_host_name="my-vm-host",
            machine_fqdn="my-machine.maas",
            timeout=100,
            state="present",
            power_parameters=dict(
                power_type="virsh",
                power_address="0.0.0.0",
                power_user="user",
                power_pass="pass",
            ),
            cpu_over_commit_ratio=1,
            memory_over_commit_ratio=2,
            default_macvlan_mode="bridge",
            new_vm_host_name="new-vm-host",
            pool="my-pool",
            zone="my-zone",
            tags="my-tag",
        )

        success, result = run_main(vm_host, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            vm_host_name="my-vm-host",
            state="present",
        )

        success, result = run_main(vm_host, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(vm_host)

        assert success is False
        assert "missing required arguments: state, vm_host_name" in result["msg"]


class TestDataForCreateVMHost:
    def test_data_for_create_vm_host(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                vm_host_name="my-vm-host",
                machine=None,
                state="present",
                power_parameters=dict(
                    power_type="virsh",
                    power_address="0.0.0.0",
                    power_user="user",
                    power_pass="pass",
                ),
                cpu_over_commit_ratio=1,
                memory_over_commit_ratio=2,
                default_macvlan_mode="bridge",
                new_vm_host_name=None,
                pool="my-pool",
                zone="my-zone",
                tags="my-tag, my-tag2",
            ),
        )
        data = vm_host.data_for_create_vm_host(module)
        assert data == {
            "type": "virsh",
            "power_address": "0.0.0.0",
            "power_user": "user",
            "power_pass": "pass",
            "tags": "my-tag, my-tag2",
            "zone": "my-zone",
            "pool": "my-pool",
            "name": "my-vm-host",
        }


class TestDataForUpdateVMHost:
    def test_data_for_update_vm_host(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                vm_host_name="my-vm-host",
                machine=None,
                state="present",
                power_parameters=dict(
                    power_type=None,
                    power_address="0.0.0.0",
                    power_user=None,
                    power_pass="pass",
                ),
                cpu_over_commit_ratio=1,
                memory_over_commit_ratio=2,
                default_macvlan_mode="bridge",
                new_vm_host_name="new-vm-host",
                pool="my-pool",
                zone="my-zone",
                tags="my-tag, my-tag2",
            ),
        )

        vm_host_obj = VMHost(
            name="old-name",
            cpu_over_commit_ratio=5,
            memory_over_commit_ratio=6,
            default_macvlan_mode="passthru",
            pool="old-pool",
            zone="old-zone",
            tags="old-tag",
        )

        data = vm_host.data_for_update_vm_host(module, vm_host_obj)
        assert data == {
            "power_address": "0.0.0.0",
            "power_pass": "pass",
            "tags": "my-tag, my-tag2",
            "zone": "my-zone",
            "pool": "my-pool",
            "name": "new-vm-host",
            "cpu_over_commit_ratio": 1,
            "memory_over_commit_ratio": 2,
            "default_macvlan_mode": "bridge",
        }


class TestDataForDeployMachine:
    def test_for_deploy_machine_as_lxd_vm_host(self):
        machine = Machine(power_type="lxd")
        data = vm_host.data_for_deploy_machine_as_vm_host(machine)
        assert data == {
            "install_kwm": False,
            "register_vmhost": True,
        }

    def test_for_deploy_machine_as_virsh_vm_host(self):
        machine = Machine(power_type="virsh")
        data = vm_host.data_for_deploy_machine_as_vm_host(machine)
        assert data == {
            "install_kwm": True,
            "register_vmhost": False,
        }
