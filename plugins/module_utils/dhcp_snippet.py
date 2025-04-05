# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
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
from ..module_utils.client import Client


MAAS_DHCP_SNIPPETS_URL = "/api/2.0/dhcp-snippets"


class DhcpSnippet(MaasValueMapper):
    def __init__(
        self,
        name=None,
        description=None,
        enabled=None,
        subnet=None,
        global_snippet=None,
        value=None,
        history=None,
        id=None,
        resource_uri=None,
    ):
        self.name = name
        self.description = description
        self.enabled = enabled
        self.subnet = subnet
        self.global_snippet = global_snippet
        self.value = value
        self.history = history
        self.id = id
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
            f"{MAAS_DHCP_SNIPPETS_URL}/", query, must_exist=must_exist
        )
        if maas_dict:
            dhcp_snippet = cls.from_maas(maas_dict)
            return dhcp_snippet

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.name = maas_dict["name"]
            obj.description = maas_dict["description"]
            obj.enabled = maas_dict["enabled"]
            obj.subnet = maas_dict["subnet"]
            obj.global_snippet = maas_dict["global_snippet"]
            obj.value = maas_dict["value"]
            obj.history = maas_dict["history"]
            obj.id = maas_dict["id"]
            obj.resource_uri = maas_dict["resource_uri"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            name=self.name,
            description=self.description,
            enabled=self.enabled,
            subnet=self.subnet,
            global_snippet=self.global_snippet,
            value=self.value,
            history=self.history,
            id=self.id,
            resource_uri=self.resource_uri,
        )

    def delete(self, module, client):
        rest_client = RestClient(client=client)
        rest_client.delete_record(
            f"{MAAS_DHCP_SNIPPETS_URL}/{self.id}/", module.check_mode
        )

    def update(self, module, client, payload):
        rest_client = RestClient(client=client)
        return rest_client.put_record(
            f"{MAAS_DHCP_SNIPPETS_URL}/{self.id}/",
            payload=payload,
            check_mode=module.check_mode,
        ).json

    @classmethod
    def create(cls, client, payload):
        dhcp_snippet_maas_dict = client.post(
            f"{MAAS_DHCP_SNIPPETS_URL}/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        dhcp_snippet = cls.from_maas(dhcp_snippet_maas_dict)
        return dhcp_snippet

    def __eq__(self, other):
        """One DHCP Snippet is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.description == other.description,
                self.enabled == other.enabled,
                self.subnet == other.subnet,
                self.global_snippet == other.global_snippet,
                self.value == other.value,
                self.id == other.id,
                self.resource_uri == other.resource_uri,
            )
        )
