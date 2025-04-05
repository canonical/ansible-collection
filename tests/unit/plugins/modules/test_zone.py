# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import zone
from ansible_collections.canonical.maas.plugins.module_utils.zone import Zone

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
            name="my-zone",
            state="present",
            new_name="updated-zone",
            description="Zone name has been updated",
        )

        success, result = run_main(zone, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            name="my-zone",
            state="present",
        )

        success, result = run_main(zone, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(zone)

        assert success is False
        assert "missing required arguments: name, state" in result["msg"]


class TestDataForCreateZone:
    def test_data_for_create_zone(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                name="my-zone",
                new_name=None,
                description=None,
            )
        )
        data = zone.data_for_create_zone(module)

        assert data == dict(name="my-zone")


class TestDataForUpdateZone:
    def test_data_for_update_zone(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                name="old-name",
                new_name="new-name",
                description="description",
            ),
        )
        old_zone = Zone(name="old-name")
        data = zone.data_for_update_zone(module, old_zone)

        assert data == dict(
            description="description",
            name="new-name",
        )

