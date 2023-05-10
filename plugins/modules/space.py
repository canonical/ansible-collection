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
  - If I(state) is C(present) and I(name) is not present or not found, creates new network space.
  - If I(state) is C(present) and I(name) is found, updates an existing network space.
  - If I(state) is C(absent) selected network space is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - maas.maas.cluster_instance
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
      - Serves as unique identifier of the network space to be updated.
    type: str
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
  maas.maas.space:
    state: present
    name: space-name
    description: My new newtork space

- name: Update network space
  maas.maas.space:
    state: present
    name: space-name
    new_name: updated-space
    description: My new newtork space updated

- name: Remove network space
  maas.maas.space:
    state: absent
    name: updated-space
"""

RETURN = r"""
record:
  description:
    - Created or updated network space.
  returned: success
  type: dict
  sample:
    id: -1
    name: undefined
    resource_uri: /MAAS/api/2.0/spaces/-1/
    subnets:
    - name: 10.10.10.0/24
      description: ""
      vlan:
        vid: 0
        mtu: 1500
        dhcp_on: true
        external_dhcp: null
        relay_vlan: null
        fabric: fabric-1
        id: 5002
        space: undefined
        fabric_id: 1
        name: untagged
        primary_rack: kwxmgm
        secondary_rack: null
        resource_uri: /MAAS/api/2.0/vlans/5002/
      cidr: 10.10.10.0/24
      rdns_mode: 2
      gateway_ip: 10.10.10.1
      dns_servers: []
      allow_dns: true
      allow_proxy: true
      active_discovery: false
      managed: true
      disabled_boot_architectures: []
      id: 2
      space: undefined
      resource_uri: /MAAS/api/2.0/subnets/2/
    vlans:
    - vid: 0
      mtu: 1500
      dhcp_on: true
      external_dhcp: null
      relay_vlan: null
      fabric: fabric-1
      id: 5002
      space: undefined
      fabric_id: 1
      name: untagged
      primary_rack: kwxmgm
      secondary_rack: null
      resource_uri: /MAAS/api/2.0/vlans/5002/
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.space import Space


def data_for_create_space(module):
    data = {}
    if module.params["name"]:
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
        if not module.params["name"]:
            return create_space(module, client)
        else:
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
            name=dict(type="str"),
            new_name=dict(type="str"),
            description=dict(type="str"),
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
