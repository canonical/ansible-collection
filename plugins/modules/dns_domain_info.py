#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: dns_domain_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: List DNS domains.
description:
  - Plugin returns information about available DNS domains.
version_added: 1.0.0
extends_documentation_fragment:
  - maas.maas.cluster_instance
seealso: []
options: {}
"""

EXAMPLES = r"""
- name: List domains
  maas.maas.dns_domain_info:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
"""

RETURN = r"""
record:
  description:
    - List of all domains.
  returned: success
  type: list
  sample:
    - authoritative: true
      id: 0
      is_default: true
      name: maas
      ttl: null
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client


def run(client: Client):
    response = client.get("/api/2.0/domains/")
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
