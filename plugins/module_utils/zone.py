# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from .utils import (
    get_query,
    MaasValueMapper,
)
from . import errors
from .rest_client import RestClient


MAAS_RESOURCE = "/api/2.0/zones"


class Zone(MaasValueMapper):
    def __init__(
        self,
        name=None, # required
        description=None,
        resource_uri=None,
    ):
        self.name = name
        self.description = description
        self.resource_uri = resource_uri

    @classmethod
    def get_by_name(cls, module, client, must_exist=False, name_field_ansible="name"):
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        zone_maas_dict = rest_client.get_record(
            "/api/2.0/zones/", query, must_exist=must_exist
        )
        if zone_maas_dict:
            zone = cls.from_maas(zone_maas_dict)
            return zone
    
    @classmethod
    def from_ansible(cls, module):
        return
    
    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.name = maas_dict["name"]
            obj.id = maas_dict["id"]
            obj.resource_uri = maas_dict["resource_uri"]
            obj.description = maas_dict["description"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            name=self.name,
            id=self.id,
            description=self.description,
            resource_uri=self.resource_uri,
        )

    def delete(self, client):
        client.delete(f"/api/2.0/zones/{self.name}/")

    def update(self, client, payload):
        return client.put(f"/api/2.0/zones/{self.name}/", data=payload).json

    @classmethod
    def create(cls, client, payload):
        zone_maas_dict = client.post(
            "/api/2.0/zones/",
            data=payload,
        ).json
        zone = cls.from_maas(zone_maas_dict)
        return zone

    def __eq__(self, other):
        """One zone is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.id == other.id,
                self.description == other.description,
            )
        )

