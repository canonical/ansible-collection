# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.user import User
from ansible_collections.canonical.maas.plugins.modules import user

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


class TestRun:
    def test_run_when_present(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                name="name",
                email="email",
                password="password",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.user.ensure_present"
        ).return_value = (False, {}, {})
        results = user.run(module, client)
        assert results == (False, {}, {})

    def test_run_when_absent(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                name="name",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.user.ensure_absent"
        ).return_value = (False, {}, {})
        results = user.run(module, client)
        assert results == (False, {}, {})


class TestEnsurePresent:
    def test_ensure_present_when_creating_new_user_no_admin(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                name="name",
                email="email",
                password="password",
            )
        )
        user_obj = User.from_ansible(
            dict(
                name="name", email="email", password="password", is_admin=False
            )
        )
        after = user_obj.to_ansible()
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.get_by_name"
        ).side_effect = [None, user_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.payload_for_create"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.send_create_request"
        ).return_value = None
        results = user.ensure_present(module, client)
        assert results == (True, after, dict(before=None, after=after))

    def test_ensure_present_when_creating_new_user_admin(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                name="name",
                email="email",
                password="password",
                is_admin=True,
            )
        )
        user_obj = User.from_ansible(
            dict(
                name="name", email="email", password="password", is_admin=True
            )
        )
        after = user_obj.to_ansible()
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.get_by_name"
        ).side_effect = [None, user_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.payload_for_create"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.send_create_request"
        ).return_value = None
        results = user.ensure_present(module, client)
        assert results == (True, after, dict(before=None, after=after))

    def test_ensure_present_when_user_already_exists(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                name="name",
                email="email",
                password="password",
                is_admin=True,
            )
        )
        user_obj = User.from_ansible(
            dict(
                name="name", email="email", password="password", is_admin=True
            )
        )
        after = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.get_by_name"
        ).side_effect = [user_obj]
        results = user.ensure_present(module, client)
        assert results == (False, after, dict(before=None, after=after))


class TestEnsureAbsent:
    def test_ensure_absent_when_deleting_user(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                name="name",
            )
        )
        user_obj = User.from_ansible(
            dict(
                name="name", email="email", password="password", is_admin=True
            )
        )
        after = None
        before = user_obj.to_ansible()
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.get_by_name"
        ).side_effect = [user_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.send_delete_request"
        ).return_value = None
        results = user.ensure_absent(module, client)
        assert results == (True, after, dict(before=before, after=after))

    def test_ensure_absent_when_user_already_deleted(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                name="name",
            )
        )
        after = None
        before = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.user.User.get_by_name"
        ).side_effect = [None]
        results = user.ensure_absent(module, client)
        assert results == (False, after, dict(before=before, after=after))
