# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import (
    vm_host_machine,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://my.host.name", client_key="client key", token_key="token key", token_secret="token secret"
            ),
            state="ready",
            vm_host="this_host"
        )

        success, results = run_main(vm_host_machine, params)
        print(success, results)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://my.host.name", client_key="client key", token_key="token key", token_secret="token secret"
            ),
            state="ready",
            vm_host="this_host",
            cores=3,
            memory=2048,
            network_interfaces={"name":"my_interface", "subnet_cidr":"10.10.10.0/24"},
            storage_disks=[{"size_gigabytes":15},{"size_gigabytes":10}],
        )

        success, results = run_main(vm_host_machine, params)
        print(success, results)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }

class TestRun:
    def test_run(self):
        pass
