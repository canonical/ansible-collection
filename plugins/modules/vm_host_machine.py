#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vm_host_machine

author:
  - Domen Dobnikar (@domen_dobnikar)
short_description: Return info about vm hosts
description:
  - Plugin return information about all or specific vm hosts.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.instance
seealso: []
options:
"""

EXAMPLES = r"""
"""

RETURN = r"""
machines:
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.state import HostState
from ..module_utils.client import Client
from ..module_utils.vmhost import VMHost
from ..module_utils.machine import Machine
from ..module_utils.utils import is_changed

def ensure_ready(module, client, vm_host_obj):
    before = []
    after = []
    machine_obj = Machine.from_ansible(module.params)
    payload = machine_obj.payload_for_compose(module)
    task = vm_host_obj.send_compose_request(module, client, payload)
    after.append((Machine.get_by_id(task["system_id"], client, must_exist=True)).to_ansible())
    return is_changed(before, after), after, dict(before=before, after= after)

def run(module, client):
    vm_host_obj = VMHost.get_by_name(module, client, must_exist=True, name_field_ansible="vm_host")
    if module.params["state"] == HostState.ready:
        changed, records, diff = ensure_ready(module, client, vm_host_obj)
    return changed, records, diff


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("instance"),
            state=dict(
                type="str",
                required=True,
                choices=["ready"] # Maybe add "deployed", "absent" in the future if needed.
            ),
            vm_host=dict(
                type="str",
                required=True,
            ),
            cores=dict(
                type="int",
            ),
            memory=dict(
                type="int",
            ),
            network_interfaces=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    name=dict(
                        type="str",
                        required=True,
                    ),
                    subnet_cidr=dict(
                        type="str",
                    ),
                ),
            ),
            storage_disks=dict(
                type="list",
                elements="dict",
                default=[],
                options=dict(
                    size_gigabytes=dict(
                        type="int",
                        required=True,
                    ),
                ),
            ),
        ),
    )

    try:
        host = module.params["instance"]["host"]
        client_key = module.params["instance"]["client_key"]
        token_key = module.params["instance"]["token_key"]
        token_secret = module.params["instance"]["token_secret"]

        client = Client(host, token_key, token_secret, client_key)
        changed, records, diff = run(module, client)
        module.exit_json(changed=changed, records=records, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
