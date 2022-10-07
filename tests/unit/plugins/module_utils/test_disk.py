# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.disk import Disk

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    @staticmethod
    def _get_disk():
        return dict(name="test_disk", id=123, size=500000000000)

    @staticmethod
    def _get_disk_from_ansible():
        return dict(size_gigabytes=5)

    def test_from_maas(self):
        maas_disk_dict = self._get_disk()
        disk_obj = Disk(
            maas_disk_dict["name"],
            maas_disk_dict["id"],
            maas_disk_dict["size"] / 1000000000,
        )
        results = Disk.from_maas(maas_disk_dict)
        assert (
            results.name == disk_obj.name
            and results.id == disk_obj.id
            and results.size == disk_obj.size
        )

    def test_from_ansible(self):
        disk_dict = self._get_disk_from_ansible()
        disk_obj = Disk(size=disk_dict["size_gigabytes"])
        results = Disk.from_ansible(disk_dict)
        print(results.size, disk_obj.size)
        assert results.size == disk_obj.size

    def test_to_maas(self):
        disk_dict = self._get_disk()
        expected = dict(name="test_disk", id=123, size=500000000000)
        disk_obj = Disk(disk_dict["name"], disk_dict["id"], disk_dict["size"])
        results = disk_obj.to_maas()
        assert results == expected

    def test_to_ansible(self):
        disk_dict = self._get_disk()
        expected = dict(id=123, name="test_disk", size_gigabytes=500)
        disk_obj = Disk(disk_dict["name"], disk_dict["id"], 500)
        results = disk_obj.to_ansible()
        assert results == expected
