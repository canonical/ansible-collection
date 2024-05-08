# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.zone import Zone

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_zone_dict = dict(
            name="zone-name",
            id="zone-id",
            description="zone-description",
            resource_uri="resource_uri",
        )
        zone = Zone(
            maas_zone_dict["name"],
            maas_zone_dict["id"],
            maas_zone_dict["description"],
            maas_zone_dict["resource_uri"],
        )
        results = Zone.from_maas(maas_zone_dict)
        assert results.name == zone.name
        assert results.id == zone.id
        assert results.description == zone.description
        assert results.resource_uri == zone.resource_uri

