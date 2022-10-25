#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: space

author:
  - Polona Mihalič (@PolonaM)
short_description: Creates, updates or deletes MAAS network space.
description:
  - If I(state) is C(present) and I(name) is not found, creates new network space.
  - If I(state) is C(present) and I(name) is found, updates an existing network space.
  - If I(state) is C(absent) selected network space is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the network space.
    choices: [ present, absent ]
    type: str
    required: True
  name:
    description:
      - Name of the network space to be created, updated or deleted.
      - Serves as unique identifier of the network space.
    type: str
    required: True
  new_name:
    description:
      - New name of the existing network space to be updated.
    type: str
  description:
    description:
      - Description of the new space.
    type: str
"""

EXAMPLES = r"""
- name: Create newtork space
  canonical.maas.space:
    state: present
    name: space-name
    description: My new newtork space

- name: Update network space
  canonical.maas.space:
    state: present
    name: space-name
    new_name: updated-space
    description: My new newtork space updated

- name: Remove network space
  canonical.maas.space:
    state: absent
    name: updated-space
"""

RETURN = r"""
record:
  description:
    - Added space.
  returned: success
  type: dict
  sample:
    name=None
    id=None
    vlans=[]
    resource_uri=None
    subnets=[]
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.space import Space


def data_for_create_space(module):
    data = {}
    data["name"] = module.params["name"]
    if module.params["description"]:
        data["description"] = module.params["description"]
    return data


def create_space(module, client: Client):
    data = data_for_create_space(module)
    space = Space.create(client, data)
    return (
        True,
        space.to_ansible(),
        dict(before={}, after=space.to_ansible()),
    )


def data_for_update_space(module, space):
    data = {}
    if module.params["new_name"]:
        if space.name != module.params["new_name"]:
            data["name"] = module.params["new_name"]
    if module.params["description"]:  # description is not returned
        data["description"] = module.params["description"]
    return data


def update_space(module, client: Client, space):
    data = data_for_update_space(module, space)
    if data:
        updated_space_maas_dict = space.update(client, data)
        space_after = Space.from_maas(updated_space_maas_dict)
        return (
            True,
            space_after.to_ansible(),
            dict(before=space.to_ansible(), after=space_after.to_ansible()),
        )
    return (
        False,
        space.to_ansible(),
        dict(before=space.to_ansible(), after=space.to_ansible()),
    )


def delete_space(module, client: Client):
    space = Space.get_by_name(module, client, must_exist=False)
    if space:
        space.delete(client)
        return True, dict(), dict(before=space.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        space = Space.get_by_name(module, client)
        if space:
            return update_space(module, client, space)
        return create_space(module, client)
    if module.params["state"] == "absent":
        return delete_space(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            name=dict(type="str", required=True),
            new_name=dict(type="str"),
            description=dict(type="str"),
        ),
    )

    try:
        cluster_instance = module.params["cluster_instance"]
        host = cluster_instance["host"]
        consumer_key = cluster_instance["customer_key"]
        token_key = cluster_instance["token_key"]
        token_secret = cluster_instance["token_secret"]

        client = Client(host, token_key, token_secret, consumer_key)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
