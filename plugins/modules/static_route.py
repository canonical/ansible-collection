#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: static_route

author:
  - Arkadiy Shinkarev (@k3nny0ne)
short_description: Creates, updates or deletes Static Routes.
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
  state:
    description:
      - Desired state of the Static Route.
    choices: [ present, absent ]
    type: str
    required: True
  source:
    description:
      - Source subnet name for the route.
    type: str
    required: True
  destination:
    description:
      - Destination subnet name for the route.
    type: str
    required: True
  gateway_ip:
    description:
      - IP address of the gateway on the source subnet.
    type: str
    required: True
  metric:
    description:
      - Weight of the route on a deployed machine.
    type: int
    required: False
"""

EXAMPLES = r"""
- name: Create Static Route
  canonical.maas.static_route:
    state: present
    source: "subnet-1"
    destination: "subnet-2"
    gateway_ip: "192.168.1.1"
    metric: 100

- name: Update Static Route
  canonical.maas.static_route:
    state: present
    source: "subnet-1"
    destination: "subnet-2"
    gateway_ip: "192.168.1.1"
    metric: 0

- name: Remove Static Route using specification
  canonical.maas.static_route:
    state: absent
    source: "subnet-1"
    destination: "subnet-2"
    gateway_ip: "192.168.1.1"
    metric: 0
"""

RETURN = r"""
record:
  description:
    - Created or updated Static Route.
  returned: success
  type: dict
  sample:
    source: "subnet-1"
    destination: "subnet-2"
    gateway_ip: "192.168.1.1"
    metric: 0
    id: 4
    resource_uri: /MAAS/api/2.0/static-routes/4/
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.static_route import StaticRoute
from ..module_utils.cluster_instance import get_oauth1_client


def data_for_create_static_route(module):
    data = {}
    data["source"] = module.params["source"]  # required
    data["destination"] = module.params["destination"]  # required
    data["gateway_ip"] = module.params["gateway_ip"]  # required

    if "metric" in module.params and module.params["metric"]:
        data["metric"] = module.params["metric"]
    return data


def create_static_route(module, client: Client):
    data = data_for_create_static_route(module)
    static_route = StaticRoute.create(client, data)
    return (
        True,
        static_route.to_ansible(),
        dict(before={}, after=static_route.to_ansible()),
    )


def data_for_update_static_route(module, static_route):
    data = {}

    if module.params["metric"]:
        if static_route.metric != module.params["metric"]:
            data["metric"] = module.params["metric"]
    if module.params["gateway_ip"]:
        if static_route.gateway_ip != module.params["gateway_ip"]:
            data["gateway_ip"] = module.params["gateway_ip"]

    if (
        static_route.source
        and isinstance(static_route.source, dict)
        and static_route.source["name"] != module.params["source"]
    ):
        data["source"] = module.params["source"]

    if (
        static_route.destination
        and isinstance(static_route.destination, dict)
        and static_route.destination["name"] != module.params["destination"]
    ):
        data["destination"] = module.params["destination"]

    return data


def update_static_route(module, client: Client, static_route: StaticRoute):
    data = data_for_update_static_route(module, static_route)
    if data:
        updated = static_route.update(module, client, data)
        after = StaticRoute.from_maas(updated)
        return (
            True,
            after.to_ansible(),
            dict(before=static_route.to_ansible(), after=after.to_ansible()),
        )
    return (
        False,
        static_route.to_ansible(),
        dict(before=static_route.to_ansible(), after=static_route.to_ansible()),
    )


def delete_static_route(module, client: Client):
    static_route = StaticRoute.get_by_spec(module, client, must_exist=False)
    if static_route:
        static_route.delete(module, client)
        return True, dict(), dict(before=static_route.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        static_route = StaticRoute.get_by_spec(module, client, must_exist=False)
        if static_route:
            return update_static_route(module, client, static_route)
        return create_static_route(module, client)
    if module.params["state"] == "absent":
        return delete_static_route(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(type="str", choices=["present", "absent"], required=True),
            source=dict(type="str", required=True),
            destination=dict(type="str", required=True),
            gateway_ip=dict(type="str", required=True),
            metric=dict(type="int"),
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
