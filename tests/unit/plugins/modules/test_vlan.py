# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import vlan
from ansible_collections.canonical.maas.plugins.module_utils.vlan import Vlan

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
            state="present",
            fabric_name="fabric-10",
            vid=5,
            vlan_name="vlan_name",
            new_vlan_name="new_vlan_name",
            description="vlan description",
            mtu=1500,
            dhcp_on=True,
            relay_vlan=17,
            space="my-space",
        )

        success, result = run_main(vlan, params)

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
            fabric_name="fabric-10",
            vid=5,
        )

        success, result = run_main(vlan, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(vlan)

        assert success is False
        assert "missing required arguments: fabric_name, state" in result["msg"]

    def test_required_one_of(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            state="present",
            fabric_name="fabric-10",
        )
        success, result = run_main(vlan, params)

        assert success is False
        assert "one of the following is required: vid, vlan_name" in result["msg"]


class TestDataForCreateSpace:
    def test_data_for_create_vlan(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                fabric_name="fabric-10",
                vid=5,
                vlan_name="vlan_name",
                new_vlan_name="new_vlan_name",
                description="vlan description",
                mtu=1500,
                dhcp_on=True,
                space="my-space",
                relay_vlan=17,
            )
        )
        data = vlan.data_for_create_vlan(module)

        assert data == dict(
            vid=5,
            name="vlan_name",
            description="vlan description",
            mtu=1500,
            space="my-space",
            relay_vlan=17,
        )


class TestDataForUpdateSpace:
    def test_data_for_update_vlan(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                fabric_name="fabric-10",
                vid=5,
                new_vlan_name="new-name",
                description="vlan description",
                mtu=2000,
                dhcp_on=True,
                space="new-space",
                relay_vlan=17,
            )
        )
        old_vlan = Vlan(
            vid=5,
            name="old-name",
            mtu=1500,
            dhcp_on=False,
            space="old-space",
        )
        data = vlan.data_for_update_vlan(module, old_vlan)

        assert data == dict(
            name="new-name",
            description="vlan description",  # description is not returned
            mtu=2000,
            space="new-space",
            dhcp_on=True,
            relay_vlan=17,
        )
