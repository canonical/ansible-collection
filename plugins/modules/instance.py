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
    If I(hostname) is not provided, a random machine with I(allocate_params) and I(deploy_params) will be allocated and deployed.
    If no parameters are given, a random machine will be allocated and deployed using the defaults.
    In case if no machine matching the given constraints could be found, the task will FAIL.
  - If I(state) value is C(ready) the selected machine will be released.
  - If I(state) value is C(absent) the selected machine will be deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.instance
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
      - All the constraints are optional and when multiple constraints are provided, they are combined using 'AND' semantics.
      - If no parameters are given, a random machine will be allocated using the defaults.
      - Relevant only if I(state) value is C(deployed)
    type: dict
    options:
      cores:
        description:
          - If present, this parameter specifies the minimum number of CPUs a returned machine must have.
          - A machine with additional CPUs may be allocated if there is no exact match, or if the 'mem' constraint is not also specified.
        type: int
      memory:
        description:
          - If present, this parameter specifies the minimum amount of memory (expressed in MB) the returned machine must have.
          - A machine with additional memory may be allocated if there is no exact match, or the 'cpu' constraint is not also specified.
        type: int
  deploy_params:
    description:
      - Specify the OS and OS release the machine will use.
      - If no parameters are given, a random machine will be deployed using the defaults.
      - Relevant only if I(state) value is C(deployed)
      - If machine is already in deployed state, I(deploy_params) will be ignored. Machine needs to be released first for I(deploy_params) to apply
    type: dict
    options:
      osystem:
        description:
          - If present, this parameter specifies the OS the machine will use.
        type: str
      distro_series:
        description:
          - If present, this parameter specifies the OS release the machine will use.
        type: str
      timeout:
        description:
          - Time in seconds to wait for server response in case of deploying.
        type: int
"""

EXAMPLES = r"""
name: Remove/delete machine
canonical.maas.instance:
  hostname: my_instance
  state: absent

name: Release machine
canonical.maas.instance:
  hostname: my_instance
  state: ready

name: Deploy already commissioned machine
canonical.maas.instance:
  hostname: my_instance
  state: deployed

name: Deploy already commissioned machine with custom OS and OS series
canonical.maas.instance:
  hostname: my_instance
  state: deployed
  deploy_params:
    osystem: ubuntu
    distro_series: focal

name: Deploy random/new machine with default OS and allocation constraints
canonical.maas.instance:
  state: deployed

name: Deploy random/new machine with custom OS and allocation constraints
canonical.maas.instance:
  state: deployed
  allocate_params:
    cores: 1
    memory: 2
  deploy_params:
    osystem: ubuntu
    distro_series: focal
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
"""


from time import sleep
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.machine import Machine
from ..module_utils.task import Task
from ..module_utils.state import MachineTaskState


def allocate(module, client: Client):
    data = {}
    if module.params["allocate_params"]:
        if module.params["allocate_params"]["cores"]:
            data["cpu_count"] = module.params["allocate_params"]["cores"]
        if module.params["allocate_params"]["memory"]:
            data["mem"] = module.params["allocate_params"]["memory"]
        # here an error can occur:
        # HTTP Status Code : 409 No machine matching the given constraints could be found.
        # This happens only when all machines are allocated and we want to release random machine using allocate_params
    # instance can't be allocated if commissioning, the only action allowed is abort
    maas_dict = client.post(
        "/api/2.0/machines/", query={"op": "allocate"}, data=data
    ).json
    return Machine.from_maas(maas_dict)


def commission(system_id, client: Client):
    """
    From MAAS documentation:
    A machine in the 'ready', 'declared' or 'failed test' state may initiate a commissioning cycle
    where it is checked out and tested in preparation for transitioning to the 'ready' state.
    If it is already in the 'ready' state this is considered a re-commissioning process which is useful
    if commissioning tests were changed after it previously commissioned.

    Also it is possible to commission the machine when it is in 'new' state.
    We get state 'new' in case if we abort commissioning of the machine (which was before already in ready or allocated state)
    """
    maas_dict = client.post(
        f"/api/2.0/machines/{system_id}", query={"op": "commission"}
    ).json
    return Machine.from_maas(maas_dict)


def delete(module, client: Client):
    machine = Machine.get_by_name(module, client, must_exist=False)
    if machine:
        client.delete(f"/api/2.0/machines/{machine.id}/")
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
        updated_machine = Task.wait_for_state(machine.id, client, False, MachineTaskState.ready)
        return (
            False,  # No change because we actually don't do anything, just wait for Ready
            updated_machine.to_ansible(),
            dict(
                before=updated_machine.to_ansible(), after=updated_machine.to_ansible()
            ),
        )
    if machine.status == "New" or machine.status == "Failed":
        # commissioning will bring machine to the ready state
        commission(machine.id, client)
        updated_machine = Task.wait_for_state(machine.id, client, False, MachineTaskState.ready)
        return (
            True,
            updated_machine.to_ansible(),
            dict(before=machine.to_ansible(), after=updated_machine.to_ansible()),
        )
    client.post(f"/api/2.0/machines/{machine.id}/", query={"op": "release"}, data={})
    try:  # this is a problem for ephemeral machines
        updated_machine = Task.wait_for_state(machine.id, client, False, MachineTaskState.ready)
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
        Task.wait_for_state(machine.id, client, False, MachineTaskState.allocated)
    if machine.status == "Deployed":
        return (
            False,
            machine.to_ansible(),
            dict(before=machine.to_ansible(), after=machine.to_ansible()),
        )
    if machine.status == "New" or machine.status == "Failed":
        commission(machine.id, client)
        Task.wait_for_state(machine.id, client, False, MachineTaskState.ready)
    if machine.status == "Commissioning":
        # commissioning will bring machine to the ready state
        Task.wait_for_state(machine.id, client, False, MachineTaskState.ready)
    data = {}
    timeout = 20  # seconds
    if module.params["deploy_params"]:
        if module.params["deploy_params"]["osystem"]:
            data["osystem"] = module.params["deploy_params"]["osystem"]
        if module.params["deploy_params"]["distro_series"]:
            data["distro_series"] = module.params["deploy_params"]["distro_series"]
        if module.params["deploy_params"]["timeout"]:
            timeout = module.params["deploy_params"]["timeout"]
    client.post(
        f"/api/2.0/machines/{machine.id}/",
        query={"op": "deploy"},
        data=data,
        timeout=timeout,
    ).json  # here we can get TimeoutError: timed out
    updated_machine = Task.wait_for_state(machine.id, client, False, MachineTaskState.deployed)
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
            arguments.get_spec("instance"),
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
                ),
            ),
            allocate_params=dict(
                type="dict",
                options=dict(
                    cores=dict(type="int"),
                    memory=dict(type="int"),
                ),
            ),
        ),
        required_if=[
            ("state", "absent", ("hostname",), False),
            ("state", "ready", ("hostname",), False),
        ],
    )

    try:
        instance = module.params["instance"]
        host = instance["host"]
        client_key = instance["client_key"]
        token_key = instance["token_key"]
        token_secret = instance["token_secret"]

        client = Client(host, token_key, token_secret, client_key)
        changed, record, diff = run(module, client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
