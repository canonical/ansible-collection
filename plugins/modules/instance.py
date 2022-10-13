#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: instance

author:
  - Polona Mihalič (@PolonaM)
short_description: Deploy, release or delete machines.
description:
  - If I(state) value is C(deployed) the selected machine will be deployed.
    If I(hostname) is not provided, a random machine with I(allocate_params),
    I(deploy_params) and I(network_interface) parameters will be allocated and deployed.
    If I(hostname) is not provided and no parameters are given, a random machine will be allocated and deployed using the defaults.
  - If I(state) value is C(ready) the selected machine will be released.
  - If I(state) value is C(absent) the selected machine will be deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  hostname:
    description:
      - Name of the machine to be deleted, deployed or released.
      - Serves as unique identifier of the machine.
      - If machine is not found the task will FAIL.
    type: str
  state:
    description:
      - Desired state of the machine.
    choices: [ ready, deployed, absent ]
    type: str
    required: True
  allocate_params:
    description:
      - Constraints parameters that can be used to allocate a machine with certain characteristics.
      - All of the constraints are optional and when multiple constraints are provided, they are combined using 'AND' semantics.
      - If no parameters are given, a random machine will be allocated using the defaults.
      - Relevant only if I(state) value is C(deployed) and I(hostname) is not provided.
    type: dict
    suboptions:
      cores:
        description:
          - The minimum number of CPUs a returned machine must have.
          - A machine with additional CPUs may be allocated if there is no exact match, or if the I(memory) constraint is not also specified.
        type: int
      memory:
        description:
          - The minimum amount of memory (expressed in MB) the returned machine must have.
          - A machine with additional memory may be allocated if there is no exact match, or the I(cores) constraint is not also specified.
        type: int
      zone:
        description: The zone name of the MAAS machine to be allocated.
        type: str
      pool:
        description: The pool name of the MAAS machine to be allocated.
        type: str
      tags:
        description: A set of tag names that must be assigned on the MAAS machine to be allocated.
        type: list
        elements: str
  deploy_params:
    description:
      - Constraints parameters that can be used to deploy a machine.
      - All of the constraints are optional and when multiple constraints are provided, they are combined using 'AND' semantics.
      - If no parameters are given, machine previously allocated will be deployed using the defaults.
      - Relevant only if I(state) value is C(deployed) and I(hostname) is not provided.
      - If machine is already in deployed state, I(deploy_params) will be ignored. Machine needs to be released first for I(deploy_params) to apply
    type: dict
    suboptions:
      osystem:
        description: The OS the machine will use.
        type: str
      distro_series:
        description: The OS release the machine will use.
        type: str
      timeout:
        description: Time in seconds to wait for server response when deploying.
        type: int
      hwe_kernel:
        description:
          - Specifies the kernel to be used on the machine.
          - Only used when deploying Ubuntu.
        type: str
      user_data:
        description: Blob of base64-encoded user-data to be made available to the machines through the metadata service.
        type: str
  network_interfaces:
    description:
      - Network interface.
    type: dict
    suboptions:
      name:
        description:
          - The name of the network interface to be configured on the allocated machine.
          - If both subnet_cidr and ip_address are not defined, the interface will not be configured on the allocated machine.
        type: str
      subnet_cidr:
        type: str
        description:
          - An existing subnet CIDR used to configure the network interface.
          - Unless ip_address is defined, a free IP address is allocated from the subnet.
      ip_address:
        type: str
        description:
          - Static IP address to be configured on the network interface.
          - If this is set, the subnet_cidr is required.
"""

EXAMPLES = r"""
- name: Remove/delete machine
  canonical.maas.instance:
    hostname: my_instance
    state: absent

- name: Release machine
  canonical.maas.instance:
    hostname: my_instance
    state: ready

- name: Deploy already commissioned machine
  canonical.maas.instance:
    hostname: my_instance
    state: deployed

- name: Deploy already commissioned machine with custom settings
  canonical.maas.instance:
    hostname: my_instance
    state: deployed
    deploy_params:
      osystem: ubuntu
      distro_series: focal
      hwe_kernel: my_kernel
      user_data: my_user_data

- name: Deploy random/new machine with default constraints
  canonical.maas.instance:
    state: deployed

- name: Deploy random/new machine with custom settings and constraints
  canonical.maas.instance:
    state: deployed
    allocate_params:
      cores: 2
      memory: 2000
      zone: my_zone
      pool: my_pool
      tags: my_tag
    network_interfaces:
      name: my_network
      subnet_cidr: 10.10.10.0/24
      ip_address: 10.10.10.190
    deploy_params:
      osystem: ubuntu
      distro_series: jammy
      hwe_kernel: my_kernel
      user_data: my_user_data
"""

RETURN = r"""
record:
  description:
    - The deployed/released machine instance.
  returned: success
  type: dict
  sample:
    id: machine-id
    hostname: this-machine
    zone: default
    pool: default
    tags: pod-console-logging
    status: Ready
    memory: 2048
    cores: 2
    network_interfaces:
      - name: this-interface
        subnet_cidr: 10.0.0.0/24
    storage_disks:
      - size_gigabytes: 5
      - size_gigabytes: 10
    osystem: ubuntu
    distro_series: jammy
    hwe_kernel: ga-22.04
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine


def allocate(module, client: Client):
    data = {}
    if module.params["allocate_params"]:
        if module.params["allocate_params"]["cores"]:
            data["cpu_count"] = module.params["allocate_params"]["cores"]
        if module.params["allocate_params"]["memory"]:
            data["mem"] = module.params["allocate_params"]["memory"]
        if module.params["allocate_params"]["zone"]:
            data["zone"] = module.params["allocate_params"]["zone"]
        if module.params["allocate_params"]["pool"]:
            data["pool"] = module.params["allocate_params"]["pool"]
    # A function can be written for this in network interface class and also maybe used in Machine.payload_for_compose
    if module.params["network_interfaces"]:
        if (
            module.params["network_interfaces"]["name"]
            and module.params["network_interfaces"]["subnet_cidr"]
        ):
            name = module.params["network_interfaces"]["name"]
            subnet_cidr = module.params["network_interfaces"]["subnet_cidr"]
            if module.params["network_interfaces"]["ip_address"]:
                ip_address = module.params["network_interfaces"]["ip_address"]
                network_interface = f"{name}:subnet_cidr={subnet_cidr},ip={ip_address}"
            else:
                network_interface = f"{name}:subnet_cidr={subnet_cidr}"
            data["interfaces"] = network_interface
    # here an error can occur: 409 No machine matching the given constraints could be found.
    # instance can't be allocated if commissioning, the only action allowed is abort
    maas_dict = client.post(
        "/api/2.0/machines/", query={"op": "allocate"}, data=data
    ).json
    # From MAAS documentation: If multiple tag names are specified, the machine must be tagged with all of them.
    # To request multiple tags, this parameter must be repeated in the request with each value.
    if module.params["allocate_params"]:
        if module.params["allocate_params"]["tags"]:
            for tag in module.params["allocate_params"]["tags"]:
                maas_dict = client.post(
                    "/api/2.0/machines/",
                    query={"op": "allocate"},
                    data={"tag_names": tag},
                ).json
    return Machine.from_maas(maas_dict)


def delete(module, client: Client):
    machine = Machine.get_by_name(module, client, must_exist=False)
    if machine:
        machine.delete(client)
        return True, dict(), dict(before=machine.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def release(module, client: Client):
    machine = Machine.get_by_name(module, client, must_exist=True)
    if machine.status == "Ready":
        return (
            False,
            machine.to_ansible(),
            dict(before=machine.to_ansible(), after=machine.to_ansible()),
        )
    if machine.status == "Commissioning":
        # commissioning will bring machine to the ready state
        # if state == commissioning: "Unexpected response - 409 b\"Machine cannot be released in its current state ('Commissioning').\""
        updated_machine = Machine.wait_for_state(machine.id, client, False, "Ready")
        return (
            False,  # No change because we actually don't do anything, just wait for Ready
            updated_machine.to_ansible(),
            dict(
                before=updated_machine.to_ansible(), after=updated_machine.to_ansible()
            ),
        )
    if machine.status == "New" or machine.status == "Failed":
        # commissioning will bring machine to the ready state
        machine.commission(client)
        updated_machine = Machine.wait_for_state(machine.id, client, False, "Ready")
        return (
            True,
            updated_machine.to_ansible(),
            dict(before=machine.to_ansible(), after=updated_machine.to_ansible()),
        )
    machine.release(client)
    try:  # this is a problem for ephemeral machines
        updated_machine = Machine.wait_for_state(machine.id, client, False, "Ready")
    except errors.MachineNotFound:  # we get this for ephemeral machine
        updated_machine = machine
        pass
    return (
        True,
        updated_machine.to_ansible(),
        dict(before=machine.to_ansible(), after=updated_machine.to_ansible()),
    )


def deploy(module, client: Client):
    if module.params["hostname"]:
        machine = Machine.get_by_name(module, client, must_exist=True)
    else:
        # allocate random machine
        # If there is no machine to allocate, new is created and can be deployed. If we release it, it is automatically deleted (ephemeral)
        machine = allocate(module, client)
        Machine.wait_for_state(machine.id, client, False, "Allocated")
    if machine.status == "Deployed":
        return (
            False,
            machine.to_ansible(),
            dict(before=machine.to_ansible(), after=machine.to_ansible()),
        )
    if machine.status == "New" or machine.status == "Failed":
        machine.commission(client)
        Machine.wait_for_state(machine.id, client, False, "Ready")
    if machine.status == "Commissioning":
        # commissioning will bring machine to the ready state
        Machine.wait_for_state(machine.id, client, False, "Ready")
    data = {}
    timeout = 20  # seconds
    if module.params["deploy_params"]:
        if module.params["deploy_params"]["osystem"]:
            data["osystem"] = module.params["deploy_params"]["osystem"]
        if module.params["deploy_params"]["distro_series"]:
            data["distro_series"] = module.params["deploy_params"]["distro_series"]
        if module.params["deploy_params"]["timeout"]:
            timeout = module.params["deploy_params"]["timeout"]
        if module.params["deploy_params"]["hwe_kernel"]:
            data["hwe_kernel"] = module.params["deploy_params"]["hwe_kernel"]
        if module.params["deploy_params"]["user_data"]:
            data["user_data"] = module.params["deploy_params"]["user_data"]
    machine.deploy(client, data, timeout)  # here we can get TimeoutError: timed out
    updated_machine = Machine.wait_for_state(machine.id, client, False, "Deployed")
    return (
        True,
        updated_machine.to_ansible(),
        dict(before=machine.to_ansible(), after=updated_machine.to_ansible()),
    )


def run(module, client: Client):
    if module.params["state"] == "deployed":
        return deploy(module, client)
    if module.params["state"] == "ready":
        return release(module, client)
    if module.params["state"] == "absent":
        return delete(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            hostname=dict(type="str"),
            state=dict(
                type="str", required=True, choices=["ready", "deployed", "absent"]
            ),
            deploy_params=dict(
                type="dict",
                options=dict(
                    osystem=dict(type="str"),
                    distro_series=dict(type="str"),
                    timeout=dict(type="int"),
                    hwe_kernel=dict(type="str"),
                    user_data=dict(type="str"),
                ),
            ),
            allocate_params=dict(
                type="dict",
                options=dict(
                    cores=dict(type="int"),
                    memory=dict(type="int"),
                    zone=dict(type="str"),
                    pool=dict(type="str"),
                    tags=dict(type="list", elements="str"),
                ),
            ),
            network_interfaces=dict(
                type="dict",
                options=dict(
                    name=dict(type="str"),
                    subnet_cidr=dict(type="str"),
                    ip_address=dict(type="str"),
                ),
            ),
        ),
        required_if=[
            ("state", "absent", ("hostname",), False),
            ("state", "ready", ("hostname",), False),
        ],
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
