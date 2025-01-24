#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: dhcp_snippet

author:
  - Arkadiy Shinkarev (@k3nny0ne)
short_description: Creates, updates or deletes DHCP Snippets.
description:
  - If I(state) is C(present) and I(name) is provided but not found,
    new DHCP Snippet with specified name - I(name) is created
    with specified content - I(value).
  - If I(state) is C(present) and I(name) is found, updates an existing DHCP Snippet.
  - If I(state) is C(absent) DHCP Snippet selected by I(name) is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the DHCP Snippet.
    choices: [ present, absent ]
    type: str
    required: True
  name:
    description:
      - Name of the DHCP Snippet.
      - Serves as unique identifier of the snippet.
    type: str
    required: True
  value:
    description:
      - The snippet of config inserted into dhcpd.conf.
      - Required when creating new DHCP Snippet.
    type: str
    required: True
  description:
    description:
      - A description of what the snippet does.
    type: str
  enabled:
    description:
      - Whether or not the snippet is currently enabled.
    type: bool
  subnet:
    description:
      - The subnet this snippet applies to.
    type: str
  global_snippet:
    description:
      - Whether or not this snippet is to be applied globally.
    type: bool
"""

EXAMPLES = r"""
- name: Create DHCP Snippet
  canonical.maas.dhcp_snippet:
    state: present
    name: default-route
    value: "option routers 192.168.1.1;"
    description: Default route
    subnet: 172.16.31.0/24
    enabled: true

- name: Update DHCP Snippet using name as identifier
  canonical.maas.dhcp_snippet:
    state: present
    name: default-route
    value: "option routers 192.168.2.1;"

- name: Remove DHCP Snippet using name as identifier
  canonical.maas.dhcp_snippet:
    state: absent
    name: default-route
"""

RETURN = r"""
record:
  description:
    - Created or updated DHCP Snippet.
  returned: success
  type: dict
  sample:
    name: default-route
    description: "Default route"
    enabled: true
    subnet: 5003
    value: "option routers 192.168.2.1;"
    id: 4
    global_snippet: false
    resource_uri: /MAAS/api/2.0/dhcp-snippets/4/
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.dhcp_snippet import DhcpSnippet
from ..module_utils.cluster_instance import get_oauth1_client


def data_for_create_dhcp_snippet(module):
    data = {}
    data["name"] = module.params["name"]  # required
    data["value"] = module.params["value"]  # required
    if module.params["description"]:
        data["description"] = module.params["description"]
    if module.params["enabled"] is not None:
        data["enabled"] = module.params["enabled"]
    if module.params["subnet"]:
        data["subnet"] = module.params["subnet"]
    if module.params["global_snippet"] is not None:
        data["global_snippet"] = module.params["global_snippet"]
    return data


def create_dhcp_snippet(module, client: Client):
    data = data_for_create_dhcp_snippet(module)
    dhcp_snippet = DhcpSnippet.create(client, data)
    return (
        True,
        dhcp_snippet.to_ansible(),
        dict(before={}, after=dhcp_snippet.to_ansible()),
    )


def data_for_update_dhcp_snippet(module, dhcp_snippet):
    data = {}

    if module.params["name"]:
        if dhcp_snippet.name != module.params["name"]:
            data["name"] = module.params["name"]
    if module.params["value"]:
        if dhcp_snippet.value != module.params["value"]:
            data["value"] = module.params["value"]
    if module.params["description"]:
        if dhcp_snippet.description != module.params["description"]:
            data["description"] = module.params["description"]
    if module.params["enabled"] is not None:
        if dhcp_snippet.enabled != module.params["enabled"]:
            data["enabled"] = module.params["enabled"]
    if module.params["subnet"]:
        if (
            dhcp_snippet.subnet
            and dhcp_snippet.subnet["name"] != module.params["subnet"]
        ):
            data["subnet"] = module.params["subnet"]
    if module.params["global_snippet"] is not None:
        if dhcp_snippet.global_snippet != module.params["global_snippet"]:
            data["global_snippet"] = module.params["global_snippet"]
            data["value"] = module.params["value"]
            if not module.params["global_snippet"]:
                data["subnet"] = module.params["subnet"]

    return data


def update_dhcp_snippet(module, client: Client, dhcp_snippet: DhcpSnippet):
    data = data_for_update_dhcp_snippet(module, dhcp_snippet)
    if data:
        updated = dhcp_snippet.update(module, client, data)
        after = DhcpSnippet.from_maas(updated)
        return (
            True,
            after.to_ansible(),
            dict(before=dhcp_snippet.to_ansible(), after=after.to_ansible()),
        )
    return (
        False,
        dhcp_snippet.to_ansible(),
        dict(before=dhcp_snippet.to_ansible(), after=dhcp_snippet.to_ansible()),
    )


def delete_dhcp_snippet(module, client: Client):
    dhcp_snippet = DhcpSnippet.get_by_name(module, client, must_exist=False)
    if dhcp_snippet:
        dhcp_snippet.delete(module, client)
        return True, dict(), dict(before=dhcp_snippet.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        dhcp_snippet = DhcpSnippet.get_by_name(module, client, must_exist=False)
        if dhcp_snippet:
            return update_dhcp_snippet(module, client, dhcp_snippet)
        return create_dhcp_snippet(module, client)
    if module.params["state"] == "absent":
        return delete_dhcp_snippet(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(type="str", choices=["present", "absent"], required=True),
            name=dict(type="str", required=True),
            value=dict(type="str", required=True),
            description=dict(type="str"),
            enabled=dict(type="bool"),
            subnet=dict(type="str"),
            global_snippet=dict(type="bool"),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
