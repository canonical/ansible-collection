# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils.utils import MaasValueMapper
from ..module_utils import errors
from ..module_utils.client import Client


class Partition(MaasValueMapper):
    def __init__(
        self,
        id=None,
        machine_id=None,
        block_device_id=None,
    ):

        self.id = id
        self.machine_id = machine_id
        self.block_device_id = block_device_id

    @classmethod
    def get_by_id(
        cls, id, client: Client, machine_id, block_device_id, must_exist=False
    ):
        response = client.get(
            f"/api/2.0/nodes/{machine_id}/blockdevices/{block_device_id}/partition/{id}/"
        )
        if response.status == 404:
            if must_exist:
                raise errors.PartitionNotFound(id)
            return None
        partition_maas_dict = response.json
        partition = cls.from_maas(partition_maas_dict)
        return partition

    @classmethod
    def from_ansible(cls, module):
        return

    @classmethod
    def from_maas(cls, maas_dict):
        obj = cls()
        try:
            obj.block_device_id = maas_dict[
                "id"
            ]  # or read from partition maas_dict["partitions"][0]["device_id"] - check if it is 0 element!
            obj.id = maas_dict["partitions"][0][
                "id"
            ]  # - check if it is 0 element or it needs to be searched by id??
            obj.machine_id = maas_dict["system_id"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return

    def delete(self, client):
        client.delete(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/"
        )

    def get(self, client):
        return client.get(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/"
        ).json

    def add_tag(self, client, tag):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/",
            query={"op": "add_tag"},
            data=tag,
        ).json

    def remove_tag(self, client, tag):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/",
            query={"op": "remove_tag"},
            data=tag,
        ).json

    def format(self, client, payload):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/",
            query={"op": "format"},
            data=payload,
        ).json

    def unformat(self, client):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/",
            query={"op": "unformat"},
        ).json

    def mount(self, client, payload):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/",
            query={"op": "mount"},
            data=payload,
        ).json

    def unmount(self, client):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}/",
            query={"op": "unmount"},
        ).json

    @classmethod
    def create(cls, client, machine_id, block_device_id, payload):
        partition_maas_dict = client.post(
            f"/api/2.0/nodes/{machine_id}/blockdevices/{block_device_id}/partitions/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        partition = cls.from_maas(partition_maas_dict)
        return partition

    def __eq__(self, other):
        """One vlan is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.block_device_id == other.block_device_id,
                self.id == other.id,
                self.machine_id == other.machine_id,
            )
        )
