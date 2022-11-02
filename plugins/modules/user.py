#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
module: user

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: 
description: 
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  name:
    description:
      - The user name.
      - Identifier-style username for the user.
    type: str
    required: True
  password:
    description: The user password.
    type: str
    required: True
  email:
    description: The user e-mail address.
    type: str
    required: True
  is_admin:
    description: Indicating if the user is a MAAS administrator.
    type: bool
    Default: False
  state:
    description: Prefered state of the user.
    choices: [ present, absent ]
    type: str
    required: True
"""

EXAMPLES = r"""
"""

RETURN = r"""
record:
"""

from ansible.module_utils.basic import AnsibleModule


from ..module_utils import arguments, errors
from ..module_utils.utils import is_changed
from ..module_utils.state import UserState
from ..module_utils.user import User
from ..module_utils.cluster_instance import get_oauth1_client


def ensure_present(module, client):
    before = None
    after = None
    new_user = User.from_ansible(module.params)
    existing_user = User.get_by_name(module, client)
    if not existing_user: #Create user
      new_user.send_create_request(client, new_user.payload_for_create())
      after = User.get_by_name(module, client).to_ansible()
    elif existing_user and existing_user.needs_update(new_user):
      before = existing_user.to_ansible()
      new_user.send_create_request(client, new_user.payload_for_create())
      # TODO: update request
      raise errors.MaasError("Check here")
      after = User.get_by_name(module, client).to_ansible()
    return is_changed(before, after), after, dict(before=before, after=after)

def ensure_absent(module, client):
    before = None
    after = None
    existing_user = User.get_by_name(module, client)
    if existing_user:
      before = existing_user.to_ansible()
      existing_user.send_delete_request(client)
    return is_changed(before, after), after, dict(before=before, after=after)

def run(module, client):
    if module.params["state"] == UserState.present:
      changed, record, diff = ensure_present(module, client)
    else:
      changed, record, diff = ensure_absent(module, client)
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
            password=dict(
                type="str",
                required=True,
                no_log=True,
            ),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            email=dict(
                type="str",
                required=True,
            ),
            is_admin=dict(
                type="bool",
                default=False,
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
