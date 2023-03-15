#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: subnet_ip_range_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: List IP ranges.
description:
  - Plugin returns all IP ranges.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options: {}
"""

EXAMPLES = r"""
- name: List IP ranges
  canonical.maas.subnet_ip_range_info:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
"""

RETURN = r"""
record:
  description:
    - List IP ranges.
  returned: success
  type: list
  sample:
    - comment: ''
      end_ip: 10.10.10.254
      id: 1
      resource_uri: /MAAS/api/2.0/ipranges/1/
      start_ip: 10.10.10.200
      subnet:
        active_discovery: false
        allow_dns: true
        allow_proxy: true
        cidr: 10.10.10.0/24
        description: ''
        disabled_boot_architectures: []
        dns_servers: []
        gateway_ip: 10.10.10.1
        id: 2
        managed: true
        name: 10.10.10.0/24
        rdns_mode: 2
        resource_uri: /MAAS/api/2.0/subnets/2/
        space: undefined
        vlan:
          dhcp_on: true
          external_dhcp: null
          fabric: fabric-1
          fabric_id: 1
          id: 5002
          mtu: 1500
          name: untagged
          primary_rack: kwxmgm
          relay_vlan: null
          resource_uri: /MAAS/api/2.0/vlans/5002/
          secondary_rack: null
          space: undefined
          vid: 0
      type: dynamic
      user:
        email: admin
        is_local: true
        is_superuser: true
        resource_uri: /MAAS/api/2.0/users/admin/
        username: admin
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client


def run(client: Client):
    response = client.get("/api/2.0/ipranges/")
    return response.json


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
