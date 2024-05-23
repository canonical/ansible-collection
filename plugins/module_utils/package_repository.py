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


class PackageRepository(MaasValueMapper):
    def __init__(
        self,
        id=None,
        name=None,
        url=None,
        distributions=None,
        disabled_pockets=None,
        disabled_components=None,
        disable_sources=None,
        components=None,
        arches=None,
        key=None,
        enabled=None,
        resource_uri=None,
    ):
        self.id = id
        self.name = name
        self.url = url
        self.distributions = distributions
        self.disabled_pockets = disabled_pockets
        self.disabled_components = disabled_components
        self.disable_sources = disable_sources
        self.components = components
        self.arches = arches
        self.key = key
        self.enabled = enabled
        self.resource_uri = resource_uri

    @classmethod
    def get_by_name(
        cls,
        module,
        client: Client,
        must_exist=False,
        name_field_ansible="name",
    ):
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        maas_dict = rest_client.get_record(
            "/api/2.0/package-repositories/", query, must_exist=must_exist
        )
        if maas_dict:
            package_repository_from_maas = cls.from_maas(maas_dict)
            return package_repository_from_maas

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.id = maas_dict["id"]
            obj.name = maas_dict["name"]
            obj.url = maas_dict["url"]
            obj.distributions = maas_dict["distributions"]
            obj.disabled_pockets = maas_dict["disabled_pockets"]
            obj.disabled_components = maas_dict["disabled_components"]
            obj.disable_sources = maas_dict["disable_sources"]
            obj.components = maas_dict["components"]
            obj.arches = maas_dict["arches"]
            obj.key = maas_dict["key"]
            obj.enabled = maas_dict["enabled"]
            obj.resource_uri = maas_dict["resource_uri"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            id=self.id,
            name=self.name,
            url=self.url,
            distributions=self.distributions,
            disabled_pockets=self.disabled_pockets,
            disabled_components=self.disabled_components,
            disable_sources=self.disable_sources,
            components=self.components,
            arches=self.arches,
            key=self.key,
            enabled=self.enabled,
            resource_uri=self.resource_uri,
        )

    def delete(self, client):
        client.delete(f"/api/2.0/package-repositories/{self.id}/")

    def update(self, client, payload):
        return client.put(
            f"/api/2.0/package-repositories/{self.id}/", data=payload
        ).json

    @classmethod
    def create(cls, client, payload):
        package_repository_maas_dict = client.post(
            "/api/2.0/package-repositories/",
            data=payload,
            timeout=60,
        ).json
        package_repository = cls.from_maas(package_repository_maas_dict)
        return package_repository

    def __eq__(self, other):
        return all(
            (
                self.id == other.id,
                self.name == other.name,
                self.url == other.url,
                self.distributions == other.distributions,
                self.disabled_pockets == other.disabled_pockets,
                self.disabled_components == other.disabled_components,
                self.disable_sources == other.disable_sources,
                self.components == other.components,
                self.arches == other.arches,
                self.key == other.key,
                self.enabled == other.enabled,
                self.resource_uri == other.resource_uri,
            )
        )
