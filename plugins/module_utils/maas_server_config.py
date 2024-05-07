# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from .utils import MaasValueMapper
from .errors import MissingValueMAAS
from .client import Client


MAAS_RESOURCE = "/api/2.0/maas"


class MaasServerConfig(MaasValueMapper):
    def __init__(
        self,
        name=None,
        value=None,
    ):
        self.name = name
        self.value = value

    @classmethod
    def get_by_name(cls, module, client: Client):
        query = {"op": "get_config", "name": module.params["name"]}
        response = client.get(f"{MAAS_RESOURCE}/", query)
        if response:
            return MaasServerConfig(
                module.params["name"], response.data.decode("utf-8").strip('"')
            )

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        return

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            name=self.name,
            value=self.value,
        )

    def update(self, module, client: Client, payload):
        response = client.post(f"{MAAS_RESOURCE}/", payload, {"op": "set_config"})

        if response.status == 200:
            return self.get_by_name(module, client)
        else:
            raise MissingValueMAAS(module.params["name"])

    def __eq__(self, other):
        """One configuration item is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.value == other.value,
            )
        )
