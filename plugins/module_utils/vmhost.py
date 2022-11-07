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


class VMHost(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        name=None,  # Host name.
        id=None,
        cpu_over_commit_ratio=None,
        memory_over_commit_ratio=None,
        default_macvlan_mode=None,
        pool=None,
        zone=None,
        tags=None,
    ):
        self.name = name
        self.id = id
        self.cpu_over_commit_ratio = cpu_over_commit_ratio
        self.memory_over_commit_ratio = memory_over_commit_ratio
        self.default_macvlan_mode = default_macvlan_mode
        self.pool = pool
        self.zone = zone
        self.tags = tags

    @classmethod
    def get_by_name(cls, module, client, must_exist=False, name_field_ansible="name"):
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        maas_dict = rest_client.get_record(
            "/api/2.0/vm-hosts/", query, must_exist=must_exist
        )
        if maas_dict:
            vmhost_from_maas = cls.from_maas(maas_dict)
            return vmhost_from_maas

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.name = maas_dict["name"]
            obj.id = maas_dict["id"]
            obj.cpu_over_commit_ratio = maas_dict["cpu_over_commit_ratio"]
            obj.memory_over_commit_ratio = maas_dict["memory_over_commit_ratio"]
            obj.default_macvlan_mode = maas_dict["default_macvlan_mode"]
            obj.tags = maas_dict["tags"]
            obj.zone = maas_dict["zone"]
            obj.pool = maas_dict["pool"]
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

    def delete(self, client):
        client.delete(f"/api/2.0/vm-hosts/{self.id}/")

    # Used because we don't store all the data in an object
    def get(self, client):
        return client.get(f"/api/2.0/vm-hosts/{self.id}/").json

    @classmethod
    def create(cls, client, payload):
        vm_host_maas_dict = client.post(
            "/api/2.0/vm-hosts/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing toimeout from 20s to 60s
        ).json
        vm_host = cls.from_maas(vm_host_maas_dict)
        return vm_host, vm_host_maas_dict

    def update(self, client, payload):
        return client.put(
            f"/api/2.0/vm-hosts/{self.id}/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing toimeout from 20s to 60s
        ).json
