# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.fabric import Fabric

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_fabric_dict = dict(
            name="fabric-name",
            id="fabric-id",
            vlans=["vlans"],
            resource_uri="resource_uri",
            class_type="class_type",
        )
        fabric = Fabric(
            maas_fabric_dict["name"],
            maas_fabric_dict["id"],
            maas_fabric_dict["vlans"],
            maas_fabric_dict["resource_uri"],
            maas_fabric_dict["class_type"],
        )
        results = Fabric.from_maas(maas_fabric_dict)
        assert results.name == fabric.name
        assert results.id == fabric.id
        assert results.vlans == fabric.vlans
        assert results.resource_uri == fabric.resource_uri
        assert results.class_type == fabric.class_type
