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
        pinned_cores=None,
        zone=None,
        pool=None,
        domain=None,
        network_interfaces=[],
        disks=[],
        status=None,
        osystem=None,
        distro_series=None,
    ):
        self.hostname = hostname
        self.id = id
        self.memory = memory
        self.cores = cores
        self.network_interfaces = network_interfaces
        self.disks = disks
        self.pinned_cores = pinned_cores
        self.zone = zone
        self.pool = pool
        self.domain = domain
        self.status = status
        self.osystem = osystem
        self.distro_series = distro_series

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
            "/api/2.0/machines/",
            query,
            must_exist=must_exist,
        )
        if maas_dict:
            machine_from_maas = cls.from_maas(maas_dict)
            return machine_from_maas

    @classmethod
    def get_by_id(cls, id, client):
        # rest_client.get_record doesn't work here
        # in case if machine doesn't exist .json throws error: MaasError("Received invalid JSON response: {0}".format(self.data))
        try:
            maas_dict = client.get(f"/api/2.0/machines/{id}/").json
            vmhost_from_maas = cls.from_maas(maas_dict)
            return vmhost_from_maas
        except errors.MaasError:
            raise errors.MachineNotFound(id)

    @classmethod
    def from_ansible(cls, module):
        obj = Machine()
        obj.hostname = module.params.get("hostname")
        obj.cores = module.params.get("cores")
        obj.memory = module.params.get("memory")
        obj.domain = module.params.get("domain")
        obj.pinned_cores = module.params.get("pinned_cores")
        obj.pool = module.params.get("pool")
        obj.zone = module.params.get("zone")
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
            obj.domain = maas_dict["domain"]["id"]
            obj.zone = maas_dict["zone"]["id"]
            obj.pool = maas_dict["pool"]["id"]
            obj.network_interfaces = [
                NetworkInterface.from_maas(net_interface)
                for net_interface in maas_dict["interface_set"] or []
            ]
            obj.disks = [
                Disk.from_maas(disk) for disk in maas_dict["blockdevice_set"] or []
            ]
            obj.status = maas_dict["status_name"]
            obj.osystem = maas_dict["osystem"]
            obj.distro_series = maas_dict["distro_series"]
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
        if self.pinned_cores:
            to_maas_dict["pinned_cores"] = self.pinned_cores
        if self.zone:
            to_maas_dict["zone"] = self.zone
        if self.pool:
            to_maas_dict["pool"] = self.pool
        if self.domain:
            to_maas_dict["domain"] = self.domain
        if self.network_interfaces:
            to_maas_dict["interfaces"] = [
                net_interface.to_maas() for net_interface in self.network_interfaces
            ]
        if self.disks:
            to_maas_dict["storage"] = [disk.to_maas() for disk in self.disks]
        return to_maas_dict

    def to_ansible(self):
        return dict(
            hostname = self.hostname,
            id = self.id,
            memory = self.memory,
            cores = self.cores,
            network_interfaces = [
            net_interface.to_ansible() for net_interface in self.network_interfaces
            ],
            storage_disks = [disk.to_ansible() for disk in self.disks],
            status = self.status,
            osystem = self.osystem,
            distro_series = self.distro_series
        )

    def payload_for_compose(self, module):
        payload = self.to_maas()
        if "interfaces" in payload:
            tmp = payload.pop("interfaces")
            for net_interface in tmp:
                payload_string_list = []
                if net_interface.get("subnet_cidr"):
                    payload_string_list.append(
                        f"subnet_cidr={net_interface['subnet_cidr']}"
                    )
                if net_interface.get("ip_address"):
                    payload_string_list.append(f"ip={net_interface['ip_address']}")
                if net_interface.get("fabric"):
                    payload_string_list.append(f"fabric={net_interface['fabric']}")
                if net_interface.get("vlan"):
                    payload_string_list.append(f"vlan={net_interface['vlan']}")
                if net_interface.get("name"):
                    payload_string_list.append(f"name={net_interface['name']}")
                payload[
                    "interfaces"
                ] = f"{net_interface['label_name']}:{','.join(payload_string_list)}"
                break  # Right now, compose only allows for one network interface.
        if "storage" in payload:
            tmp = payload.pop("storage")
            payload["storage"] = ",".join([f"label:{disk['size']}" for disk in tmp])
        return payload

    def __eq__(self, other):
        """One Machine is equal to another if it has ALL attributes exactly the same"""
        return all(
            (
                self.hostname == other.hostname,
                self.id == other.id,
                self.memory == other.memory,
                self.cores == other.cores,
                self.network_interfaces == other.network_interfaces,
                self.disks == other.disks,
                self.status == other.status,
                self.osystem == other.osystem,
                self.distro_series == other.distro_series,
            )
        )
