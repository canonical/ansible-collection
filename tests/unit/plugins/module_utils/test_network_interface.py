# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.network_interface import (
    NetworkInterface,
)


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    @staticmethod
    def _get_net_interface():
        return dict(
            name="test_net_int",
            id=123,
            system_id=1234,
            mac_address="this-mac",
            tags=[],
            effective_mtu=1500,
            links=[
                dict(
                    subnet=dict(cidr="ip", vlan=dict(name="vlan-1", fabric="fabric-1"))
                )
            ],
        )

    @staticmethod
    def _get_net_interface_from_ansible():
        return dict(name="test_net", subnet_cidr="ip")

    def test_from_maas(self):
        maas_net_interface_dict = self._get_net_interface()
        net_interface = NetworkInterface(
            maas_net_interface_dict["name"],
            maas_net_interface_dict["id"],
            maas_net_interface_dict["links"][0]["subnet"]["cidr"],
            maas_net_interface_dict["system_id"],
        )
        results = NetworkInterface.from_maas(maas_net_interface_dict)
        assert (
            results.name == net_interface.name
            and results.id == net_interface.id
            and results.machine_id == net_interface.machine_id
            and results.subnet_cidr == net_interface.subnet_cidr
        )

    def test_from_ansible(self):
        net_interface_dict = self._get_net_interface_from_ansible()
        net_interface = NetworkInterface(
            name=net_interface_dict["name"],
            subnet_cidr=net_interface_dict["subnet_cidr"],
        )
        results = NetworkInterface.from_ansible(net_interface_dict)
        assert (
            results.name == net_interface.name
            and results.subnet_cidr == net_interface.subnet_cidr
        )

    def test_to_maas(self):
        net_interface_dict = self._get_net_interface()
        expected = dict(
            name="test_net_int",
            id=123,
            subnet_cidr="ip",
            mac_address="this-mac",
            ip_address="this-ip",
            fabric="fabric-1",
            vlan="this-vlan",
            label_name="this-interface",
            mtu=1500,
        )
        net_interface_obj = NetworkInterface(
            net_interface_dict["name"],
            net_interface_dict["id"],
            net_interface_dict["links"][0]["subnet"]["cidr"],
            net_interface_dict["system_id"],
            "this-mac",
            "this-vlan",
            1500,
            [],
            "this-ip",
            net_interface_dict["links"][0]["subnet"]["vlan"]["fabric"],
            "this-interface",
        )
        results = net_interface_obj.to_maas()
        assert results == expected

    def test_to_ansible(self):
        net_interface_dict = self._get_net_interface()
        expected = dict(
            id=123,
            name="test_net_int",
            subnet_cidr="ip",
            ip_address="this-ip",
            fabric="this-fabric",
            vlan="this-vlan",
            mac="this-mac",
            mtu=1500,
            tags=None,
        )
        net_interface_obj = NetworkInterface(
            net_interface_dict["name"],
            net_interface_dict["id"],
            net_interface_dict["links"][0]["subnet"]["cidr"],
            net_interface_dict["system_id"],
            "this-mac",
            "this-vlan",
            1500,
            None,
            "this-ip",
            "this-fabric",
            "this-label",
            "this-mac-address",
        )
        results = net_interface_obj.to_ansible()
        assert results == expected
