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
  - If I(state) is C(present) and I(hostname) is not provided or not found, adds an existing machine to the system.
  - If I(state) is C(present) and I(hostname) is found, updates an existing machine in the system.
  - If I(state) is C(absent) selected machine is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the machine.
    choices: [ present, absent ]
    type: str
    required: True
  power_type
    description:
      - A power management type (e.g. ipmi).
      - In case of adding new machine to the system, this parameters is required.
    type: str
    choices: [ "amt", "apc", "dli", "eaton", "hmc", "ipmi", "manual", "moonshot", "mscm", "msftocs", "nova",
              "openbmc", "proxmox", "recs_box", "redfish", "sm15k", "ucsm", "vmware", "webhook", "wedge", "lxd", "virsh" ]
  power_parameters:
    description:
      - A dictionary with the parameters specific to the power_type.
      - See U(https://maas.io/docs/api#power-types) section for a list of available power parameters for each power type.
      - In case of adding new machine to the system, this parameters is required.
    type: dict
  pxe_mac_address:
    description:
      - The MAC address of the machine's PXE boot NIC.
      - In case of adding new machine to the system, this parameters is required.
    type: str
  architecture:
    description:
      - The architecture type of the machine (for example, "i386/generic" or "amd64/generic").
      - Defaults to amd64/generic.
    type: str
  fqdn:
    description:
      - Fully qualified domain name of the machine to be updated or deleted.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
  hostname:
    description:
      - Name of the machine to be added. In case of updating the machine, this parameter is used for updating the name if the machine.
      - In case if new machine is added, the name is computed if it's not set.
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



"""

EXAMPLES = r"""
- name: Add machine to the system
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
    architecture: amd64/generic
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
      mac_address: 00:00:00:00:00:01
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


def add_machine(module, client: Client):
    data = {}
    try:
        data["power_type"] = module.params["power_type"]  # required
        data["power_parameters"] = json.dumps(
            module.params["power_parameters"]
        )  # required
        data["mac_addresses "] = module.params["pxe_mac_address"]  # required
    except Exception as e:
        raise errors.MissingValueAnsible(e)
    data["architecture"] = "amd64/generic"  # default
    if module.params["architecture"]:
        data["architecture"] = module.params["architecture"]
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

    return (
        True,
        machine.to_ansible(),
        dict(before={}, after=machine.to_ansible()),
    )


def update_machine(module, client: Client):
    machine = Machine.get_by_fqdn(module, client, must_exist=True)
    data = {}
    if module.params["power_type"]:
        if machine.power_type != module.params["power_type"]:
            data["power_type"] = module.params["power_type"]
    if module.params["power_parameters"]:
        # Here we will not check for changes because some parameteres aren't returned
        data["power_parameters"] = json.dumps(module.params["power_parameters"])
    if module.params["pxe_mac_addresses"]:
        if machine.network_interfaces.mac_address != module.params["pxe_mac_address"]:
            data["mac_addresses "] = module.params["pxe_mac_address"]
    if module.params["architecture"]:
        if machine.architecture != module.params["architecture"]:
            data["architecture"] = module.params["architecture"]
    if module.params["hostname"]:
        if machine.hostname != module.params["hostname"]:
            data["hostname"] = module.params["hostname"]
    if module.params["domain"]:
        if machine.domain != module.params["domain"]:
            data["domain"] = module.params["domain"]
    if module.params["zone"]:
        if machine.zone != module.params["zone"]:
            data["zone"] = module.params["zone"]
    if module.params["pool"]:
        if machine.pool != module.params["pool"]:
            data["pool"] = module.params["pool"]
    if module.params["min_hwe_kernel"]:
        if machine.hwe_kernel != module.params["min_hwe_kernel"]:
            data["min_hwe_kernel"] = module.params["min_hwe_kernel"]

    if data:
        updated_machine_maas_dict = machine.update(client, data)
        machine_after = Machine.from_maas(updated_machine_maas_dict)
        return (
            True,
            machine_after.to_ansible(),
            dict(before=machine.to_ansible(), after=machine_after.to_ansible()),
        )
    return (
        False,
        machine.to_ansible(),
        dict(before=machine.to_ansible(), after=machine.to_ansible()),
    )


def delete_machine(module, client: Client):
    machine = Machine.get_by_fqdn(module, client, must_exist=False)
    if machine:
        machine.delete(client)
        return True, dict(), dict(before=machine.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        if module.params["fqdn"]:
            return update_machine(module, client)
        else:
            return add_machine(module, client)
    if module.params["state"] == "absent":
        return delete_machine(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(
                type="str",
                choices=["present", "absent"],
                required=True,
            ),
            power_type=dict(
                type="str",
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
            power_parameters=dict(type="dict"),
            pxe_mac_address=dict(type="str"),
            hostname=dict(type="str"),
            domain=dict(type="str"),
            zone=dict(type="str"),
            pool=dict(type="str"),
            min_hwe_kernel=dict(type="str"),
            architecture=dict(type="str"),
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
