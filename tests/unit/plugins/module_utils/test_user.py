# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.maas.maas.plugins.module_utils.client import Response
from ansible_collections.maas.maas.plugins.module_utils.user import User

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestEq:
    @staticmethod
    def get_user_one():
        return dict(
            name="one",
            email="one.email",
            is_admin=False,
            password="one_password",
        )

    @staticmethod
    def get_user_two():
        return dict(
            name="two",
            email="two.email",
            is_admin=False,
            password="two_password",
        )

    def test_eq_when_are_same(self):
        user_one_dict = self.get_user_one()
        user_two_dict = self.get_user_one()
        user_one_obj = User.from_ansible(user_one_dict)
        user_two_obj = User.from_ansible(user_two_dict)
        assert user_one_obj == user_two_obj

    def test_eq_when_are_not_same(self):
        user_one_dict = self.get_user_one()
        user_two_dict = self.get_user_two()
        user_one_obj = User.from_ansible(user_one_dict)
        user_two_obj = User.from_ansible(user_two_dict)
        assert user_one_obj != user_two_obj


class TestMapper:
    def test_from_ansible_not_admin(self):
        user_dict = dict(
            name="name", password="password", email="email", is_admin=False
        )
        user_obj = User.from_ansible(user_dict)
        assert (
            user_obj.name == "name"
            and user_obj.password == "password"
            and user_obj.email == "email"
            and user_obj.is_admin is False
        )

    def test_from_ansible_admin(self):
        user_dict = dict(
            name="name", password="password", email="email", is_admin=True
        )
        user_obj = User.from_ansible(user_dict)
        assert (
            user_obj.name == "name"
            and user_obj.password == "password"
            and user_obj.email == "email"
            and user_obj.is_admin is True
        )

    def test_from_maas_superuser(self):
        user_dict = dict(
            username="name", is_local=False, is_superuser=True, email="email"
        )
        user_obj = User.from_maas(user_dict)
        assert (
            user_obj.name == "name"
            and user_obj.password is None
            and user_obj.email == "email"
            and user_obj.is_admin is True
        )

    def test_from_maas_not_superuser(self):
        user_dict = dict(
            username="name", is_local=False, is_superuser=False, email="email"
        )
        user_obj = User.from_maas(user_dict)
        assert (
            user_obj.name == "name"
            and user_obj.password is None
            and user_obj.email == "email"
            and user_obj.is_admin is False
        )

    def test_to_ansible_admin(self):
        user_dict = dict(
            username="name", is_local=False, is_superuser=True, email="email"
        )
        user_obj = User.from_maas(user_dict)
        user_to_ansible = user_obj.to_ansible()
        assert user_to_ansible == dict(
            name="name", is_local=False, is_admin=True, email="email"
        )

    def test_to_ansible_not_admin(self):
        user_dict = dict(
            username="name", is_local=False, is_superuser=False, email="email"
        )
        user_obj = User.from_maas(user_dict)
        user_to_ansible = user_obj.to_ansible()
        assert user_to_ansible == dict(
            name="name", is_local=False, is_admin=False, email="email"
        )

    def test_to_maas_not_admin(self):
        user_dict = dict(
            name="name", password="password", is_admin=False, email="email"
        )
        user_obj = User.from_ansible(user_dict)
        user_to_maas = user_obj.to_maas()
        assert user_to_maas == dict(
            username="name",
            email="email",
            is_superuser=False,
            password="password",
        )

    def test_to_maas_admin(self):
        user_dict = dict(
            name="name", password="password", is_admin=True, email="email"
        )
        user_obj = User.from_ansible(user_dict)
        user_to_maas = user_obj.to_maas()
        assert user_to_maas == dict(
            username="name",
            email="email",
            is_superuser=True,
            password="password",
        )


class TestSendRequestAndPayload:
    def test_payload_for_create_when_is_superuser(self):
        user_dict = dict(
            name="name", password="password", email="email", is_admin=True
        )
        user_obj = User.from_ansible(user_dict)
        results = user_obj.payload_for_create()
        assert results == dict(
            username="name", password="password", email="email", is_superuser=1
        )

    def test_payload_for_create_when_is_not_superuser(self):
        user_dict = dict(
            name="name", password="password", email="email", is_admin=False
        )
        user_obj = User.from_ansible(user_dict)
        results = user_obj.payload_for_create()
        assert results == dict(
            username="name", password="password", email="email", is_superuser=0
        )

    def test_send_create_request(self, client):
        user_dict = dict(
            name="name", password="password", email="email", is_admin=False
        )
        user_obj = User.from_ansible(user_dict)
        client.post.return_value = Response(200, '{"username": "name"}')
        results = user_obj.send_create_request(
            client, user_obj.payload_for_create()
        )
        assert results == {"username": "name"}

    def test_send_delete_request(self, client):
        user_dict = dict(
            name="name", password="password", email="email", is_admin=False
        )
        user_obj = User.from_ansible(user_dict)
        client.delete.return_value = None
        results = user_obj.send_delete_request(client)
        assert results is None
