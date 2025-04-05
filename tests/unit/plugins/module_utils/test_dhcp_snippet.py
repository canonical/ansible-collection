# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.dhcp_snippet import (
    DhcpSnippet,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_dhcp_snippet_dict = get_dhcp_snippet()
        dhcp_snippet = DhcpSnippet(**get_dhcp_snippet())
        results = DhcpSnippet.from_maas(maas_dhcp_snippet_dict)
        assert results == dhcp_snippet

    def test_to_ansible(self):
        dhcp_snippet = DhcpSnippet(**get_dhcp_snippet())

        ansible_dict = get_dhcp_snippet()

        results = dhcp_snippet.to_ansible()
        assert results == ansible_dict


class TestGet:
    def test_get_by_name(self, create_module, mocker, client):
        name = "dhcp-snippet-name"
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                name="dhcp-snippet-name",
                description="snippet description",
                enabled=True,
                subnet="test-subnet-name",
                global_snippet=False,
                value="max-lease-time 7200;",
            )
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = get_dhcp_snippet()

        assert DhcpSnippet.get_by_name(module, client, name, True) == DhcpSnippet(
            **get_dhcp_snippet()
        )


def get_dhcp_snippet():
    return dict(
        name="dhcp-snippet-name",
        description="snippet description",
        enabled=True,
        subnet="test-subnet-name",
        global_snippet=False,
        value="max-lease-time 7200;",
        history=[],
        id=6,
        resource_uri="/MAAS/api/2.0/dhcp-snippets/6/",
    )
