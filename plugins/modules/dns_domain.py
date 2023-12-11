#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: dns_domain

author:
  - Jure Medvesek (@juremedvesek)
short_description: Edit DNS domains.
description:
  - Plugin provides a resource to manage MAAS DNS domains.
version_added: 1.0.0
extends_documentation_fragment:
  - maas.maas.cluster_instance
seealso: []
options:
  state:
    description: Should domain be present or absent.
    type: str
    choices:
      - present
      - absent
    required: true
  name:
    description: The name of the DNS domain.
    type: str
    required: true
  authoritative:
    type: bool
    description: Boolean value indicating if the DNS domain is authoritative. Defaults to false
  ttl:
    type: int
    description: The default TTL for the DNS domain.
  is_default:
    type: bool
    description:
     - Boolean value indicating if the new DNS domain will be set as the default in the MAAS environment.
     - One is not allowed to set it to false. It can be achieved by setting to a value other than the default
    choices: [True]
"""

EXAMPLES = r"""
- name: Add domain
  maas.maas.dns_domain:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
    name: dns_domain_name
    state: present

    ttl: 3600
    authoritative: true
"""

RETURN = r"""
record:
  description:
    - Added domain.
  returned: success
  type: dict
  sample:
    authoritative: true
    id: 0
    is_default: true
    name: maas
    ttl: null
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client

ENDPOINT = "/api/2.0/domains/"


def clean_data(data: dict):
    return {key: value for key, value in data.items() if value is not None}


def get_match(items, key, value):
    return next((item for item in items if item.get(key) == value), None)


def must_update(old_data, new_data):
    return any(old_data.get(key) != value for key, value in new_data.items())


def ensure_present(module, client: Client):
    # extract all data from ansible task
    domain_name = module.params["name"]
    is_default = module.params["is_default"]

    data = {
        "name": module.params["name"],
        "ttl": module.params["ttl"],
        "authoritative": module.params["authoritative"],
    }
    cleaned_data = clean_data(data)

    # module.params["name"] not set - creating new item and return
    # Here name is obligatory, so this case is not reached

    # find a match on server, if none, create new object
    items = client.get(ENDPOINT).json
    item = get_match(items, "name", domain_name)
    if not item:
        response_json = client.post(ENDPOINT, cleaned_data).json
        return True, response_json, dict(before={}, after=response_json)

    # check if update is needed at all
    item_changed = must_update(item, cleaned_data)
    force_update = is_default and not item.get("is_default")
    if not item_changed and not force_update:
        return False, item, dict(before=item, after=item)

    # update object
    id = item.get("id")
    if item_changed:
        response_json = client.put(f"{ENDPOINT}/{id}/", cleaned_data).json
    if force_update:
        response_json = client.post(
            f"{ENDPOINT}/{id}/", {}, query={"op": "set_default"}
        ).json
    return True, response_json, dict(before=item, after=response_json)


def ensure_absent(module, client: Client):
    domain_name = module.params["name"]

    items = client.get(ENDPOINT).json
    item = get_match(items, "name", domain_name)
    if not item:
        return False, None, dict(before={}, after={})

    id = item.get("id")
    client.delete(f"{ENDPOINT}/{id}/")
    return True, None, dict(before=item, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        record, changed, diff = ensure_present(module, client)
    elif module.params["state"] == "absent":
        record, changed, diff = ensure_absent(module, client)
    return changed, record, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str", required=True, choices=["present", "absent"]
            ),
            name=dict(type="str", required=True),
            ttl=dict(type="int", required=False),
            authoritative=dict(type="bool", required=False),
            is_default=dict(type="bool", required=False, choices=[True]),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        record, changed, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as ex:
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
