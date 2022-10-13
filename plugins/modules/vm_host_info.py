#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_hosts

author:
  - Jure Medvesek (@juremedvesek)
short_description: Return info about vm hosts
description:
  - Plugin return information about all or specific vm hosts.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
"""

EXAMPLES = r"""
- name: Get list of all hosts.
  hosts: localhost
  tasks:
  - name: Get host info.
    canonical.maas.vm_host_info:
      cluster_instance:
        host: 'host address'
        token_key: 'token key'
        token_secret: 'token secret'
        customer_key: 'customer key'
    register: hosts
  - debug:
      var: hosts
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


def run(module, client: Client):
    response = client.request("GET", "/api/2.0/vm-hosts/")
    return response.json


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
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
