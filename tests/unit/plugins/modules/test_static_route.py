# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import static_route
from ansible_collections.canonical.maas.plugins.module_utils.static_route import (
    StaticRoute,
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
            source="subnet-1",
            destination="subnet-2",
            gateway_ip="192.168.1.1",
            metric=100,
            state="present",
        )

        success, result = run_main(static_route, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            source="subnet-1",
            destination="subnet-2",
            gateway_ip="192.168.1.1",
            state="present",
        )

        success, result = run_main(static_route, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(static_route)

        assert success is False
        assert (
            "missing required arguments: destination, gateway_ip, source, state"
            in result["msg"]
        )


class TestDataForCreateStaticRoute:
    def test_data_for_create_static_route(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                source="subnet-1",
                destination="subnet-2",
                gateway_ip="192.168.1.1",
            )
        )
        data = static_route.data_for_create_static_route(module)

        assert data == dict(
            source="subnet-1",
            destination="subnet-2",
            gateway_ip="192.168.1.1",
        )


class TestDataForUpdateStaticRoute:
    def test_data_for_update_static_route(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                source="subnet-1",
                destination="subnet-2",
                gateway_ip="192.168.1.1",
                metric=100,
            )
        )
        old_static_route = StaticRoute(
            source="subnet-1",
            destination="subnet-2",
            gateway_ip="192.168.1.1",
        )
        data = static_route.data_for_update_static_route(module, old_static_route)

        assert data == dict(metric=100)
