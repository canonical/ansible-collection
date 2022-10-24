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
short_description: List DNS domains.
description:
  - Plugin returns information about available DNS domains.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
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
    description: Domain name
    type: str
    required: true
  authoritative:
    type: bool
    description: ""
  ttl:
    type: int
    description: Time to live. If not set, default value will be used.
  is_default:
    type: bool
    description: Should this domain be set as defult.
"""

EXAMPLES = r"""
- name: List domains
  cannonical.maas.dns_domain_info:
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
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client


ENDPOINT = "/api/2.0/domains/"


def clean_data(data: dict):
    return {key: value for key, value in data.items() if value is not None}


def get_match(items, key, value):
    for item in items.json:
        if item.get(key) == value:
            return item
    return None


def must_update(old_data, new_data):
    for key, value in new_data.items():
        if old_data.get(key) != value:
            return True
    return False


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

    # find a match on server, if none, create new object
    items = client.get(ENDPOINT)
    item = get_match(items, "name", domain_name)
    if not item:
        return client.post(ENDPOINT, cleaned_data), True

    # check if update is needed at all
    force_update = is_default and not item.get("is_default")
    if not must_update(item, cleaned_data) and not force_update:
        return item, False

    # update object
    id = item.get("id")
    if must_update(item, cleaned_data):
        response = client.put(f"{ENDPOINT}/{id}/", cleaned_data)
    if force_update:
        response = client.post(f"{ENDPOINT}/{id}/", {}, query={"op", "set_default"})
    return response.json, True


def ensure_absent(module, client: Client):
    domain_name = module.params["name"]

    items = client.get(ENDPOINT)
    match = get_match(items, "name", domain_name)
    if not match:
        return None, False

    client.delete(f"{ENDPOINT}/{id}/")
    return None, True


def run(module, client: Client):
    if module.params["state"] == "present":
        record, changed = ensure_present(module, client)
    elif module.params["state"] == "absent":
        record, changed = ensure_absent(module, client)
    return record, changed


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(type="str", required=True, choices=["present", "absent"]),
            name=dict(type="str", required=True),
            ttl=dict(type="int", required=False),
            authoritative=dict(type="bool", required=False),
            is_default=dict(type="bool", required=False),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        record, changed = run(module, client)
        module.exit_json(changed=changed, record=record)
    except errors.MaasError as ex:
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
