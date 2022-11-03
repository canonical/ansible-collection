#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: fabric

author:
  - Polona Mihalič (@PolonaM)
short_description: Creates, updates or deletes MAAS network fabric.
description:
  - If I(state) is C(present) and I(name) is not present or not found, creates new network fabric.
  - If I(state) is C(present) and I(name) is found, updates an existing network fabric.
  - If I(state) is C(absent) selected network fabric is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the network fabric.
    choices: [ present, absent ]
    type: str
    required: True
  name:
    description:
      - Name of the network fabric to be created, updated or deleted.
      - Serves as unique identifier of the network fabric to be updated.
    type: str
  new_name:
    description:
      - New name of the existing network fabric to be updated.
    type: str
  description:
    description:
      - Description of the fabric.
    type: str
  class_type:
    description:
      - Class type of the fabric.
    type: str
"""

EXAMPLES = r"""
- name: Create newtork fabric
  canonical.maas.fabric:
    state: present
    name: fabric-name
    class_type: class_type
    description: My new newtork fabric

- name: Update network fabric
  canonical.maas.fabric:
    state: present
    name: fabric-name
    new_name: updated-fabric
    description: My new newtork fabric updated

- name: Remove network fabric
  canonical.maas.fabric:
    state: absent
    name: updated-fabric
"""

RETURN = r"""
record:
  description:
    - Created or updated fabric.
  returned: success
  type: dict
  sample:
    class_type: null
    id: 7
    name: fabric-7
    resource_uri: /MAAS/api/2.0/fabrics/7/
    vlans:
    - dhcp_on: false
      external_dhcp: null
      fabric: fabric-0
      fabric_id: 0
      id: 5001
      mtu: 1500
      name: untagged
      primary_rack: null
      relay_vlan: null
      resource_uri: /MAAS/api/2.0/vlans/5001/
      secondary_rack: null
      space: undefined
      vid: 0
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.fabric import Fabric


def data_for_create_fabric(module):
    data = {}
    if module.params["name"]:
        data["name"] = module.params["name"]
    if module.params["description"]:
        data["description"] = module.params["description"]
    if module.params["class_type"]:
        data["class_type"] = module.params["class_type"]
    return data


def create_fabric(module, client: Client):
    data = data_for_create_fabric(module)
    fabric = Fabric.create(client, data)
    return (
        True,
        fabric.to_ansible(),
        dict(before={}, after=fabric.to_ansible()),
    )


def data_for_update_fabric(module, fabric):
    data = {}
    if module.params["new_name"]:
        if fabric.name != module.params["new_name"]:
            data["name"] = module.params["new_name"]
    if module.params["class_type"]:
        if fabric.class_type != module.params["class_type"]:
            data["class_type"] = module.params["class_type"]
    if module.params["description"]:  # TODO: update when description is returned
        data["description"] = module.params["description"]
    return data


def update_fabric(module, client: Client, fabric):
    data = data_for_update_fabric(module, fabric)
    if data:
        updated_fabric_maas_dict = fabric.update(client, data)
        fabric_after = Fabric.from_maas(updated_fabric_maas_dict)
        return (
            True,
            fabric_after.to_ansible(),
            dict(before=fabric.to_ansible(), after=fabric_after.to_ansible()),
        )
    return (
        False,
        fabric.to_ansible(),
        dict(before=fabric.to_ansible(), after=fabric.to_ansible()),
    )


def delete_fabric(module, client: Client):
    fabric = Fabric.get_by_name(module, client, must_exist=False)
    if fabric:
        fabric.delete(client)
        return True, dict(), dict(before=fabric.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        if not module.params["name"]:
            return create_fabric(module, client)
        else:
            fabric = Fabric.get_by_name(module, client)
            if fabric:
                return update_fabric(module, client, fabric)
            return create_fabric(module, client)
    if module.params["state"] == "absent":
        return delete_fabric(module, client)


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
            class_type=dict(type="str"),
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
