# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import dhcp_snippet
from ansible_collections.canonical.maas.plugins.module_utils.dhcp_snippet import (
    DhcpSnippet,
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
            name="dhcp-snippet-name",
            description="snippet description",
            enabled=True,
            subnet="test-subnet-name",
            global_snippet=False,
            value="max-lease-time 7200;",
            state="present",
        )

        success, result = run_main(dhcp_snippet, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            name="dhcp-snippet-name",
            value="max-lease-time 7200;",
            state="present",
        )

        success, result = run_main(dhcp_snippet, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(dhcp_snippet)

        assert success is False
        assert "missing required arguments: name, state, value" in result["msg"]


class TestDataForCreateDhcpSnippet:
    def test_data_for_create_dhcp_snippet(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                name="dhcp-snippet-name",
                description="snippet description",
                enabled=True,
                subnet="test-subnet-name",
                global_snippet=False,
                value="max-lease-time 7200;",
            )
        )
        data = dhcp_snippet.data_for_create_dhcp_snippet(module)

        assert data == dict(
            name="dhcp-snippet-name",
            description="snippet description",
            enabled=True,
            subnet="test-subnet-name",
            global_snippet=False,
            value="max-lease-time 7200;",
        )


class TestDataForUpdateDhcpSnippet:
    def test_data_for_update_dhcp_snippet(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                name="dhcp-snippet-name",
                description="snippet description",
                enabled=True,
                subnet="",
                global_snippet=True,
                value="max-lease-time 3600;",
            )
        )
        old_dhcp_snippet = DhcpSnippet(
            name="dhcp-snippet-name",
            enabled=True,
            subnet=dict(name="subnet-1"),
            global_snippet=False,
            value="max-lease-time 7200;",
        )
        data = dhcp_snippet.data_for_update_dhcp_snippet(module, old_dhcp_snippet)

        assert data == dict(
            global_snippet=True,
            value="max-lease-time 3600;",
            description="snippet description",
        )
