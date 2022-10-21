# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.modules import machine
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
            fqdn="my-machine.maas",
            state="present",
            power_type="virsh",
            power_parameters=dict(
                power_address="0.0.0.0",
                power_user="user",
                power_pass="pass",
            ),
            pxe_mac_address="00:00:00:00:00:01",
            architecture="i386/generic",
            hostname="updated-machine",
            domain="new-domain",
            pool="my-pool",
            zone="my-zone",
            min_hwe_kernel="ga-20.04",
        )

        success, result = run_main(machine, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            state="present",
        )

        success, result = run_main(machine, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(machine)

        assert success is False
        assert "missing required arguments: state" in result["msg"]


class TestDataForAddMachine:
    def test_data_for_add_machine(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                fqdn=None,
                state="present",
                power_type="virsh",
                power_parameters=dict(
                    power_address="0.0.0.0",
                    power_user="user",
                    power_pass="pass",
                ),
                pxe_mac_address="00:00:00:00:00:01",
                architecture="i386/generic",
                hostname="new-machine",
                domain="my-domain",
                pool="my-pool",
                zone="my-zone",
                min_hwe_kernel="ga-20.04",
            ),
        )
        data = machine.data_for_add_machine(module)

        assert data == dict(
            power_type="virsh",
            power_parameters='{"power_address": "0.0.0.0", "power_user": "user", "power_pass": "pass"}',
            mac_addresses="00:00:00:00:00:01",
            architecture="i386/generic",
            hostname="new-machine",
            domain="my-domain",
            pool="my-pool",
            zone="my-zone",
            min_hwe_kernel="ga-20.04",
        )

    @pytest.mark.parametrize(
        "power_type, power_parameters, pxe_mac_address, error",
        [
            (
                "virsh",
                '{"power_address": "0.0.0.0", "power_user": "user", "power_pass": "pass"}',
                None,
                "pxe_mac_address",
            ),
            (
                None,
                '{"power_address": "0.0.0.0", "power_user": "user", "power_pass": "pass"}',
                "00:00:00:00:00:01",
                "power_type",
            ),
            (
                "virsh",
                None,
                "00:00:00:00:00:01",
                "power_parameters",
            ),
        ],
    )
    def test_data_for_add_machine_missing_params(
        self, create_module, power_type, power_parameters, pxe_mac_address, error
    ):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                fqdn=None,
                state="present",
                power_type=power_type,
                power_parameters=power_parameters,
                pxe_mac_address=pxe_mac_address,
                architecture="i386/generic",
                hostname="new-machine",
                domain="my-domain",
                pool="my-pool",
                zone="my-zone",
                min_hwe_kernel="ga-20.04",
            ),
        )

        with pytest.raises(errors.MissingValueAnsible) as exc:
            machine.data_for_add_machine(module)

        assert f"Missing value - {error}" in str(exc.value)


class TestDataForUpdateMachine:
    def test_data_for_update_machine(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                fqdn=None,
                state="present",
                power_type="virsh",
                power_parameters=dict(
                    power_address="0.0.0.0",
                    power_user="user",
                    power_pass="pass",
                ),
                pxe_mac_address="00:00:00:00:00:01",
                architecture="i386/generic",
                hostname="new-machine",
                domain="my-domain",
                pool="new-pool",
                zone="my-zone",
                min_hwe_kernel="ga-20.04",
            ),
        )
        old_machine = Machine(
            architecture="i386/generic",
            hostname="old-machine",
            domain="my-domain",
            pool="my-pool",
            zone="my-zone",
            hwe_kernel="ga-20.04-edge",
        )
        data = machine.data_for_update_machine(module, old_machine)

        assert data == dict(
            power_type="virsh",
            power_parameters='{"power_address": "0.0.0.0", "power_user": "user", "power_pass": "pass"}',
            hostname="new-machine",
            pool="new-pool",
            min_hwe_kernel="ga-20.04",
        )
