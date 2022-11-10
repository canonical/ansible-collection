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
        size=None,
        bootable=None,
        tags=None,
        fstype=None,
        label=None,
        mount_point=None,
        mount_options=None,
    ):
        self.id = id
        self.machine_id = machine_id
        self.block_device_id = block_device_id
        self.size = size
        self.bootable = bootable
        self.tags = tags
        self.fstype = fstype
        self.label = label
        self.mount_point = mount_point
        self.mount_options = mount_options

    @classmethod
    def get_by_id(
        cls, id, client: Client, machine_id, block_device_id, must_exist=False
    ):
        response = client.get(
            f"/api/2.0/nodes/{machine_id}/blockdevices/{block_device_id}/partition/{id}"
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
            obj.block_device_id = maas_dict["device_id"]
            obj.id = maas_dict["id"]
            obj.machine_id = maas_dict["system_id"]
            obj.size = maas_dict["size"]
            obj.bootable = maas_dict["bootable"]
            obj.tags = maas_dict["tags"]
            if maas_dict["filesystem"]:
                obj.fstype = maas_dict["filesystem"]["fstype"]
                obj.label = maas_dict["filesystem"]["label"]
                obj.mount_point = maas_dict["filesystem"]["mount_point"]
                obj.mount_options = maas_dict["filesystem"]["mount_options"]
        except KeyError as e:
            raise errors.MissingValueMAAS(e)
        return obj

    def to_maas(self):
        return

    def to_ansible(self):
        return

    def delete(self, client):
        client.delete(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}"
        )

    def get(self, client):
        response = client.get(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}"
        )
        raise Exception(response)

    def add_tag(self, client, tag):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}",
            query={"op": "add_tag"},
            data=dict(tag=tag),
        ).json

    def remove_tag(self, client, tag):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}",
            query={"op": "remove_tag"},
            data=dict(tag=tag),
        ).json

    def format(self, client, payload):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}",
            query={"op": "format"},
            data=payload,
        ).json

    def unformat(self, client):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}",
            query={"op": "unformat"},
            data={},
        ).json

    def mount(self, client, payload):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}",
            query={"op": "mount"},
            data=payload,
        ).json

    def unmount(self, client):
        return client.post(
            f"/api/2.0/nodes/{self.machine_id}/blockdevices/{self.block_device_id}/partition/{self.id}",
            query={"op": "unmount"},
            data={},
        ).json

    @classmethod
    def create(cls, client, block_device, payload):
        partition_maas_dict = client.post(
            f"/api/2.0/nodes/{block_device.machine_id}/blockdevices/{block_device.id}/partitions/",
            data=payload,
            timeout=60,  # Sometimes we get timeout error thus changing timeout from 20s to 60s
        ).json
        partition = cls.from_maas(partition_maas_dict)
        return partition

    def __eq__(self, other):
        """One partition is equal to another if it has all attributes exactly the same"""
        return all(
            (
                self.block_device_id == other.block_device_id,
                self.id == other.id,
                self.machine_id == other.machine_id,
                self.size == other.size,
                self.bootable == other.bootable,
                self.tags == other.tags,
                self.fstype == other.fstype,
                self.label == other.label,
                self.mount_point == other.mount_point,
                self.mount_options == other.mount_options,
            )
        )
