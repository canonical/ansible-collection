#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from random import choices

__metaclass__ = type

DOCUMENTATION = r"""
module: instance # maas_instance?

author:
  - Polona Mihalič (@PolonaM)
short_description: Deploy or release machines already configured in MAAS.
description:
  - If I(state) value is C(deploy) the selected machine will be deployed.
  - If I(state) value is C(release) the selected machine will be released.
  - If no parameters are given, a random machine will be allocated and deployed using the defaults. # THIS IS DONE IN TERRAFORM
version_added: 1.0.0
extends_documentation_fragment: # ADD DOC_FRAGMENT FOR VM_HOST
seealso: []
options:
  name:
    description:
      - Name of the machine to be deployed or released.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
    required: True
  state:
    description:
      - Desired state of the machine.
    choices: [ deploy, release ]
    type: str
    required: True
"""

EXAMPLES = r"""
"""

RETURN = r"""
machines:
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client


def release(module, client: Client):  # "client: Client" is type annotation
    system_id = "w7d7ef"
    response = client.post(
        f"/api/2.0/machines/{system_id}/", query={"op": "release"}, data={}
    )
    return response.json


def deploy(module, client: Client):
    system_id = "w7d7ef"
    response = client.post(
        f"/api/2.0/machines/{system_id}/", query={"op": "deploy"}, data={}
    )
    return response.json


def run(module, client: Client):
    if module.params["state"] == "release":
        return release(module, client)
    return deploy(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("instance"),
            name=dict(type="str", required=True),
            state=dict(type="str", required=True, choices=["deployed", "released"]),
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
