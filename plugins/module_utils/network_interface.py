# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
        obj.mac_address = network_interface_dict.get("mac_address")
        obj.mtu = network_interface_dict.get("mtu")
        obj.tags = network_interface_dict.get("tags", [])
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = NetworkInterface()
        try:
            obj.name = maas_dict["name"]
            obj.label_name = maas_dict["name"]
            obj.id = maas_dict["id"]
            obj.mac_address = maas_dict["mac_address"]
            obj.machine_id = maas_dict["system_id"]
            obj.tags = maas_dict["tags"]
            obj.mtu = maas_dict["effective_mtu"]
            if maas_dict.get("discovered"):  # Auto assigned IP
                obj.ip_address = maas_dict["discovered"][0].get("ip_address")
                obj.ip_address = maas_dict["discovered"][0].get("mac_address")
                obj.subnet_cidr = maas_dict["discovered"][0]["subnet"].get("cidr")
                obj.vlan = maas_dict["discovered"][0]["subnet"]["vlan"].get("name")
                obj.fabric = maas_dict["discovered"][0]["subnet"]["vlan"].get("fabric")
            elif maas_dict.get("links") and len(maas_dict["links"]) > 0:  # Static IP
                obj.ip_address = maas_dict["links"][0].get("ip_address")
                obj.ip_address = maas_dict["links"][0].get("mac_address")
                obj.subnet_cidr = maas_dict["links"][0]["subnet"].get("cidr")
                obj.vlan = maas_dict["links"][0]["subnet"]["vlan"].get("name")
                obj.fabric = maas_dict["links"][0]["subnet"]["vlan"].get("fabric")
            else:  # interface auto generated
                obj.ip_address = maas_dict.get("ip_address")
                obj.subnet_cidr = maas_dict.get("cidr")
                # "if" added because of: AttributeError: 'NoneType' object has no attribute 'get'
                if maas_dict["vlan"]:
                    obj.vlan = maas_dict["vlan"].get("name")
                    obj.fabric = maas_dict["vlan"].get("fabric")
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
            to_maas_dict["tags"] = ",".join(self.tags)
        if self.ip_address:
            to_maas_dict["ip_address"] = self.ip_address
        if self.fabric:
            to_maas_dict["fabric"] = self.fabric
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
            mac_address=self.mac_address,
            mtu=self.mtu,
            tags=self.tags,
        )

    def needs_update(self, new_nic):
        new_nic_dict = new_nic.to_maas()
        if is_superset(
            self.to_maas(),
            filter_dict(new_nic_dict, list(new_nic_dict.keys())),
        ):
            return False
        return True

    def payload_for_update(self):
        return self.to_maas()

    def send_update_request(self, client, machine_obj, payload, nic_id):
        results = client.put(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/{nic_id}/", data=payload
        ).json
        return results

    def payload_for_create(self):
        return self.to_maas()

    def send_create_request(self, client, machine_obj, payload):
        results = client.post(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/",
            query={"op": "create_physical"},
            data=payload,
        ).json
        return results

    def send_delete_request(self, client, machine_obj, nic_id):
        # DELETE does not return valid json.
        client.delete(f"/api/2.0/nodes/{machine_obj.id}/interfaces/{nic_id}/")
