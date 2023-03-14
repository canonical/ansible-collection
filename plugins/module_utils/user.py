# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils import errors
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import MaasValueMapper, get_query

__metaclass__ = type


class User(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        is_admin=None,
        name=None,
        email=None,
        is_local=None,
        password=None,
    ):
        self.is_admin = is_admin
        self.name = name
        self.email = email
        self.is_local = is_local
        self.password = password

    def __eq__(self, other):
        return self.to_ansible() == other.to_ansible()

    @classmethod
    def from_ansible(cls, module):
        obj = User()
        obj.name = module.get("name")
        obj.email = module.get("email")
        obj.is_admin = module.get("is_admin")
        obj.password = module.get("password")
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = User()
        try:
            obj.is_admin = maas_dict["is_superuser"]
            obj.email = maas_dict["email"]
            obj.name = maas_dict["username"]
            obj.is_local = maas_dict["is_local"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    @classmethod
    def get_by_name(
        cls, module, client, must_exist=False, name_field_ansible="name"
    ):
        # Returns machine object or None
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "username"},
        )
        maas_dict = rest_client.get_record(
            "/api/2.0/users/",
            query,
            must_exist=must_exist,
        )
        if maas_dict:
            user_from_maas = cls.from_maas(maas_dict)
            return user_from_maas

    def to_maas(self):
        to_maas_dict = {}
        if self.name:
            to_maas_dict["username"] = self.name
        if self.email:
            to_maas_dict["email"] = self.email
        if self.is_admin is not None:
            to_maas_dict["is_superuser"] = self.is_admin
        if self.is_local:
            to_maas_dict["is_local"] = self.is_local
        if self.password:
            to_maas_dict["password"] = self.password
        return to_maas_dict

    def to_ansible(self):
        return dict(
            name=self.name,
            email=self.email,
            is_admin=self.is_admin,
            is_local=self.is_local,
        )

    def payload_for_create(self):
        payload = self.to_maas()
        if payload["is_superuser"]:
            payload["is_superuser"] = 1
        else:
            payload["is_superuser"] = 0
        return payload

    def send_create_request(self, client, payload):
        results = client.post(
            "/api/2.0/users/",
            data=payload,
        ).json
        return results

    def send_delete_request(self, client):
        client.delete(f"/api/2.0/users/{self.name}/")
