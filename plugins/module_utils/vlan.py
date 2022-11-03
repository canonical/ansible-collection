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
from ..module_utils.client import Client


class Vlan(MaasValueMapper):
    def __init__(
        self,
        name=None,
        id=None,
        vid=None,
        mtu=None,
        dhcp_on=None,
        external_dhcp=None,
        relay_vlan=None,
        space=None,
        fabric_id=None,
        secondary_rack=None,
        fabric=None,
        primary_rack=None,
        resource_uri=None,
    ):
        self.name = name
        self.id = id
        self.vid = vid
        self.mtu = mtu
        self.dhcp_on = dhcp_on
        self.external_dhcp = external_dhcp
        self.relay_vlan = relay_vlan
        self.space = space
        self.fabric_id = fabric_id
        self.secondary_rack = secondary_rack
        self.fabric = fabric
        self.primary_rack = primary_rack
        self.resource_uri = resource_uri

    @classmethod
    def get_by_name(
        cls,
        module,
        client: Client,
        fabric_id,
        must_exist=False,
        name_field_ansible="vlan_name",
    ):
        rest_client = RestClient(client=client)
        query = get_query(
            module,
            name_field_ansible,
            ansible_maas_map={name_field_ansible: "name"},
        )
        maas_dict = rest_client.get_record(
            f"/api/2.0/fabrics/{fabric_id}/vlans/", query, must_exist=must_exist
        )
        if maas_dict:
            vlan_from_maas = cls.from_maas(maas_dict)
            return vlan_from_maas

    @classmethod
    def get_by_vid(cls, vid, client: Client, fabric_id, must_exist=False):
        response = client.get(f"/api/2.0/fabrics/{fabric_id}/vlans/{vid}/")
        if response.status == 404:
            if must_exist:
                raise errors.VlanNotFound(vid)
            return None
        vlan_maas_dict = response.json
        vlan = cls.from_maas(vlan_maas_dict)
        return vlan

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.name = maas_dict["name"]
            obj.id = maas_dict["id"]
            obj.vid = maas_dict["vid"]
            obj.mtu = maas_dict["mtu"]
            obj.dhcp_on = maas_dict["dhcp_on"]
            obj.external_dhcp = maas_dict["external_dhcp"]
            obj.relay_vlan = maas_dict["relay_vlan"]
            obj.space = maas_dict["space"]
            obj.fabric_id = maas_dict["fabric_id"]
            obj.secondary_rack = maas_dict["secondary_rack"]
            obj.fabric = maas_dict["fabric"]
            obj.primary_rack = maas_dict["primary_rack"]
            obj.resource_uri = maas_dict["resource_uri"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return dict(
            name=self.name,
            id=self.id,
            vid=self.vid,
            mtu=self.mtu,
            dhcp_on=self.dhcp_on,
            external_dhcp=self.external_dhcp,
            relay_vlan=self.relay_vlan,
            space=self.space,
            fabric_id=self.fabric_id,
            secondary_rack=self.secondary_rack,
            fabric=self.fabric,
            primary_rack=self.primary_rack,
            resource_uri=self.resource_uri,
        )

    def delete(self, client):
        client.delete(f"/api/2.0/fabrics/{self.fabric_id}/vlans/{self.vid}/")

    def get(self, client):
        return client.get(f"/api/2.0/fabrics/{self.fabric_id}/vlans/{self.vid}/").json
        # Also possible: client.get(f"/api/2.0/vlans/{self.id}/").json

    def update(self, client, payload):
        return client.put(
            f"/api/2.0/fabrics/{self.fabric_id}/vlans/{self.vid}/", data=payload
        ).json

    @classmethod
    def create(cls, client, fabric_id, payload):
        vlan_maas_dict = client.post(
            f"/api/2.0/fabrics/{fabric_id}/vlans/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        vlan = cls.from_maas(vlan_maas_dict)
        return vlan

    def __eq__(self, other):
        """One vlan is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.name == other.name,
                self.id == other.id,
                self.vid == other.vid,
                self.mtu == other.mtu,
                self.dhcp_on == other.dhcp_on,
                self.external_dhcp == other.external_dhcp,
                self.relay_vlan == other.relay_vlan,
                self.space == other.space,
                self.fabric_id == other.fabric_id,
                self.secondary_rack == other.secondary_rack,
                self.fabric == other.fabric,
                self.primary_rack == other.primary_rack,
                self.resource_uri == other.resource_uri,
            )
        )
