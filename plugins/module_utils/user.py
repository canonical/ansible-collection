# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import MaasValueMapper
from ..module_utils import errors

__metaclass__ = type


class User(MaasValueMapper):
    def __init__(
        # Add more values as needed.
        self,
        is_admin,
        name,
        email,
        is_local
    ):
        self.is_admin = is_admin
        self.name = name
        self.email = email
        self.is_local = is_local

    def __eq__(self, other):
        return self.to_ansible() == other.to_ansible()

    @classmethod
    def from_ansible(cls, user_dict):
        obj = User()
        return obj

    @classmethod
    def from_maas(cls, maas_dict):
        obj = User()
        try:
            obj.is_admin = maas_dict["is_superuser"]
            obj.email = maas_dict["email"]
            obj.name = maas_dict["name"]
            obj.is_local = maas_dict["is_local"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        to_maas_dict = {}
        return to_maas_dict

    def to_ansible(self):
        return dict(
            username=self.username,
            subnet_cidr=self.subnet_cidr,
            ip_address=self.ip_address,
            fabric=self.fabric,
            vlan=self.vlan,
            mac_address=self.mac_address,
            mtu=self.mtu,
            tags=self.tags,
        )
