# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.space import Space

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_space_dict = dict(
            name="space-name",
            id="space-id",
            vlans=["vlans"],
            resource_uri="resource_uri",
            subnets=["subnets"],
        )
        space = Space(
            maas_space_dict["name"],
            maas_space_dict["id"],
            maas_space_dict["vlans"],
            maas_space_dict["resource_uri"],
            maas_space_dict["subnets"],
        )
        results = Space.from_maas(maas_space_dict)
        assert results.name == space.name
        assert results.id == space.id
        assert results.vlans == space.vlans
        assert results.resource_uri == space.resource_uri
        assert results.subnets == space.subnets
