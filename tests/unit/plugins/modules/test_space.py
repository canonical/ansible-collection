# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.maas.maas.plugins.module_utils.space import Space
from ansible_collections.maas.maas.plugins.modules import space

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
            name="my-space",
            state="present",
            new_name="updated-space",
            description="Updated Network Space",
        )

        success, result = run_main(space, params)

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

        success, result = run_main(space, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(space)

        assert success is False
        assert "missing required arguments: state" in result["msg"]


class TestDataForCreateSpace:
    def test_data_for_create_space(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                name="my-space",
                new_name=None,
                description=None,
            )
        )
        data = space.data_for_create_space(module)

        assert data == dict(name="my-space")


class TestDataForUpdateSpace:
    def test_data_for_update_space(self, create_module):
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
        old_space = Space(name="old-name")
        data = space.data_for_update_space(module, old_space)

        assert data == dict(
            description="description",
            name="new-name",
        )
