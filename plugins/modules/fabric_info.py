#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: fabric_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns info about network fabrics.
description:
  - Plugin returns information about all network fabrics or specific network fabric if I(name) is provided.
version_added: 1.0.0
extends_documentation_fragment:
  - maas.maas.cluster_instance
seealso: []
options:
  name:
    description:
      - Name of the network fabric to be listed.
      - Serves as unique identifier of the network fabric.
    type: str
"""

EXAMPLES = r"""
- name: Get list of all network fabrics
  maas.maas.fabric_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key

- name: Get info about a specific network fabric
  maas.maas.fabric_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    name: my-network-fabric
"""

RETURN = r"""
records:
  description:
    - Network fabric info list.
  returned: success
  type: list
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
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.fabric import Fabric


def run(module, client: Client):
    if module.params["name"]:
        fabric = Fabric.get_by_name(module, client, must_exist=True)
        response = [fabric.to_ansible()]
    else:
        response = client.get("/api/2.0/fabrics/").json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            name=dict(type="str"),
        ),
    )

    try:
        client = get_oauth1_client(module.params)
        records = run(module, client)
        module.exit_json(changed=False, records=records)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
