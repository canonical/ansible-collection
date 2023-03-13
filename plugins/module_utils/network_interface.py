# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils import errors
from ..module_utils.utils import MaasValueMapper, filter_dict, is_superset

__metaclass__ = type

__metaclass__ = type


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
        mode=None,
        default_gateway=None,
        connected=None,
        linked_subnets=None,
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
        self.mode = mode
        self.default_gateway = default_gateway
        self.connected = connected
        self.linked_subnets = linked_subnets

    def __eq__(self, other):
        return self.to_ansible() == other.to_ansible()

    @classmethod
    def from_ansible(cls, network_interface_dict):
        obj = NetworkInterface()
        obj.name = network_interface_dict.get(
            "name", network_interface_dict.get("network_interface")
        )
        obj.subnet_cidr = network_interface_dict.get(
            "subnet_cidr", network_interface_dict.get("subnet")
        )
        obj.ip_address = network_interface_dict.get("ip_address")
        obj.fabric = network_interface_dict.get("fabric")
        obj.vlan = network_interface_dict.get("vlan")
        obj.label_name = network_interface_dict.get("label_name")
        obj.mac_address = network_interface_dict.get("mac_address")
        obj.mtu = network_interface_dict.get("mtu")
        obj.tags = network_interface_dict.get("tags", [])
        obj.mode = network_interface_dict.get("mode")
        obj.default_gateway = network_interface_dict.get("default_gateway")
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
            obj.connected = maas_dict.get("link_connected", False)
            obj.linked_subnets = []  # One nic can have multiple linked subnets
            for linked_subnet in maas_dict["links"] or []:
                obj.linked_subnets.append(linked_subnet)
            if maas_dict.get("discovered"):  # Auto assigned IP
                obj.ip_address = maas_dict["discovered"][0].get("ip_address")
                obj.ip_address = maas_dict["discovered"][0].get("mac_address")
                obj.subnet_cidr = maas_dict["discovered"][0]["subnet"].get(
                    "cidr"
                )
                obj.vlan = maas_dict["discovered"][0]["subnet"]["vlan"].get(
                    "id"
                )
                obj.fabric = maas_dict["discovered"][0]["subnet"]["vlan"].get(
                    "fabric"
                )
            elif (
                maas_dict.get("links") and len(maas_dict["links"]) > 0
            ):  # Static IP
                obj.ip_address = maas_dict["links"][0].get("ip_address")
                obj.subnet_cidr = (
                    maas_dict["links"][0].get("subnet", {}).get("cidr")
                )
                obj.vlan = (
                    maas_dict["links"][0]
                    .get("subnet", {})
                    .get("vlan", {})
                    .get("id")
                )
                obj.fabric = (
                    maas_dict["links"][0]
                    .get("subnet", {})
                    .get("vlan", {})
                    .get("fabric")
                )
            else:  # interface auto generated
                obj.ip_address = maas_dict.get("ip_address")
                obj.subnet_cidr = maas_dict.get("cidr")
                # "if" added because of: AttributeError: 'NoneType' object has no attribute 'get'
                if maas_dict["vlan"]:
                    obj.vlan = maas_dict["vlan"].get("id")
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
        if self.mode:
            to_maas_dict["mode"] = self.mode
        if self.default_gateway:
            to_maas_dict["default_gateway"] = self.default_gateway

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

    def find_linked_alias_by_cidr(self, module):
        for linked_subnet in self.linked_subnets:
            if (
                linked_subnet.get("subnet", {}).get("name")
                and linked_subnet["subnet"]["name"] == module.params["subnet"]
            ):  # subnet name is cidr from MaaS API.
                return linked_subnet

    @staticmethod
    def find_subnet_by_cidr(client, cidr):
        results = client.get(
            "/api/2.0/subnets/",
        ).json
        for subnet in results:
            if subnet["cidr"] == cidr:
                return subnet

    def needs_update(self, new_nic):
        new_nic_dict = new_nic.to_maas()
        if is_superset(
            self.to_maas(),
            filter_dict(new_nic_dict, *list(new_nic_dict.keys())),
        ):
            return False
        return True

    @staticmethod
    def alias_needs_update(client, existing_alias, module):
        # Gateway can only be changed in STATIC or AUTO mode.
        # Ip_address can only be changed in STATIC mode.
        subnet = NetworkInterface.find_subnet_by_cidr(
            client, module.params["subnet"]
        )
        if (
            module.params["mode"]
            and existing_alias["mode"].lower() != module.params["mode"].lower()
        ):
            return True
        if (
            module.params["mode"] == "STATIC"
            and module.params["ip_address"]
            and existing_alias.get("ip_address") != module.params["ip_address"]
        ):
            return True
        if (
            (
                module.params["mode"] == "STATIC"
                or module.params["mode"] == "AUTO"
            )
            and module.params["default_gateway"]
            and existing_alias["gateway_ip"] != subnet["gateway_ip"]
        ):
            return True
        return False

    def payload_for_update(self):
        return self.to_maas()

    def send_update_request(self, client, machine_obj, payload, nic_id):
        results = client.put(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/{nic_id}/",
            data=payload,
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

    def payload_for_link_subnet(self, client, fabric):
        payload = self.to_maas()
        subnet = NetworkInterface.find_subnet_by_cidr(
            client, payload["subnet_cidr"]
        )
        if subnet.get("vlan", {}).get("fabric") != fabric:
            raise errors.MaasError(
                f"subnet - {payload['subnet_cidr']} does not have the same fabric. Try another subnet or change fabric."
            )
        payload["subnet"] = subnet["id"]
        return payload

    def send_link_subnet_request(self, client, machine_obj, payload, nic_id):
        results = client.post(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/{nic_id}/",
            query={"op": "link_subnet"},
            data=payload,
        ).json
        return results

    def send_unlink_subnet_request(
        self, client, machine_obj, linked_subnet_id
    ):
        results = client.post(
            f"/api/2.0/nodes/{machine_obj.id}/interfaces/{self.id}/",
            query={"op": "unlink_subnet"},
            data={"id": linked_subnet_id},
        ).json
        return results
