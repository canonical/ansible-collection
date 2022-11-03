#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: block_device_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns info about MAAS machines' block devices.
description:
  - Plugin returns information about all block devices or specific block device if I(name) is provided.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  machine_fqdn:
    description:
      - Fully qualified domain name of the specific machine whose block devices will be listed.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
    required: true
  name:
    description:
      - Name of a block device.
      - Serves as unique identifier of the block device.
      - If block device is not found the task will FAIL.
    type: str
"""

EXAMPLES = r"""
- name: Get list of all block devices of a selected machine.
  canonical.maas.block_device_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine_fqdn: machine_name.project

- name: Get info about a specific block device of a selected machine.
  canonical.maas.block_device_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    machine_fqdn: machine_name.project
    name: newblockdevice
"""

RETURN = r"""
records:
  description:
    - Machine's block device info list.
  returned: success
  type: list
  sample:
  - firmware_version: null
    system_id: y7388k
    block_size: 102400
    available_size: 1000000000
    model: fakemodel
    serial: 123
    used_size: 0
    tags: []
    partition_table_type: null
    partitions: []
    path: /dev/disk/by-dname/newblockdevice
    size: 1000000000
    id_path: ""
    filesystem: null
    storage_pool: null
    name: newblockdevice
    used_for: Unused
    id: 73
    type: physical
    uuid: null
    resource_uri: /MAAS/api/2.0/nodes/y7388k/blockdevices/73/
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine
from ..module_utils.block_device import BlockDevice


def run(module, client: Client):
    machine = Machine.get_by_fqdn(
        module, client, must_exist=True, name_field_ansible="machine_fqdn"
    )
    if module.params["name"]:
        block_device = BlockDevice.get_by_name(
            module, client, machine.id, must_exist=True
        )
        response = [block_device.get(client)]
    else:
        response = client.get(f"/MAAS/api/2.0/nodes/{machine.id}/blockdevices/").json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            machine_fqdn=dict(type="str", required=True),
            name=dict(type="str"),
        ),
    )

    try:
        cluster_instance = module.params["cluster_instance"]
        host = cluster_instance["host"]
        consumer_key = cluster_instance["customer_key"]
        token_key = cluster_instance["token_key"]
        token_secret = cluster_instance["token_secret"]

        client = Client(host, token_key, token_secret, consumer_key)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
