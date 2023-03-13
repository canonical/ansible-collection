#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_host_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: Returns info about vm hosts.
description:
  - Plugin returns information about all or specific vm hosts if I(name) is provided.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  name:
    description:
      - Name of the specific vm host to be listed.
      - Serves as unique identifier of the vm host.
      - If vm host is not found the task will FAIL.
    type: str
"""

EXAMPLES = r"""
- name: Get list of all hosts.
  canonical.maas.vm_host_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key

- name: Get info about a specific vm host.
  canonical.maas.vm_host_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    name: sunny-raptor
"""

RETURN = r"""
records:
  description:
    - List records of vm hosts.
  returned: success
  type: list
  sample:
    - architectures:
      - amd64/generic
      available:
        cores: 1
        local_storage: 6884062720
        memory: 4144
      capabilities:
      - composable
      - dynamic_local_storage
      - over_commit
      - storage_pools
      cpu_over_commit_ratio: 1.0
      default_macvlan_mode: null
      host:
        __incomplete__: true
        system_id: d6car8
      id: 1
      memory_over_commit_ratio: 1.0
      name: sunny-raptor
      pool:
        description: Default pool
        id: 0
        name: default
        resource_uri: /MAAS/api/2.0/resourcepool/0/
      resource_uri: /MAAS/api/2.0/vm-hosts/1/
      storage_pools:
      - available: 6884062720
        default: true
        id: default
        name: default
        path: /var/snap/lxd/common/lxd/disks/default.img
        total: 22884062720
        type: zfs
        used: 16000000000
      tags:
      - pod-console-logging
      total:
        cores: 4
        local_storage: 22884062720
        memory: 8192
      type: lxd
      used:
        cores: 3
        local_storage: 16000000000
        memory: 4048
      version: '5.5'
      zone:
        description: ''
        id: 1
        name: default
        resource_uri: /MAAS/api/2.0/zones/default/
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.vmhost import VMHost


def run(module, client: Client):
    if module.params["name"]:
        vm_host = VMHost.get_by_name(module, client, must_exist=True)
        response = [vm_host.get(client)]
    else:
        response = client.get("/api/2.0/vm-hosts/").json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(type="str"),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
