# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from distutils.log import error
from ..module_utils.utils import (
    get_query,
    Mapper,
)
from ..module_utils import errors
from ..module_utils.rest_client import RestClient

class Machine(Mapper):
    def __init__(
        # Add more values as needed.
        self,
        hostname=None, # Machine name.
        id=None,
        memory=None,
        cores=None,
    ):
        self.hostname = hostname
        self.id = id
        self.memory = memory
        self.cores = cores

    def payload_for_compose(self, module):
        payload = self.to_mass()
        return payload

    @classmethod
    def get_by_name(cls, module, client, must_exist=False, name_field_ansible="name"):
        rest_client = RestClient(client=client)
        query = get_query(
            module.params, name_field_ansible, ansible_maas_map={name_field_ansible: "hostname"}
        )
        maas_dict = rest_client.get_record(
            "/api/2.0/machines/", query, must_exist=must_exist
        )
        vmhost_from_maas = cls.from_maas(maas_dict)
        return vmhost_from_maas

    @classmethod
    def get_by_id(cls, id, client, must_exist=False):
        maas_dict = client.get(f"/api/2.0/machines/{id}/").json
        vmhost_from_maas = cls.from_maas(maas_dict)
        return vmhost_from_maas

    @classmethod
    def from_ansible(cls, ansible_dict):
        obj = Machine()
        obj.hostname = ansible_dict.get("name") # Maybe change to vm_name or machine_name
        obj.cores = ansible_dict.get("cores")
        obj.memory = ansible_dict.get("memory")
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = Machine()
        try:
            obj.hostname = maas_dict["hostname"]
            obj.id = maas_dict["system_id"]
            obj.memory = maas_dict["memory"]
            obj.cores = maas_dict["cpu_count"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_mass(self):
        to_mass_dict = {}
        if self.hostname:
            to_mass_dict["hostname"] = self.hostname
        if self.id:
            to_mass_dict["id"] = self.id
        if self.memory:
            to_mass_dict["memory"] = self.memory
        if self.cores:
            to_mass_dict["cores"] = self.cores
        return to_mass_dict

    def to_ansible(self):
        to_ansible_dict = {}
        if self.hostname:
            to_ansible_dict["name"] = self.hostname
        if self.id:
            to_ansible_dict["id"] = self.id
        if self.memory:
            to_ansible_dict["memory"] = self.memory
        if self.cores:
            to_ansible_dict["cores"] = self.cores
        return to_ansible_dict
