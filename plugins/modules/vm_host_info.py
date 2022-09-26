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
  - canonical.maas.instance
seealso: []
options:
"""

EXAMPLES = r"""
"""

RETURN = r"""
machines:
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
            arguments.get_spec("instance"),
        ),
    )

    try:
        instance = module.params["instance"]
        host = instance["host"]
        client_key = instance["client_key"]
        token_key = instance["token_key"]
        token_secret = instance["token_secret"]

        client = Client(host, token_key, token_secret, client_key)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
