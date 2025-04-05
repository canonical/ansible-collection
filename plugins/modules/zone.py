#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: zone

author:
  - İzzettin Erdem (@rootz1one)
short_description: Creates, updates or deletes MAAS zone.
description:
  - If I(state) is C(present) and I(name) is not present or not found, creates new zone.
  - If I(state) is C(present) and I(name) is found, updates an existing zone.
  - If I(state) is C(absent) selected zone is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the zone.
    choices: [ present, absent ]
    type: str
    required: True
  name:
    description:
      - Name of the zone to be created, updated or deleted.
      - Serves as unique identifier of the zone to be updated.
    type: str
    required: True
  new_name:
    description:
      - New name of the existing zone to be updated.
    type: str
  description:
    description:
      - Description of the new zone.
    type: str
"""

EXAMPLES = r"""
- name: Create new zone
  canonical.maas.zone:
    state: present
    name: my-zone
    description: My zone

- name: Update zone
  canonical.maas.zone:
    state: present
    name: my-zone
    new_name: updated-zone
    description: My zone updated

- name: Remove zone
  canonical.maas.zone:
    state: absent
    name: updated-zone
"""

RETURN = r"""
record:
  description:
    - Created or updated zone.
  returned: success
  type: dict
  sample:
    description: test
    id: -1
    name: undefined
    resource_uri: /MAAS/api/2.0/zones/undefined/
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.zone import Zone
from ..module_utils.cluster_instance import get_oauth1_client


def data_for_create_zone(module):
    data = {}

    data["name"] = module.params["name"]
    if module.params["description"]:
        data["description"] = module.params["description"]
    return data


def create_zone(module, client: Client):
    data = data_for_create_zone(module)
    zone = Zone.create(client, data)
    return (
        True,
        zone.to_ansible(),
        dict(before={}, after=zone.to_ansible()),
    )


def data_for_update_zone(module, zone):
    data = {}
    if module.params["new_name"]:
        if zone.name != module.params["new_name"]:
            data["name"] = module.params["new_name"]
    if module.params["description"]:
        data["description"] = module.params["description"]
    return data


def update_zone(module, client: Client, zone):
    changed = False
    zone_before = zone
    data = data_for_update_zone(module, zone)
    if data:
        updated_zone_maas_dict = zone.update(client, data)
        zone_after = Zone.from_maas(updated_zone_maas_dict)

        if zone != zone_after:
            changed = True
            zone = zone_after

    return (
        changed,
        zone.to_ansible(),
        dict(before=zone_before.to_ansible(), after=zone.to_ansible()),
    )


def delete_zone(module, client: Client):
    zone = Zone.get_by_name(module, client, must_exist=False)
    if zone:
        zone.delete(client)
        return True, dict(), dict(before=zone.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        if not module.params["name"]:
            return create_zone(module, client)
        else:
            zone = Zone.get_by_name(module, client)
            if zone:
                return update_zone(module, client, zone)
            return create_zone(module, client)
    if module.params["state"] == "absent":
        return delete_zone(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True
            ),
            name=dict(
                type="str",
                required=True,
            ),
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

