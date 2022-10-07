# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine
from ansible_collections.scale_computing.hypercore.plugins.module_utils.client import (
    Response,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestGet:
    def test_get_by_id(self, client, mocker):
        id = 123
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.utils.get_query"
        ).return_value = []
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.from_maas"
        ).return_value = None
        client.get.return_value = Response(200, "{}")
        results = Machine.get_by_id(id, client, must_exist=True)
        assert results == None


class TestPayloadForCompose:
    def test_payload_for_compose_with_interface_and_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(
            interfaces=[
                dict(
                    label_name="test",
                    name="esp0",
                    subnet_cidr="subnet",
                    fabric="fabric-1",
                    vlan="vlan-1",
                    ip_address="ip",
                )
            ],
            storage=[dict(size=5), dict(size=10)],
        )
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {
            "interfaces": "test:subnet_cidr=subnet,ip=ip,fabric=fabric-1,vlan=vlan-1,name=esp0",
            "storage": "label:5,label:10",
        }

    def test_payload_for_compose_without_interface_and_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict()
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {}

    def test_payload_for_compose_with_storage_without_interface(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(storage=[dict(size=5), dict(size=10)])
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {"storage": "label:5,label:10"}

    def test_payload_for_compose_with_interface_without_storage(self, mocker):
        module = ""
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.to_maas"
        ).return_value = dict(
            interfaces=[dict(label_name="test", name="esp0", subnet_cidr="ip")]
        )
        machine_obj = Machine()
        results = machine_obj.payload_for_compose(module)
        assert results == {"interfaces": "test:subnet_cidr=ip,name=esp0"}


# TODO: test mapper, when more values are added.
