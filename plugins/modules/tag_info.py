#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: tag_info

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Get list of all tags.
description: Shows information about all tags on this MAAS.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options: {}
"""

EXAMPLES = r"""
- name: List tags
  canonical.maas.tag_info:
    cluster_instance:
      host: http://10.44.240.10:5240/MAAS
      token_key: kDcKvtWX7fXLB7TvB2
      token_secret: ktBqeLMRvLBDLFm7g8xybgpQ4jSkkwgk
      customer_key: tqDErtYzyzRVdUb9hS
  register: tags
- ansible.builtin.debug:
  var: tags
"""

RETURN = r"""
records:
  description:
    - Tag information.
  returned: success
  type: list
  sample:
    - comment: ''
      definition: ''
      kernel_opts: ''
      name: virtual
      resource_uri: /MAAS/api/2.0/tags/virtual/
    - comment: ''
      definition: ''
      kernel_opts: console=tty1 console=ttyS0
      name: pod-console-logging
      resource_uri: /MAAS/api/2.0/tags/pod-console-logging/
    - comment: my-tag
      definition: ''
      kernel_opts: ''
      name: my-tag
      resource_uri: /MAAS/api/2.0/tags/my-tag/
    - comment: my-tag2
      definition: ''
      kernel_opts: ''
      name: my-tag2
      resource_uri: /MAAS/api/2.0/tags/my-tag2/
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.cluster_instance import get_oauth1_client


def run(module, client):
    response = client.get("/api/2.0/tags/")
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
