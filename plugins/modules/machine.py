#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: machine

author:
  - Polona Mihalič (@PolonaM)
short_description: Provides a resource to manage MAAS machines.
description:
  - Adds existing machine to the system.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  power_type
    description:
      - A power management type (e.g. ipmi).
    type: str
    required: true
    choices: [ "amt", "apc", "dli", "eaton", "hmc", "ipmi", "manual", "moonshot", "mscm", "msftocs", "nova",
              "openbmc", "proxmox", "recs_box", "redfish", "sm15k", "ucsm", "vmware", "webhook", "wedge", "lxd", "virsh" ]
  power_parameters:
    description:
      - A dictionary with the parameters specific to the power_type.
      - See U(https://maas.io/docs/api#power-types) section for a list of available power parameters for each power type.
    type: dict
    required: true
  pxe_mac_address:
    description:
      - The MAC address of the machine's PXE boot NIC.
    type: str
    required: true
  arhitecture:
    description:
      - The architecture type of the machine (for example, "i386/generic" or "amd64/generic").
      - Defaults to amd64/generic.
    type: str
  hostname:
    description:
      - Name of the machine to be added # also updated??.
      - This is computed if it's not set.
    type: str
  domain:
    description:
      - The domain of the machine.
      - This is computed if it's not set.
    type: str
  zone:
    description:
      - The zone of the machine.
      - This is computed if it's not set.
    type: str
  pool:
    description:
      - The resource pool of the machine.
      - This is computed if it's not set.
    type: str
  min_hwe_kernel:
    description:
      - The minimum kernel version allowed to run on this machine.
      - Only used when deploying Ubuntu.
      - This is computed if it's not set.
    type: str


  # state:
  #   description:
  #     - Desired state of the machine.
  #   choices: [ ready, deployed, absent ]
  #   type: str
  #   required: True
"""

EXAMPLES = r"""
- name: Add machine to system
  canonical.maas.machine:
    state: present
    power_type: lxd
    power_parameters:
      power_address: ...
      power_id: ...
    pxe_mac_address: ...
"""

RETURN = r"""
record:
  description:
    - Added machine.
  returned: success
  type: dict
  sample:
    cores: 2
    distro_series: focal
    fqdn: new-machine.maas
    hostname: new-machine
    hwe_kernel: ga-22.04
    id: 6h4fn6
    memory: 2048
    network_interfaces:
    - fabric: fabric-1
      id: 277
      ip_address: 10.10.10.190
      name: my-net
      subnet_cidr: 10.10.10.0/24
      vlan: untagged
    osystem: ubuntu
    pool: default
    power_type: lxd
    status: Commissioning
    storage_disks:
    - id: 288
      name: sda
      size_gigabytes: 3
    - id: 289
      name: sdb
      size_gigabytes: 5
    tags:
      - pod-console-logging
      - my-tag
    zone: default
"""


import json
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine


def create_machine(module, client: Client):
    data = {}
    data["power_type"] = module.params["power_type"]
    data["power_parameters"] = json.dumps(module.params["power_parameters"])
    data["mac_addresses "] = module.params["pxe_mac_address"]
    data["arhitecture"] = "amd64/generic"  # Default
    if module.params["arhitecture"]:
        data["arhitecture"] = module.params["arhitecture"]
    if module.params["hostname"]:
        data["hostname"] = module.params["hostname"]
    if module.params["domain"]:
        data["domain"] = module.params["domain"]
    if module.params["zone"]:
        data["zone"] = module.params["zone"]
    if module.params["pool"]:
        data["pool"] = module.params["pool"]
    if module.params["min_hwe_kernel"]:
        data["min_hwe_kernel"] = module.params["min_hwe_kernel"]

    machine = Machine.create(client, data)
    # machine = Machine.wait_for_state(machine.id, client, False, "Ready")

    return (
        True,
        machine,
        dict(before={}, after=machine),
    )


def run(module, client: Client):
    return create_machine(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            power_type=dict(
                type="str",
                required=True,
                choices=[
                    "amt",
                    "apc",
                    "dli",
                    "eaton",
                    "hmc",
                    "ipmi",
                    "manual",
                    "moonshot",
                    "mscm",
                    "msftocs",
                    "nova",
                    "openbmc",
                    "proxmox",
                    "recs_box",
                    "redfish",
                    "sm15k",
                    "ucsm",
                    "vmware",
                    "webhook",
                    "wedge",
                    "lxd",
                    "virsh",
                ],
            ),
            power_parameters=dict(type="dict", required=True),
            pxe_mac_address=dict(type="str", required=True),
            hostname=dict(type="str"),
            domain=dict(type="str"),
            zone=dict(type="str"),
            pool=dict(type="str"),
            min_hwe_kernel=dict(type="str"),
            arhitecture=dict(type="str"),
        ),
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
