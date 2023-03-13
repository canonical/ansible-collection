# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
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
from .client import Client


MAAS_RESOURCE = "/api/2.0/static-routes"


class StaticRoute(MaasValueMapper):
    def __init__(
        self,
        source=None,
        destination=None,
        gateway_ip=None,
        metric=None,
        id=None,
        resource_uri=None,
    ):
        self.source = source
        self.destination = destination
        self.gateway_ip = gateway_ip
        self.metric = metric
        self.id = id
        self.resource_uri = resource_uri

    @classmethod
    def get_by_spec(cls, module, client: Client, must_exist=False):
        rest_client = RestClient(client=client)
        fields = {"source", "destination"}
        ansible_maas_map_dict = {k: k for k in fields}
        query = get_query(
            module,
            *fields,
            ansible_maas_map=ansible_maas_map_dict,
        )
        maas_dict = rest_client.get_record(
            f"{MAAS_RESOURCE}/", query, must_exist=must_exist
        )
        if maas_dict:
            static_route = cls.from_maas(maas_dict)
            return static_route

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.source = maas_dict["source"]
            obj.destination = maas_dict["destination"]
            obj.gateway_ip = maas_dict["gateway_ip"]
            obj.metric = maas_dict["metric"]
            obj.id = maas_dict["id"]
            obj.resource_uri = maas_dict["resource_uri"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            source=self.source,
            destination=self.destination,
            gateway_ip=self.gateway_ip,
            metric=self.metric,
            id=self.id,
            resource_uri=self.resource_uri,
        )

    def delete(self, module, client):
        rest_client = RestClient(client=client)
        rest_client.delete_record(f"{MAAS_RESOURCE}/{self.id}/", module.check_mode)

    def update(self, module, client, payload):
        rest_client = RestClient(client=client)
        return rest_client.put_record(
            f"{MAAS_RESOURCE}/{self.id}/",
            payload=payload,
            check_mode=module.check_mode,
        ).json

    @classmethod
    def create(cls, client, payload):
        static_route_maas_dict = client.post(
            f"{MAAS_RESOURCE}/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        static_route = cls.from_maas(static_route_maas_dict)
        return static_route

    def __eq__(self, other):
        """One DHCP Snippet is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.source == other.source,
                self.destination == other.destination,
                self.gateway_ip == other.gateway_ip,
                self.metric == other.metric,
                self.id == other.id,
                self.resource_uri == other.resource_uri,
            )
        )
