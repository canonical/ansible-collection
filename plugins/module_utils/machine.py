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
from ..module_utils.network_interface import NetworkInterface
from ..module_utils.disk import Disk


class Machine(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        hostname=None,  # Machine name.
        id=None,
        memory=None,
        cores=None,
        network_interfaces=[],
        disks=[],
    ):
        self.hostname = hostname
        self.id = id
        self.memory = memory
        self.cores = cores
        self.network_interfaces = network_interfaces
        self.disks = disks

    @classmethod
    def get_by_name(
        cls, module, client, must_exist=False, name_field_ansible="hostname"
    ):
        # Returns machine object or None
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "hostname"},
        )
        maas_dict = rest_client.get_record(
            "/api/2.0/machines/", query, must_exist=must_exist
        )
        if maas_dict:
            machine_from_maas = cls.from_maas(maas_dict)
            return machine_from_maas

    @classmethod
    def get_by_id(cls, id, client, must_exist=False):
        maas_dict = client.get(f"/api/2.0/machines/{id}/").json
        vmhost_from_maas = cls.from_maas(maas_dict)
        return vmhost_from_maas

    @classmethod
    def from_ansible(cls, module):
        obj = Machine()
        obj.hostname = module.params.get("hostname")
        obj.cores = module.params.get("cores")
        obj.memory = module.params.get("memory")
        obj.network_interfaces = [
            NetworkInterface.from_ansible(net_interface)
            for net_interface in module.params.get("network_interfaces") or []
        ]
        obj.disks = [
            Disk.from_ansible(disk) for disk in module.params.get("storage_disks") or []
        ]
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = Machine()
        try:
            obj.hostname = maas_dict["hostname"]
            obj.id = maas_dict["system_id"]
            obj.memory = maas_dict["memory"]
            obj.cores = maas_dict["cpu_count"]
            obj.network_interfaces = [
                NetworkInterface.from_maas(net_interface)
                for net_interface in maas_dict["interface_set"] or []
            ]
            obj.disks = [
                Disk.from_maas(disk) for disk in maas_dict["blockdevice_set"] or []
            ]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        to_maas_dict = {}
        if self.hostname:
            to_maas_dict["hostname"] = self.hostname
        if self.id:
            to_maas_dict["id"] = self.id
        if self.memory:
            to_maas_dict["memory"] = self.memory
        if self.cores:
            to_maas_dict["cores"] = self.cores
        if self.network_interfaces:
            to_maas_dict["interfaces"] = [
                net_interface.to_maas() for net_interface in self.network_interfaces
            ]
        if self.disks:
            to_maas_dict["storage"] = [disk.to_maas() for disk in self.disks]
        return to_maas_dict

    def to_ansible(self):
        to_ansible_dict = {}
        if self.hostname:
            to_ansible_dict["hostname"] = self.hostname
        if self.id:
            to_ansible_dict["id"] = self.id
        if self.memory:
            to_ansible_dict["memory"] = self.memory
        if self.cores:
            to_ansible_dict["cores"] = self.cores
        if self.network_interfaces:
            to_ansible_dict["network_interfaces"] = [
                net_interface.to_ansible() for net_interface in self.network_interfaces
            ]
        if self.disks:
            to_ansible_dict["storage_disks"] = [
                disk.to_ansible() for disk in self.disks
            ]
        return to_ansible_dict

    def payload_for_compose(self, module):
        payload = self.to_maas()
        if "interfaces" in payload:
            tmp = payload.pop("interfaces")
            for net_interface in tmp:
                payload[
                    "interfaces"
                ] = f"{net_interface['name']}:subnet_cidr={net_interface['subnet_cidr']}"
                break  # Right now, compose only allows for one network interface.
        if "storage" in payload:
            tmp = payload.pop("storage")
            payload["storage"] = ",".join([f"label:{disk['size']}" for disk in tmp])
        return payload

    def find_nic_by_mac(self, mac):
        # returns nic object or None
        for nic_obj in self.network_interfaces:
            if mac == nic_obj.mac_address:
                return nic_obj
