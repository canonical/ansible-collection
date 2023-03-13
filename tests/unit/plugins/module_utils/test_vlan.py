# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.module_utils.client import (
    Response,
)
from ansible_collections.canonical.maas.plugins.module_utils.vlan import Vlan

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_vlan_dict = dict(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )
        vlan = Vlan(
            maas_vlan_dict["name"],
            maas_vlan_dict["id"],
            maas_vlan_dict["vid"],
            maas_vlan_dict["mtu"],
            maas_vlan_dict["dhcp_on"],
            maas_vlan_dict["external_dhcp"],
            maas_vlan_dict["relay_vlan"],
            maas_vlan_dict["space"],
            maas_vlan_dict["fabric_id"],
            maas_vlan_dict["secondary_rack"],
            maas_vlan_dict["fabric"],
            maas_vlan_dict["primary_rack"],
            maas_vlan_dict["resource_uri"],
        )
        results = Vlan.from_maas(maas_vlan_dict)
        assert results == vlan

    def test_to_ansible(self):
        vlan = Vlan(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )

        ansible_dict = dict(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )

        results = vlan.to_ansible()
        assert results == ansible_dict


class TestGet:
    def test_get_by_vid_200(self, client, mocker):
        vid = 5
        fabric_id = 10
        client.get.return_value = Response(
            200,
            '{"name":"vlan-name", "id":5014, "vid":5, "mtu":1000, "dhcp_on":true, "external_dhcp":"external_dhcp", "relay_vlan":"relay_vlan",\
                "space":"my-space", "fabric_id":10, "secondary_rack":"secondary-rack", "fabric":"fabric-10", "primary_rack":"primary_rack",\
                    "resource_uri":"/MAAS/api/2.0/vlans/5014/"}',
        )
        vlan = Vlan(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )
        results = Vlan.get_by_vid(vid, client, fabric_id, must_exist=False)

        client.get.assert_called_with(
            "/api/2.0/fabrics/10/vlans/5/",
        )
        assert results == vlan

    def test_get_by_vid_404(self, client, mocker):
        vid = 5
        fabric_id = 10
        client.get.return_value = Response(404, "{}")
        results = Vlan.get_by_vid(vid, client, fabric_id, must_exist=False)

        client.get.assert_called_with(
            "/api/2.0/fabrics/10/vlans/5/",
        )
        assert results is None

    def test_get_by_vid_404_must_exist(self, client, mocker):
        vid = 5
        fabric_id = 10
        client.get.return_value = Response(404, "{}")

        with pytest.raises(errors.VlanNotFound) as exc:
            Vlan.get_by_vid(vid, client, fabric_id, must_exist=True)

        assert "VLAN - 5 - not found" in str(exc.value)

    def test_get_by_name(self, create_module, mocker, client):
        fabric_id = 10
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                fabric_name="fabric-10",
                vid=5,
                vlan_name="vlan_name",
                new_vlan_name=None,
                description="vlan description",
                mtu=1000,
                dhcp_on=True,
                space="my-space",
            )
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = dict(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )

        assert Vlan.get_by_name(module, client, fabric_id, True) == Vlan(
            name="vlan-name",
            id=5014,
            vid=5,
            mtu=1000,
            dhcp_on=True,
            external_dhcp="external_dhcp",
            relay_vlan="relay_vlan",
            space="my-space",
            fabric_id=10,
            secondary_rack="secondary-rack",
            fabric="fabric-10",
            primary_rack="primary_rack",
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )
