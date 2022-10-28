#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible_collections.canonical.maas.plugins.module_utils.fabric import Fabric

__metaclass__ = type

DOCUMENTATION = r"""
module: vlan

author:
  - Polona Mihalič (@PolonaM)
short_description: Creates, updates or deletes MAAS VLANs.
description:
  - If I(state) is C(present) and I(vlan_name) is not present or not found, new VLAN with specified traffic segregation ID - I(vid)
    is created on a specified fabric - I(fabric_name).
  - If I(state) is C(present) and I(vlan_name) is found, updates an existing VLAN.
  - If I(state) is C(absent) selected VLAN is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the VLAN.
    choices: [ present, absent ]
    type: str
    required: True
  fabric_name:
    description:
      - Name of the fabric where VLAN is created, updated or deleted.
      - Serves as unique identifier of the fabric.
      - If fabric is not found the task will FAIL.
    type: str
    required: True
  vid:
    description:
      - The traffic segregation ID for the new VLAN.
    type: str
    required: True
  vlan_name:
    description:
      - The name of the new VLAN.
      - This is computed if it's not set.
    type: str
  new_vlan_name:
    description:
      - New name of the existing VLAN to be updated.
    type: str
  description:
    description:
      - Description of the new VLAN.
    type: str
  mtu:
    description:
      - The MTU to use on the VLAN.
      - This is computed if it's not set.
    type: int
  dhcp_on:
    description:
      - Whether or not DHCP should be managed on the new VLAN.
      - This is computed if it's not set.
    type: bool
  space:
    description:
      - The network space this VLAN should be placed in.
      - Passing in an empty string (or the string undefined) will cause the VLAN to be placed in the undefined space.
    type: str
"""

EXAMPLES = r"""
- name: Create VLAN
  canonical.maas.vlan:
    state: present
    fabric_name: fabric-10
    vid: 0
    vlan_name: vlan-10
    description: VLAN on fabric-10
    mtu: 1500
    dhcp_on: false
    space: network-space-10

- name: Update VLAN
  canonical.maas.space:
    state: present
    fabric_name: fabric-10
    vid: 0
    vlan_name: vlan-10
    new_vlan_name: vlan-10-updated
    description: VLAN on fabric-10 updated
    mtu: 2000
    dhcp_on: true
    space: network-space-10

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
    dhcp_on: false
    external_dhcp: null
    fabric: fabric-10
    fabric_id: 10
    id: 5014
    mtu: 1500
    name: untagged
    primary_rack: null
    relay_vlan: null
    resource_uri: /MAAS/api/2.0/vlans/5014/
    secondary_rack: null
    space: undefined
    vid: 0
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.vlan import Vlan


def data_for_create_vlan(module):
    data = {}
    data["vid"] = module.params["vid"]  # required
    if module.params["vlan_name"]:
        data["name"] = module.params["vlan_name"]
    if module.params["description"]:
        data["description"] = module.params["description"]
    if module.params["mtu"]:
        data["mtu"] = module.params["mtu"]
    if module.params["space"]:
        data["space"] = module.params["space"]
    return data


def create_vlan(module, client: Client, fabric_id):
    data = data_for_create_vlan(module)
    vlan = Vlan.create(client, fabric_id, data)
    if module.params["dhcp_on"]:  # this parameter can only be set with put
        data = data_for_update_vlan(module, fabric_id, vlan)
        vlan.update(client, fabric_id, data)
    return (
        True,
        vlan.to_ansible(),
        dict(before={}, after=vlan.to_ansible()),
    )


def data_for_update_vlan(module, vlan):
    data = {}
    if module.params["new_vlan_name"]:
        if vlan.name != module.params["new_vlan_name"]:
            data["name"] = module.params["new_vlan_name"]
    if module.params["description"]:  # description is not returned
        data["description"] = module.params["description"]
    if module.params["mtu"]:
        if vlan.mtu != module.params["mtu"]:
            data["mtu"] = module.params["mtu"]
    if module.params["dhcp_on"]:
        if vlan.dhcp_on != module.params["dhcp_on"]:
            data["dhcp_on"] = module.params["dhcp_on"]
    if module.params["space"]:
        if vlan.space != module.params["space"]:
            data["space"] = module.params["space"]
    return data


def update_vlan(module, client: Client, vlan):
    data = data_for_update_vlan(module, vlan)
    if data:
        updated_vlan_maas_dict = vlan.update(client, data)
        vlan_after = Vlan.from_maas(updated_vlan_maas_dict)
        return (
            True,
            vlan_after.to_ansible(),
            dict(before=vlan.to_ansible(), after=vlan_after.to_ansible()),
        )
    return (
        False,
        vlan.to_ansible(),
        dict(before=vlan.to_ansible(), after=vlan.to_ansible()),
    )


def delete_vlan(module, client: Client, fabric_id):
    vlan = Vlan.get_by_name(module, client, fabric_id, must_exist=False)
    if vlan:
        vlan.delete(client)
        return True, dict(), dict(before=vlan.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    fabric = Fabric.get_by_name(
        module, client, must_exist=True, name_field_ansible="fabric_name"
    )
    if module.params["state"] == "present":
        if not module.params["vid"]:
            vlan = Vlan.get_by_name(module, client, fabric.id, must_exist=True)
            return update_vlan(module, client, vlan)
        else:
            vlan = Vlan.get_by_vid(module, client, fabric.id)
            if vlan:
                return update_vlan(module, client, vlan)
            return create_vlan(module, client)
    if module.params["state"] == "absent":
        return delete_vlan(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(type="str", choices=["present", "absent"], required=True),
            fabric_name=dict(type="str", required=True),
            vid=dict(type="str"),
            vlan_name=dict(type="str"),
            new_vlan_name=dict(type="str"),
            description=dict(type="str"),
            mtu=dict(type="str"),
            dhcp_on=dict(type="str"),
            space=dict(type="str"),
        ),
        # required_one_of=
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
