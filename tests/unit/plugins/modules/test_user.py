# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import (
    user,
)


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params_present(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            name="name",
            password="password",
            email="email",
            state="present",
        )

        success, results = run_main(user, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_minimal_set_of_params_absent(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            name="name",
            state="absent",
        )

        success, results = run_main(user, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params_is_admin(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            state="present",
            name="name",
            password="password",
            email="email",
            is_admin=True,
        )

        success, results = run_main(user, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params_is_not_admin(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            state="present",
            name="name",
            password="password",
            email="email",
            is_admin=False,
        )

        success, results = run_main(user, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }
