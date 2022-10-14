# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.vmhost import VMHost
from ansible_collections.canonical.maas.plugins.module_utils.client import (
    Response,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestSendComposeRequest:
    @staticmethod
    def _get_empty_host_dict():
        return dict(
            name="test_name",
            id="1234",
            cpu_over_commit_ratio=1,
            memory_over_commit_ratio=2,
            default_macvlan_mode="bridge",
            pool="my-pool",
            zone="my-zone",
            tags="my-tag",
        )

    def test_send_compose_request(self, client, mocker):
        module = ""
        payload = ""
        vmhost_dict = self._get_empty_host_dict()
        vmhost_obj = VMHost.from_maas(vmhost_dict)
        client.post.return_value = Response(
            200, '{"system_id":"123", "resource_uri":""}'
        )
        results = vmhost_obj.send_compose_request(module, client, payload)
        assert results == {"system_id": "123", "resource_uri": ""}


class TestMapper:
    @staticmethod
    def _get_host():
        return dict(
            name="test_host",
            id=123,
            cpu_over_commit_ratio=1,
            memory_over_commit_ratio=2,
            default_macvlan_mode="bridge",
            pool="my-pool",
            zone="my-zone",
            tags="my-tag",
        )

    def test_from_maas(self):
        maas_host_dict = self._get_host()
        host = VMHost(
            maas_host_dict["name"],
            maas_host_dict["id"],
            maas_host_dict["cpu_over_commit_ratio"],
            maas_host_dict["memory_over_commit_ratio"],
            maas_host_dict["default_macvlan_mode"],
            maas_host_dict["pool"],
            maas_host_dict["zone"],
            maas_host_dict["tags"],
        )
        results = VMHost.from_maas(maas_host_dict)
        assert results.name == host.name
        assert results.cpu_over_commit_ratio == host.cpu_over_commit_ratio
        assert results.memory_over_commit_ratio == host.memory_over_commit_ratio
        assert results.default_macvlan_mode == host.default_macvlan_mode
        assert results.id == host.id
        assert results.pool == host.pool
        assert results.zone == host.zone
        assert results.tags == host.tags
