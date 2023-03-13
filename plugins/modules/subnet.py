#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: subnet

author:
  - Jure Medvesek (@juremedvesek)
short_description: Edit subnets.
description:
  - Plugin provides a resource to manage MAAS subnets.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description: Should subnet be present or absent.
    type: str
    choices:
      - present
      - absent
    required: true
  name:
    description: The name of subnet that we want to be present or absent.
    type: str
    required: true
  cidr:
    description: The network CIDR for this subnet.
    type: str
  rdns_mode:
    description:
      - How reverse DNS is handled for this subnet. One of
      - "c(0) Disabled: No reverse zone is created."
      - "c(1) Enabled: Generate reverse zone."
      - "c(2) RFC2317: Extends '1' to create the necessary parent zone with the appropriate CNAME resource records for the network,
        if the the network is small enough to require the support described in RFC2317."
    type: int
    choices: [0, 1, 2]
    required: false
  allow_dns:
    description: Configure MAAS DNS to allow DNS resolution from this subnet.
    type: bool
    required: false
  allow_proxy:
    description: Configure maas-proxy to allow requests from this subnet.
    type: bool
    required: false
  dns_servers:
    description: List of DNS servers for this subnet.
    type: list
    elements: str
  fabric:
    description: Fabric for the subnet. Defaults to the fabric the provided VLAN belongs to, or defaults to the default fabric.
    type: str
    required: false
  gateway_ip:
    description: The gateway IP address for this subnet.
    type: str
    required: false
  vlan:
    description:
      - VLAN this subnet belongs to. Defaults to the default VLAN for the provided fabric or defaults to the default VLAN
        in the default fabric (if unspecified).
    type: str
    required: false
  ip_ranges:
    description: IP ranges that should be set on subnet
    type: list
    required: false
    elements: dict
    suboptions:
      type:
        type: str
        choices: ['reserved', 'dynamic']
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
"""

EXAMPLES = r"""
- name: Add subnet IP range
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

from itertools import groupby

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client

ENDPOINT = "/api/2.0/subnets/"


def clean_data(data: dict):
    return {key: value for key, value in data.items() if value is not None}


def get_match(items, key, value):
    return next((item for item in items if item.get(key) == value), None)


def get_match_or_fail(items, key, value, attribute_name):
    result = get_match(items, key, value)
    if result:
        return result

    available_items = ", ".join(x[key] for x in items)
    raise errors.MaasError(
        f"Can not find matching { attribute_name }. Options are [{ available_items }]"
    )


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
    for key, value in new_data.items():
        if old_data.get(key) != value:
            #  raise Exception(f"{key}: {old_data.get(key)} != {value}")
            return True
    return False


def map_item(module, client: Client, fail_if_empty, key, endpoint):
    item_name = module.params[key]

    # map subitem
    items = client.get(endpoint).json
    if fail_if_empty:
        return get_match_or_fail(items, "name", item_name, key)
    return get_match(items, "name", item_name)


def get_ip_ranges(client):
    def key_function(item):
        return item["subnet"]

    ip_ranges = client.get("/api/2.0/ipranges/").json
    data = [
        {
            "subnet": ip_range["subnet"]["name"],
            "id": ip_range["id"],
            "data": {
                "type": ip_range["type"],
                "start_ip": ip_range["start_ip"],
                "end_ip": ip_range["end_ip"],
            },
        }
        for ip_range in ip_ranges
    ]

    sorted_data = sorted(data, key=key_function)

    grouped = {
        k: [(v["id"], v["data"]) for v in g]
        for k, g in groupby(sorted_data, key_function)
    }
    return grouped


class IpRangeUpdater:
    @staticmethod
    def ranges_to_update(client, subnet, ip_ranges):
        if subnet is None:
            return [], ip_ranges

        ranges_to_delete = []
        ranges_to_add = []

        old_ranges = get_ip_ranges(client).get(subnet["name"]) or []

        for ip_range_id, data in old_ranges:
            if any(ip_range == data for ip_range in ip_ranges):
                continue
            ranges_to_delete.append(ip_range_id)

        simplified = [v for k, v in old_ranges]
        for ip_range in ip_ranges:
            if any(ip_range == old_range for old_range in simplified):
                continue
            ranges_to_add.append(ip_range)

        return old_ranges, (ranges_to_delete, ranges_to_add)

    @staticmethod
    def update(client, subnet, actions):
        to_delete, to_add = actions
        IpRangeUpdater.remove_ip_ranges(client, to_delete)
        IpRangeUpdater.add_ip_ranges(client, to_add, subnet["id"])
        result = get_ip_ranges(client).get(subnet["name"])
        return [v for k, v in result]

    @staticmethod
    def add_ip_ranges(client: Client, ip_ranges, subnet_id):
        for ip_range in ip_ranges:
            ip_range["subnet"] = subnet_id
            client.post("/api/2.0/ipranges/", ip_range)

    @staticmethod
    def remove_ip_ranges(client: Client, ip_range_ids):
        for ip_range_id in ip_range_ids:
            client.delete(f"/api/2.0/ipranges/{ip_range_id}/")


def ensure_present(module, client: Client):
    vlan_name = module.params["vlan"]
    ip_ranges = module.params["ip_ranges"] or []

    fabric = map_item(
        module, client, vlan_name is not None, "fabric", "/api/2.0/fabrics/"
    )
    vlan = (
        get_match_or_fail(fabric["vlans"], "name", vlan_name, "vlan")
        if vlan_name
        else None
    )
    dns_servers = ",".join(module.params.get("dns_servers") or [])

    data = {
        "name": module.params["name"],
        "cidr": module.params["cidr"],
        "fabric": fabric["id"] if fabric else None,
        "vlan": vlan["id"] if vlan else None,
        "rdns_mode": module.params["rdns_mode"],
        "allow_dns": module.params["allow_dns"],
        "allow_proxy": module.params["allow_proxy"],
        "gateway_ip": module.params["gateway_ip"] or None,
        "dns_servers": dns_servers,
    }
    cleaned_data = clean_data(data)

    # find a match on server, if none, create new object
    items = client.get(ENDPOINT).json
    item = get_match(items, "name", module.params["name"])
    if not item:
        response_json = client.post(ENDPOINT, cleaned_data).json

        # Add IP ranges to new subnet
        if ip_ranges:
            response_json["ip_ranges"] = IpRangeUpdater.update(
                client, response_json, ([], ip_ranges)
            )

        # map to Ansible module fields
        response_json["fabric"] = response_json.get("vlan", {}).get("fabric")
        response_json["vlan"] = response_json.get("vlan", {}).get("name")
        return True, response_json, dict(before={}, after=response_json)

    # check if update is needed at all
    old_vlan = item.get("vlan", {})
    item["fabric"] = item.get("vlan", {}).get("fabric_id")
    item["vlan"] = item.get("vlan", {}).get("id")
    item["dns_servers"] = ",".join(item.get("dns_servers", []))
    item_changed = must_update(item, cleaned_data)
    item["dns_servers"] = item["dns_servers"].split(",")
    item["vlan"] = old_vlan["name"]
    item["fabric"] = old_vlan["fabric"]

    old_ranges, ranges_to_update = IpRangeUpdater.ranges_to_update(
        client, item, ip_ranges
    )
    item["ip_ranges"] = [v for k, v in old_ranges]
    if not item_changed and ranges_to_update == ([], []):
        return False, item, dict(before=item, after=item)

    # update object
    id = item.get("id")
    if item_changed:
        response_json = client.put(f"{ENDPOINT}/{id}/", cleaned_data).json
    else:
        response_json = client.get(f"{ENDPOINT}/{id}/").json

    response_json["fabric"] = response_json.get("vlan", {}).get("fabric")
    response_json["vlan"] = response_json.get("vlan", {}).get("name")
    response_json["ip_ranges"] = IpRangeUpdater.update(
        client, response_json, ranges_to_update
    )

    return True, response_json, dict(before=item, after=response_json)


def ensure_absent(module, client: Client):
    key = "name"

    items = client.get(ENDPOINT).json
    item = get_match(items, key, module.params[key])
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
    ip_range_spec = dict(
        type=dict(type="str", required=True, choices=["reserved", "dynamic"]),
        start_ip=dict(type="str", required=True),
        end_ip=dict(type="str", required=True),
    )

    ip_range_list_spec = dict(
        type="list", elements="dict", options=ip_range_spec
    )

    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str", required=True, choices=["present", "absent"]
            ),
            name=dict(type="str", required=True),
            cidr=dict(type="str"),
            fabric=dict(type="str"),
            vlan=dict(type="str"),
            rdns_mode=dict(type="int", choices=[0, 1, 2]),
            allow_dns=dict(type="bool"),
            allow_proxy=dict(type="bool"),
            gateway_ip=dict(type="str"),
            dns_servers=dict(type="list", elements="str"),
            ip_ranges=ip_range_list_spec,
        ),
        required_if=[("state", "present", ("cidr", "ip_ranges"))],
        required_by={"vlan": "fabric"},
    )

    try:
        client = get_oauth1_client(module.params)
        record, changed, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as ex:
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
