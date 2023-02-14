#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
module: dns_record

author:
  - Jure Medvesek (@juremedvesek)
short_description: Edit DNS records.
description:
  - Plugin provides a resource to manage MAAS DNS records.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description: Should record be present or absent.
    type: str
    choices:
      - present
      - absent
    required: true
  type:
    description: The DNS record type
    type: str
    choices: [A/AAAA, CNAME, MX, NS, SRV, SSHFP, TXT]
  fqdn:
    description: The fully qualified domain name of the new DNS record.
    type: str
    required: false
  domain:
    description: Domain name.
    type: str
    required: false
  name:
    description: Hostname (without domain).
    type: str
    required: false
  ttl:
    type: int
    description: The TTL for the DNS record.
  data:
    description: The data set for the new DNS record.
    type: str
"""

EXAMPLES = r"""
- name: Add domain
  cannonical.maas.dns_record:
    cluster_instance:
      host: ...
      token_key: ...
      token_secret: ...
      customer_key: ...
    state: present
    domain: maas
    name: test2
    data: 10.0.0.1 10.0.0.2
    ttl: 5
    type: A/AAAA
"""

RETURN = r"""
record:
  description:
    - Added DNS record.
  returned: success
  type: dict
  sample:
    data: 10.0.0.1 10.0.0.2
    fqdn: test2.maas
    ttl: 5
    type: A/AAAA
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.dns_record import to_ansible


ENDPOINT_A = "/api/2.0/dnsresources/"
ENDPOINT_OTHER = "/api/2.0/dnsresourcerecords/"


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


def must_update(old_data, new_data):
    return any(old_data.get(key) != value for key, value in new_data.items())


def ensure_present(module, client: Client):
    # extract all data from ansible task
    if module.params["fqdn"]:
        resource_name = module.params["fqdn"]
        name, domain = resource_name.rsplit(".", 1)
    else:
        name = module.params["name"]
        domain = module.params["domain"]
        resource_name = f"{name}.{domain}"

    dns_type = module.params["type"]
    is_a = dns_type == "A/AAAA"
    endpoint = ENDPOINT_A if is_a else ENDPOINT_OTHER

    common_reperesentation = {
        "name": name,
        "domain": domain,
        "ttl": module.params["ttl"],
        "data": module.params["data"],
        "type": module.params["type"],
    }

    data = (
        {
            "name": common_reperesentation["name"],
            "domain": common_reperesentation["domain"],
            "address_ttl": common_reperesentation["ttl"],
            "ip_addresses": common_reperesentation["data"],
        }
        if is_a
        else {
            "name": common_reperesentation["name"],
            "domain": common_reperesentation["domain"],
            "rrtype": common_reperesentation["type"],
            "rrdata": common_reperesentation["data"],
        }
    )
    cleaned_data = clean_data(data)

    # check if domain exist so we can print nicer errors - better than 404 Not found.
    items = client.get("/api/2.0/domains/").json
    item = get_match_or_fail(items, "name", domain, "domain " + domain)

    # find a match on server, if none, create new object
    items = client.get(ENDPOINT_A).json
    item = get_match(items, "fqdn", resource_name)

    if not item:
        response_json = client.post(endpoint, cleaned_data).json
        as_ansible = to_ansible(response_json, not is_a)[0]
        return True, as_ansible, dict(before={}, after=as_ansible)

    # check if update is needed at all
    items_as_ansible = to_ansible(item)
    if len(items_as_ansible) != 1:
        raise errors.MaasError(
            "Case not covered yet. Can be reached with A and TXT objects"
        )
    item_as_ansible = items_as_ansible[0]

    item_changed = must_update(item_as_ansible, common_reperesentation)
    if not item_changed:
        return (
            False,
            item_as_ansible,
            dict(before=item_as_ansible, after=item_as_ansible),
        )

    # update only if allowed operation
    if item_as_ansible["type"] != dns_type:
        old_type = item_as_ansible["type"]
        raise errors.MaasError(
            f"Type of DNS record may not be changed. Change from {old_type} to {dns_type}."
        )

    cleaned_data.pop("name")
    cleaned_data.pop("domain")
    id = item_as_ansible["id"]
    response_json = client.put(f"{endpoint}/{id}/", cleaned_data).json
    response_as_ansible = to_ansible(response_json, not is_a)[0]

    return (
        True,
        response_as_ansible,
        dict(before=item_as_ansible, after=response_as_ansible),
    )


def ensure_absent(module, client: Client):
    resource_name = (
        module.params["fqdn"] or f"{module.params['name']}.{module.params['domain']}"
    )

    items = client.get(ENDPOINT_A).json

    item = get_match(items, "fqdn", resource_name)
    if not item:
        return False, None, dict(before={}, after={})

    id = item.get("id")
    client.delete(f"{ENDPOINT_A}/{id}/")

    formated = to_ansible(item)
    return True, None, dict(before=formated[0] if formated else {}, after={})


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
            state=dict(type="str", required=True, choices=["present", "absent"]),
            fqdn=dict(type="str"),
            name=dict(type="str"),
            domain=dict(type="str"),
            type=dict(
                type="str",
                choices=["A/AAAA", "CNAME", "MX", "NS", "SRV", "SSHFP", "TXT"],
            ),
            data=dict(type="str"),
            ttl=dict(type="int", required=False),
        ),
        required_if=[("state", "present", ("type", "data"), False)],
        required_together=[
            ("name", "domain"),
        ],
        mutually_exclusive=[
            ("fqdn", "name"),
        ],
    )

    try:
        client = get_oauth1_client(module.params)
        record, changed, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as ex:
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
