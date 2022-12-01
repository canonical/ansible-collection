# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.static_route import (
    StaticRoute,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_static_route_dict = get_static_route()
        static_route = StaticRoute(**get_static_route())
        results = StaticRoute.from_maas(maas_static_route_dict)
        assert results == static_route

    def test_to_ansible(self):
        static_route = StaticRoute(**get_static_route())

        ansible_dict = get_static_route()

        results = static_route.to_ansible()
        assert results == ansible_dict


class TestGet:
    def test_get_by_spec(self, create_module, mocker, client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                source="subnet-1",
                destination="subnet-2",
                gateway_ip="192.168.1.1",
                metric=100,
            )
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = get_static_route()

        assert StaticRoute.get_by_spec(module, client, True) == StaticRoute(
            **get_static_route()
        )


def get_static_route():
    return dict(
        source="subnet-1",
        destination="subnet-2",
        gateway_ip="192.168.1.1",
        metric=100,
        id=1,
        resource_uri="/MAAS/api/2.0/static-routes/1/",
    )
