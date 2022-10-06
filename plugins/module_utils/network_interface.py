# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from ..module_utils.utils import MaasValueMapper
from ..module_utils import errors


class NetworkInterface(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        name=None, # Only used during create (search query), after name=label_name.
        id=None,
        subnet_cidr=None,
        machine_id=None,
        ip_address=None,
        fabric=None,
        vlan=None,
        label_name=None,
    ):
        self.name = name
        self.id = id
        self.subnet_cidr = subnet_cidr
        self.machine_id = machine_id
        self.ip_address = ip_address
        self.fabric = fabric
        self.vlan = vlan
        self.label_name = label_name

    @classmethod
    def from_ansible(cls, network_interface_dict):
        obj = NetworkInterface()
        obj.name = network_interface_dict.get("name")
        obj.subnet_cidr = network_interface_dict.get("subnet_cidr")
        obj.ip_address = network_interface_dict.get("ip_address")
        obj.fabric = network_interface_dict.get("fabric")
        obj.vlan = network_interface_dict.get("vlan")
        obj.label_name = network_interface_dict.get("label_name")
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = NetworkInterface()
        try:
            obj.name = maas_dict["name"]
            obj.label_name = maas_dict["name"]
            obj.id = maas_dict["id"]
            if maas_dict["discovered"]: # Auto assigned IP
                obj.ip_address = maas_dict["discovered"][0].get("ip_address")
                obj.subnet_cidr = maas_dict["discovered"][0]["subnet"].get("cidr")
                obj.vlan = maas_dict["discovered"][0]["subnet"]["vlan"].get("name")
                obj.fabric = maas_dict["discovered"][0]["subnet"]["vlan"].get("fabric")
            elif len(maas_dict["links"]) > 0: # Static IP
                obj.ip_address = maas_dict["links"][0].get("ip_address")
                obj.subnet_cidr = maas_dict["links"][0]["subnet"].get("cidr")
                obj.vlan = maas_dict["links"][0]["subnet"]["vlan"].get("name")
                obj.fabric = maas_dict["links"][0]["subnet"]["vlan"].get("fabric")
            else: # interface auto generated
                obj.ip_address = maas_dict.get("ip_address")
                obj.subnet_cidr = maas_dict.get("cidr")
                obj.vlan = maas_dict["vlan"].get("name")
                obj.fabric = maas_dict["vlan"].get("fabric")
            obj.machine_id = maas_dict["system_id"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return dict(
            id = self.id,
            name = self.name,
            subnet_cidr = self.subnet_cidr,
            ip_address = self.ip_address,
            fabric = self.fabric,
            vlan = self.vlan,
            label_name = self.label_name
        )

    def to_ansible(self):
        return dict(
            id = self.id,
            name = self.name,
            subnet_cidr = self.subnet_cidr,
            ip_address = self.ip_address,
            fabric = self.fabric,
            vlan = self.vlan
        )
