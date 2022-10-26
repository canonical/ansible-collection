# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import fabric
from ansible_collections.canonical.maas.plugins.module_utils.fabric import Fabric

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
            name="my-fabric",
            state="present",
            new_name="updated-fabric",
            description="Updated Network Fabric",
        )

        success, result = run_main(fabric, params)

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

        success, result = run_main(fabric, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(fabric)

        assert success is False
        assert "missing required arguments: state" in result["msg"]


class TestDataForCreateFabric:
    def test_data_for_create_fabric(self, create_module):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                name="my-fabric",
                new_name=None,
                description=None,
                class_type=None,
            )
        )
        data = fabric.data_for_create_fabric(module)

        assert data == dict(name="my-fabric")


class TestDataForUpdateFabric:
    def test_data_for_update_fabric(self, create_module):
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
                class_type="class_type",
            ),
        )
        old_fabric = Fabric(name="old-name")
        data = fabric.data_for_update_fabric(module, old_fabric)

        assert data == dict(
            description="description",
            name="new-name",
            class_type="class_type",
        )
