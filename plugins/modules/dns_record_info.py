#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
module: dns_record_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: List DNS records.
description:
  - Plugin returns information about available DNS records.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  all:
    description: Include implicit DNS records created for nodes registered in MAAS if true.
    type: bool
    required: false
"""

EXAMPLES = r"""
- name: List records
  cannonical.maas.dns_records_info:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
"""

RETURN = r"""
record:
  description:
    - List of all dns records.
  returned: success
  type: list
  sample:
    - address_ttl: null
      fqdn: maas.maas
      id: -1
      ip_addresses: null
      resource_records:
      - dnsdata_id: null
        dnsresource_id: null
        node_type: 4
        rrdata: 10.157.248.49
        rrtype: A
        system_id: kwxmgm
        ttl: null
        user_id: null
      resource_uri: /MAAS/api/2.0/dnsresources/-1/
    - address_ttl: null
      fqdn: lxdbr0.maas
      id: -1
      ip_addresses: null
      resource_records:
      - dnsdata_id: null
        dnsresource_id: null
        node_type: 4
        rrdata: 10.10.10.1
        rrtype: A
        system_id: kwxmgm
        ttl: null
        user_id: 1
      resource_uri: /MAAS/api/2.0/dnsresources/-1/
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client


def to_ansible(record):
    resource_records = record.get("resource_records", [])
    if resource_records:
        item = resource_records[0]
        return {
            "type": item["rrtype"],
            "data": item["rrdata"],
            "fqdn": item["fqdn"],
            "ttl": item["ttl"],
        }

    return {
        "type": "A/AAAA",
        "data": record["ip_addresses"][0]["ip"],
        "fqdn": record["fqdn"],
        "ttl": record["address_ttl"],
    }


def run(module, client: Client):
    query = {"all": True} if module.params["all"] else None
    response = client.get("/api/2.0/dnsresources/", query).json

    result = [to_ansible(item) for item in response]
    return result


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            all=dict(type="bool", required=False),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as ex:
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
