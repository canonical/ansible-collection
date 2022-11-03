#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
module: tag

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Manages network interfaces on a specific machine.
description: Connects, updates or disconnects an existing network interface on a specified machine.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  name:
    description: 
      - The new tag name.
      - Because the name will be used in urls, it should be short.
    type: str
    required: True
  machines:
    description: 
      - List of MAAS machines.
      - Use FQDN.
    type: list
    elements: str
    required: True
  state:
    description: Prefered tag state.
    choices: [ present, absent, set ]
    type: str
    required: True
"""

EXAMPLES = r"""
"""

RETURN = r"""
record:
  description:
    - Created or deleted subnet link.
  returned: success
  type: dict
  sample:
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.utils import is_changed
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.state import TagState


def ensure_present(module, client, machine_obj):
    return is_changed(before, after), after, dict(before=before, after=after)


def ensure_absent(module, client, machine_obj):
    return is_changed(before, after), after, dict(before=before, after=after)


def run(module, client):
    if module.params["state"] == TagState.present:
        changed, record, diff = ensure_present(module, client, machine_obj)
    else:
        changed, record, diff = ensure_absent(module, client, machine_obj)
    return changed, record, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(
                type="str",
                required=True,
            ),
            machines=dict(
                type="list",
                required=True,
                elements="str",
            ),
            state=dict(
                type="str",
                choices=["present", "absent", "set"],
                required=True,
            ),
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
