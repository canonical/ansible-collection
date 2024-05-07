# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import maas_server_config
from ansible_collections.canonical.maas.plugins.module_utils.maas_server_config import (
    MaasServerConfig,
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
            name="completed_intro",
            value="true",
        )

        success, result = run_main(maas_server_config, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            name="completed_intro",
        )

        success, result = run_main(maas_server_config, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(maas_server_config)

        assert success is False
        assert "missing required arguments: name" in result["msg"]


class TestDataForUpdateConfig:
    def test_data_for_update_config(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                name="completed_intro",
                value="true",
            )
        )
        old_config = MaasServerConfig(
            name="completed_intro",
            value="false",
        )
        data = maas_server_config.data_for_update_config(module, old_config)

        assert data == dict(name="completed_intro", value="true")
