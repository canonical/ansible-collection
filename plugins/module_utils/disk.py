# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from .utils import MaasValueMapper
from . import errors


class Disk(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        name=None,
        id=None,
        size=None,
    ):
        self.name = name
        self.id = id
        self.size = size

    @classmethod
    def from_ansible(cls, disk_dict):
        obj = Disk()
        obj.size = disk_dict["size_gigabytes"]
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = Disk()
        try:
            obj.name = maas_dict["name"]
            obj.id = maas_dict["id"]
            obj.size = int(int(maas_dict["size"]) / 1000000000)
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        to_maas_dict = {}
        if self.id:
            to_maas_dict["id"] = self.id
        if self.name:
            to_maas_dict["name"] = self.name
        if self.size:
            to_maas_dict["size"] = self.size
        return to_maas_dict

    def to_ansible(self):
        return dict(
            id=self.id,
            name=self.name,
            size_gigabytes=self.size,
        )
