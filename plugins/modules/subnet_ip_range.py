#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: subnet_ip_range

author:
  - Jure Medvesek (@juremedvesek)
short_description: Edit subnets IP range.
description:
  - Plugin provides a resource to manage MAAS IP ranges.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description: Should IP range be present or absent.
    type: str
    choices:
      - present
      - absent
    required: true
  subnet:
    description: The name of subnet that we attach IP range to.
    type: str
    required: true
  type:
    type: str
    description: Type of IP range. Options are dynamic, reserved, ...
    required: true
  start_ip:
    type: str
    description: Start of IP range.
    required: true
  end_ip:
    type: str
    description: End of IP range
    required: true
  comment:
    type: str
    description: Free text
"""

EXAMPLES = r"""
- name: Add subnet IP range
  canonical.maas.dns_domain_info:
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

ENDPOINT = "/api/2.0/ipranges/"


def clean_data(data: dict):
    return {key: value for key, value in data.items() if value is not None}


def get_match(items, key, value):
    return next((item for item in items if item.get(key) == value), None)


def get_complex_match(items, conditions: dict):
    for item in items:
        complex_conditions = {
            k: v for k, v in conditions.items() if not isinstance(k, str)
        }

        is_simple_match = all(
            item[k] == v
            for k, v in conditions.items()
            if k not in complex_conditions
        )
        is_complex_match = all(
            item[k1][k2] == v for (k1, k2), v in complex_conditions.items()
        )
        if is_simple_match and is_complex_match:
            return item

    return None


def must_update(old_data, new_data):
    return any(old_data.get(key) != value for key, value in new_data.items())


def ensure_present(module, client: Client):
    subnet_name = module.params["subnet"]

    # map subnet to its Id
    subnets = client.get("/api/2.0/subnets/").json
    subnet = get_match(subnets, "name", subnet_name)
    if not subnet:
        available_subnets = ", ".join(x["name"] for x in subnets)
        raise errors.MaasError(
            f"Can not find matching subnet. Options are [{ available_subnets }]"
        )

    compound_key = {
        ("subnet", "id"): subnet["id"],
        "type": module.params["type"],
        "start_ip": module.params["start_ip"],
        "end_ip": module.params["end_ip"],
    }

    data = {
        "subnet": subnet["id"],
        "type": module.params["type"],
        "start_ip": module.params["start_ip"],
        "end_ip": module.params["end_ip"],
        "comment": module.params["comment"],
    }
    cleaned_data = clean_data(data)

    # module.params["name"] not set - creating new item and return
    # Here name is obligatory, so this case is not reached

    # find a match on server, if none, create new object
    items = client.get(ENDPOINT).json
    item = get_complex_match(items, compound_key)
    if not item:
        response_json = client.post(ENDPOINT, cleaned_data).json
        return True, response_json, dict(before={}, after=response_json)

    # check if update is needed at all
    item["subnet"] = item["subnet"]["id"]
    item_changed = must_update(item, cleaned_data)
    item["subnet"] = subnet["name"]

    if not item_changed:
        return False, item, dict(before=item, after=item)

    # update object
    id = item.get("id")
    if item_changed:
        response_json = client.put(f"{ENDPOINT}/{id}/", cleaned_data).json
        response_json["subnet"] = subnet["name"]

    return True, response_json, dict(before=item, after=response_json)


def ensure_absent(module, client: Client):
    compound_key = {
        ("subnet", "name"): module.params["subnet"],
        "type": module.params["type"],
        "start_ip": module.params["start_ip"],
        "end_ip": module.params["end_ip"],
    }

    items = client.get(ENDPOINT).json
    item = get_complex_match(items, compound_key)
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
            subnet=dict(type="str", required=True),
            type=dict(type="str", required=True),
            start_ip=dict(type="str", required=True),
            end_ip=dict(type="str", required=True),
            comment=dict(type="str", required=False),
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
