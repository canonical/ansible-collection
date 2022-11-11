# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import (
    get_query,
    MaasValueMapper,
)
from ..module_utils import errors
from ..module_utils.rest_client import RestClient


class Space(MaasValueMapper):
    def __init__(
        self,
        name=None,
        id=None,
        vlans=None,
        resource_uri=None,
        subnets=None,
    ):
        self.name = name
        self.id = id
        self.vlans = vlans
        self.resource_uri = resource_uri
        self.subnets = subnets

    @classmethod
    def get_by_name(cls, module, client, must_exist=False, name_field_ansible="name"):
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        space_maas_dict = rest_client.get_record(
            "/api/2.0/spaces/", query, must_exist=must_exist
        )
        if space_maas_dict:
            space = cls.from_maas(space_maas_dict)
            return space

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.name = maas_dict["name"]
            obj.id = maas_dict["id"]
            obj.vlans = maas_dict["vlans"]
            obj.resource_uri = maas_dict["resource_uri"]
            obj.subnets = maas_dict["subnets"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            name=self.name,
            id=self.id,
            resource_uri=self.resource_uri,
            vlans=self.vlans,
            subnets=self.subnets,
        )

    def delete(self, client):
        client.delete(f"/api/2.0/spaces/{self.id}/")

    def update(self, client, payload):
        return client.put(f"/api/2.0/spaces/{self.id}/", data=payload).json

    @classmethod
    def create(cls, client, payload):
        space_maas_dict = client.post(
            "/api/2.0/spaces/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        space = cls.from_maas(space_maas_dict)
        return space

    def __eq__(self, other):
        """One space is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.id == other.id,
                self.vlans == other.vlans,
                self.resource_uri == other.resource_uri,
                self.subnets == other.subnets,
            )
        )
