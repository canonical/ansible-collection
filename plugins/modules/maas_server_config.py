#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: maas_server_config
author:
  - Arkadiy Shinkarev (@k3nny0ne)
short_description: Manage the MAAS server configuration.
description:
  - If I(state) is C(present) and all required options is provided but not found,
    new Static Route with specified configuration is created.
  - If I(state) is C(present) and static route is found based on specified options, updates an existing Static Route.
  - If I(state) is C(absent) Static Route selected by I(name) is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  name:
    description:
      - The name of the configuration item to be set.
      - See L(MAAS API Reference,https://maas.io/docs/api#maas-server)
        for available configuration items.
    type: str
    required: True
  value:
    description:
      - The value of the configuration item to be set.
    type: str
    required: False
"""

EXAMPLES = r"""
- name: Complete intro
  canonical.maas.maas_server_config:
    name: completed_intro
    value: true
- name: Cleanup boot parameters
  canonical.maas.maas_server_config:
    name: kernel_opts
    value: ""
"""

RETURN = r"""
record:
  description:
    - Updated configuration option.
  returned: success
  type: dict
  sample:
    name: completed_intro
    value: true
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.maas_server_config import MaasServerConfig
from ..module_utils.cluster_instance import get_oauth1_client


def data_for_update_config(module, maas_server_config):
    data = {}
    # raise Exception(str(module.params["value"]))
    if module.params["value"]:
        if maas_server_config.value != module.params["value"]:
            data["name"] = module.params["name"]
            data["value"] = module.params["value"]

    return data


def update_config(module, client: Client, config: MaasServerConfig):
    data = data_for_update_config(module, config)
    if data:
        updated = config.update(module, client, data)
        return (
            True,
            updated.to_ansible(),
            dict(before=config.to_ansible(), after=updated.to_ansible()),
        )
    return (
        False,
        config.to_ansible(),
        dict(before=config.to_ansible(), after=config.to_ansible()),
    )


def run(module, client: Client):
    config = MaasServerConfig.get_by_name(module, client)
    if config:
        return update_config(module, client, config)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(type="str", required=True),
            value=dict(type="str"),
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
