# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.maas_server_config import (
    MaasServerConfig,
)
from ansible_collections.canonical.maas.plugins.module_utils.client import Response

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_to_ansible(self):
        config = MaasServerConfig(**get_config())

        ansible_dict = get_config()

        results = config.to_ansible()
        assert results == ansible_dict


class TestGet:
    def test_get_by_name(self, create_module, mocker, client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                **get_config(),
            )
        )

        client.get.return_value = Response(200, b"true")

        assert MaasServerConfig.get_by_name(module, client) == MaasServerConfig(
            **get_config()
        )


def get_config():
    return dict(
        name="completed_intro",
        value="true",
    )
