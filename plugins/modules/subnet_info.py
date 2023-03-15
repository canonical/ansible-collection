#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: subnet_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: List subnets.
description:
  - Plugin returns all subnets.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options: {}
"""

EXAMPLES = r"""
- name: List subnets
  canonical.maas.subnet_info:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
"""

RETURN = r"""
record:
  description:
    - List subnets.
  returned: success
  type: list
  sample:
    records:
    - active_discovery: false
      allow_dns: true
      allow_proxy: true
      cidr: 10.157.248.0/24
      description: ''
      disabled_boot_architectures: []
      dns_servers: []
      gateway_ip: 10.157.248.1
      id: 1
      ip_ranges:
      - end_ip: 192.168.0.128
        start_ip: 192.168.0.64
        type: reserved
      managed: true
      name: 10.157.248.0/24
      rdns_mode: 2
      resource_uri: /MAAS/api/2.0/subnets/1/
      space: undefined
      vlan:
        dhcp_on: false
        external_dhcp: null
        fabric: fabric-0
        fabric_id: 0
        id: 5001
        mtu: 1500
        name: untagged
        primary_rack: null
        relay_vlan: null
        resource_uri: /MAAS/api/2.0/vlans/5001/
        secondary_rack: null
        space: undefined
        vid: 0
"""

from itertools import groupby

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client


def get_ip_ranges(client):
    def key_function(item):
        return item["subnet"]

    ip_ranges = client.get("/api/2.0/ipranges/").json
    data = [
        {
            "subnet": ip_range["subnet"]["name"],
            "data": {
                "type": ip_range["type"],
                "start_ip": ip_range["start_ip"],
                "end_ip": ip_range["end_ip"],
            },
        }
        for ip_range in ip_ranges
    ]

    sorted_data = sorted(data, key=key_function)

    grouped = {
        k: [v["data"] for v in g]
        for k, g in groupby(sorted_data, key_function)
    }
    return grouped


def run(client: Client):
    subnets = client.get("/api/2.0/subnets/").json
    ip_ranges = get_ip_ranges(client)
    for subnet in subnets:
        subnet["ip_ranges"] = ip_ranges.get(subnet["name"], [])

    return subnets


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        records = run(client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as ex:
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
