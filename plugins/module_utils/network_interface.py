# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
from ..module_utils.utils import MaasValueMapper
from ..module_utils import errors
from ..module_utils.utils import is_superset, filter_dict


class NetworkInterface(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        name=None,  # Only used during create (search query), after name=label_name.
        id=None,
        subnet_cidr=None,
        machine_id=None,
        mac_address=None,
        vlan=None,
        mtu=None,
        tags=None,
        ip_address=None,
        fabric=None,
        label_name=None,
    ):
        self.name = name
        self.id = id
        self.subnet_cidr = subnet_cidr
        self.machine_id = machine_id
        self.mac_address = mac_address
        self.vlan = vlan
        self.mtu = mtu
        self.tags = tags
        self.ip_address = ip_address
        self.fabric = fabric
        self.vlan = vlan
        self.label_name = label_name

    def __eq__(self, other):
        return self.to_ansible() == other.to_ansible()

    @classmethod
    def from_ansible(cls, network_interface_dict):
        obj = NetworkInterface()
        obj.name = network_interface_dict.get("name")
        obj.subnet_cidr = network_interface_dict.get("subnet_cidr")
        obj.ip_address = network_interface_dict.get("ip_address")
        obj.fabric = network_interface_dict.get("fabric")
        obj.vlan = network_interface_dict.get("vlan")
        obj.label_name = network_interface_dict.get("label_name")
        obj.mtu = network_interface_dict.get("mtu")
        obj.tags = network_interface_dict.get("tags", [])
        obj.mac_address = network_interface_dict.get("mac_address")
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = NetworkInterface()
        try:
            obj.name = maas_dict["name"]
            obj.label_name = maas_dict["name"]
            obj.id = maas_dict["id"]
            if maas_dict.get("discovered"):  # Auto assigned IP
                obj.ip_address = maas_dict["discovered"][0].get("ip_address")
                obj.subnet_cidr = maas_dict["discovered"][0]["subnet"].get("cidr")
                obj.vlan = maas_dict["discovered"][0]["subnet"]["vlan"].get("name")
                obj.fabric = maas_dict["discovered"][0]["subnet"]["vlan"].get("fabric")
            elif maas_dict.get("links") and len(maas_dict["links"]) > 0:  # Static IP
                obj.ip_address = maas_dict["links"][0].get("ip_address")
                obj.subnet_cidr = maas_dict["links"][0]["subnet"].get("cidr")
                obj.vlan = maas_dict["links"][0]["subnet"]["vlan"].get("name")
                obj.fabric = maas_dict["links"][0]["subnet"]["vlan"].get("fabric")
            else:  # interface auto generated
                # TODO: DOMEN get mac address from maas_dict
                raise errors.MaasError(maas_dict)
                obj.ip_address = maas_dict.get("ip_address")
                obj.subnet_cidr = maas_dict.get("cidr")
                obj.vlan = maas_dict["vlan"].get("name") if maas_dict["vlan"] else None
                obj.fabric = maas_dict["vlan"].get("fabric") if maas_dict["vlan"] else None
            obj.machine_id = maas_dict["system_id"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        to_maas_dict = {}
        if self.id:
            to_maas_dict["id"] = self.id
        if self.name:
            to_maas_dict["name"] = self.name
        if self.subnet_cidr:
            to_maas_dict["subnet_cidr"] = self.subnet_cidr
        if self.mac_address:
            to_maas_dict["mac_address"] = self.mac_address
        if self.vlan:
            to_maas_dict["vlan"] = self.vlan
        if self.mtu:
            to_maas_dict["mtu"] = self.mtu
        if self.tags:
            to_maas_dict["tags"] = self.tags
        if self.ip_address:
            to_maas_dict["ip_address"] = self.ip_address
        if self.fabric:
            to_maas_dict["fabric"] = self.fabric
        if self.vlan:
            to_maas_dict["vlan"] = self.vlan
        if self.label_name:
            to_maas_dict["label_name"] = self.label_name
        return to_maas_dict

    def to_ansible(self):
        return dict(
            id=self.id,
            name=self.name,
            subnet_cidr=self.subnet_cidr,
            ip_address=self.ip_address,
            fabric=self.fabric,
            vlan=self.vlan,
            mac=self.mac_address,
            mtu=self.mtu,
            tags=self.tags,
        )

    def needs_update(self, new_nic):
        new_nic_dict = new_nic.to_maas()
        if is_superset(self.to_maas(), filter_dict(new_nic_dict, new_nic_dict.keys())):
            return False
        return True

    def payload_for_update(self):
        return

    def send_update_request(self, payload):
        return

    def payload_for_create(self):
        payload = self.to_maas()
        return payload

    def send_create_request(self, client, machine_obj ,payload):
        results = client.post(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/", query={"op": "create_physical"}, data=payload
        ).json
        return results
