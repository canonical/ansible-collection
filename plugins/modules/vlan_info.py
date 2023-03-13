#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: vlan_info

author:
  - Polona Mihalič (@PolonaM)
short_description: Returns info about VLANs.
description:
  - Plugin returns information about all VLANs on a specfic fabric or specific VLAN on a specfic fabric.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  fabric_name:
    description:
      - Name of the fabric whose VLANs will be listed.
      - Serves as unique identifier of the fabric.
      - If fabric is not found, the task will FAIL.
    type: str
    required: true
  vid:
    description:
      - Traffic segregation ID of the VLAN to be listed.
      - Serves as unique identifier of the VLAN.
      - If VLAN is not found, the task will FAIL.
    type: str
  vlan_name:
    description:
      - Name of the VLAN to be listed.
      - Serves as unique identifier of the VLAN if I(vid) is not provided.
      - If VLAN is not found, the task will FAIL.
    type: str
"""

EXAMPLES = r"""
- name: Get list of all VLANs on a specific fabric
  canonical.maas.vlan_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    fabric_name: fabric-7

- name: Get info about a specific VLAN on a specific fabric - by vlan name
  canonical.maas.vlan_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    fabric_name: fabric-7
    vlan_name: vlan-5

- name: Get info about a specific VLAN on a specific fabric - by vid
  canonical.maas.vlan_info:
    cluster_instance:
      host: host-ip
      token_key: token-key
      token_secret: token-secret
      customer_key: customer-key
    fabric_name: fabric-7
    vid: 5
"""

RETURN = r"""
records:
  description:
    - VLANs on a specific fabric info list.
  returned: success
  type: list
  sample:
  - dhcp_on: false
    external_dhcp: null
    fabric: fabric-7
    fabric_id: 7
    id: 5014
    mtu: 1500
    name: vlan-5
    primary_rack: null
    relay_vlan: null
    resource_uri: /MAAS/api/2.0/vlans/5014/
    secondary_rack: null
    space: undefined
    vid: 5
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.cluster_instance import get_oauth1_client
from ..module_utils.fabric import Fabric
from ..module_utils.vlan import Vlan


def run(module, client: Client):
    fabric = Fabric.get_by_name(
        module, client, must_exist=True, name_field_ansible="fabric_name"
    )
    if module.params["vid"]:
        vlan = Vlan.get_by_vid(module, client, fabric.id, must_exist=True)
        response = [vlan.to_ansible()]
    elif module.params["vlan_name"]:
        vlan = Vlan.get_by_name(module, client, fabric.id, must_exist=True)
        response = [vlan.to_ansible()]
    else:
        response = client.get(f"/api/2.0/fabrics/{fabric.id}/vlans/").json
    return response


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            fabric_name=dict(type="str", required=True),
            vlan_name=dict(type="str"),
            vid=dict(type="str"),
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
