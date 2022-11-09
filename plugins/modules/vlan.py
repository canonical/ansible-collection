#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vlan

author:
  - Polona Mihalič (@PolonaM)
short_description: Creates, updates or deletes MAAS VLANs.
description:
  - If I(state) is C(present) and I(vid) is provided but not found, new VLAN with specified traffic segregation ID - I(vid)
    is created on a specified fabric - I(fabric_name).
  - If I(state) is C(present) and I(vid) or I(vlan_name) is found, updates an existing VLAN.
  - If I(state) is C(absent) VLAN selected either by I(vid) or I(vlan_name) is deleted.
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
      - Required when creating new VLAN.
      - Serves as unique identifier of VLAN to be updated.
    type: int
  vlan_name:
    description:
      - The name of the new VLAN to be created. This is computed if it's not set.
      - Serves also as unique identifier of VLAN to be updated if I(vid) is not provided.
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
      - Passing in an empty string will cause the VLAN to be placed in the undefined space.
    type: str
"""

EXAMPLES = r"""
- name: Create VLAN
  canonical.maas.vlan:
    state: present
    fabric_name: fabric-10
    vid: 5
    vlan_name: vlan-10
    description: VLAN on fabric-10
    mtu: 1500
    dhcp_on: false
    space: network-space-10

- name: Update VLAN - using vid as identifier
  canonical.maas.vlan:
    state: present
    fabric_name: fabric-10
    vid: 5
    new_vlan_name: vlan-10-updated
    description: VLAN on fabric-10 updated
    mtu: 2000
    dhcp_on: true
    space: new-network-space

- name: Update VLAN - using name as identifier
  canonical.maas.vlan:
    state: present
    fabric_name: fabric-10
    vlan_name: vlan-10
    new_vlan_name: vlan-10-updated
    description: VLAN on fabric-10 updated
    mtu: 2000
    dhcp_on: true
    space: new-network-space

- name: Remove VLAN - using vid as identifier
  canonical.maas.vlan:
    state: absent
    fabric_name: fabric-10
    vid: 5

- name: Remove VLAN - using name as identifier
  canonical.maas.vlan:
    state: absent
    fabric_name: fabric-10
    vlan_name: vlan-10
"""

RETURN = r"""
record:
  description:
    - Created or updated VLAN.
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
from ..module_utils.fabric import Fabric
from ..module_utils.cluster_instance import get_oauth1_client


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
        data = data_for_update_vlan(module, vlan)
        vlan.update(client, data)
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
    if (
        module.params["space"] is not None
    ):  # we want a possibility to write empty string to get "undefined" space
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
    if module.params["vid"]:
        vlan = Vlan.get_by_vid(
            module.params["vid"], client, fabric_id, must_exist=False
        )
    else:
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
            vlan = Vlan.get_by_vid(
                module.params["vid"], client, fabric.id, must_exist=False
            )
            if vlan:
                return update_vlan(module, client, vlan)
            return create_vlan(module, client, fabric.id)
    if module.params["state"] == "absent":
        return delete_vlan(module, client, fabric.id)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(type="str", choices=["present", "absent"], required=True),
            fabric_name=dict(type="str", required=True),
            vid=dict(type="int"),
            vlan_name=dict(type="str"),
            new_vlan_name=dict(type="str"),
            description=dict(type="str"),
            mtu=dict(type="int"),
            dhcp_on=dict(type="bool"),
            space=dict(type="str"),
        ),
        required_one_of=[
            ("vid", "vlan_name"),
        ],
    )

    try:
        client = get_oauth1_client(module.params)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
