# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from ..module_utils.utils import (
    get_query,
    MaasValueMapper,
)
from ..module_utils import errors
from ..module_utils.rest_client import RestClient


class VMHost(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        name=None,  # Host name.
        id=None,
    ):
        self.name = name
        self.id = id

    @classmethod
    def get_by_name(cls, module, client, must_exist=False, name_field_ansible="name"):
        rest_client = RestClient(client=client)
        query = get_query(
            module.params,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        maas_dict = rest_client.get_record(
            "/api/2.0/vm-hosts/", query, must_exist=must_exist
        )
        vmhost_from_maas = cls.from_maas(maas_dict)
        return vmhost_from_maas

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = VMHost()
        try:
            obj.name = maas_dict["name"]
            obj.id = maas_dict["id"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return

    def send_compose_request(self, module, client, payload):
        results = client.post(
            f"/api/2.0/vm-hosts/{self.id}/", query={"op": "compose"}, data=payload
        ).json
        return results
