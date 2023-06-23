#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: boot_sources_info

author:
  - Jure Medvesek (@juremedvesek)
short_description: Return info about boot sources.
description:
  - Plugin returns information about available boot sources.
version_added: 1.0.0
extends_documentation_fragment:
  - maas.maas.cluster_instance
seealso: []
options: {}
"""

EXAMPLES = r"""
- name: List boot sources
  maas.maas.vm_host_info:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
"""

RETURN = r"""
records:
  description:
    - Boot sources info list.
  returned: success
  type: list
  sample: # ADD SAMPLE
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client


def run(module, client: Client):
    response = client.get("/api/2.0/boot-resources/")
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
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
