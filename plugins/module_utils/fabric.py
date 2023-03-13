# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils import errors
from ..module_utils.rest_client import RestClient
from ..module_utils.utils import MaasValueMapper, get_query


class Fabric(MaasValueMapper):
    def __init__(
        self,
        name=None,
        id=None,
        vlans=None,
        resource_uri=None,
        class_type=None,
    ):
        self.name = name
        self.id = id
        self.vlans = vlans
        self.resource_uri = resource_uri
        self.class_type = class_type

    @classmethod
    def get_by_name(
        cls, module, client, must_exist=False, name_field_ansible="name"
    ):
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        fabric_maas_dict = rest_client.get_record(
            "/api/2.0/fabrics/", query, must_exist=must_exist
        )
        if fabric_maas_dict:
            fabric = cls.from_maas(fabric_maas_dict)
            return fabric

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
            obj.class_type = maas_dict["class_type"]
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
            class_type=self.class_type,
        )

    def delete(self, client):
        client.delete(f"/api/2.0/fabrics/{self.id}/")

    def update(self, client, payload):
        return client.put(f"/api/2.0/fabrics/{self.id}/", data=payload).json

    @classmethod
    def create(cls, client, payload):
        fabric_maas_dict = client.post(
            "/api/2.0/fabrics/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        fabric = cls.from_maas(fabric_maas_dict)
        return fabric

    def __eq__(self, other):
        """One fabric is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.id == other.id,
                self.vlans == other.vlans,
                self.resource_uri == other.resource_uri,
                self.class_type == other.class_type,
            )
        )
