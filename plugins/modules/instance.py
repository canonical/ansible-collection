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
    If I(hostname) is not provided, a random machine will be allocated using I(allocate_params).
    If no parameters are given, a random machine will be allocated using the defaults.
    In case if no machine matching the given constraints could be found, the task will FAIL.
  - If I(state) value is C(absent) the selected machine will be deleted.
version_added: 1.0.0
extends_documentation_fragment: # ADD DOC_FRAGMENT FOR VM_HOST
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
    type: dict
    options:
      cpu:
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
      - If no parameters are given, a random machine will be allocated and deployed using the defaults.
      - Relevant only if I(state) value is C(deployed)
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
"""

EXAMPLES = r"""
name: Remove/delete an instance
canonical.maas.instance:
  hostname: my_instance
  state: absent

name: Commision new machine with custom constraints
canonical.maas.instance:
  state: ready
  allocate_params:
    cpu: 1
    memory: 2

name: Commision new machine with default constraints
canonical.maas.instance:
  state: ready

name: Release machine
canonical.maas.instance:
  hostname: my_instance
  state: ready

name: Deploy already commisioned machine
canonical.maas.instance:
  hostname: my_instance
  state: deployed

name: Deploy already commisioned machine with custom OS and OS series
canonical.maas.instance:
  hostname: my_instance
  state: deployed
  deploy_params:
    osystem: ubuntu
    distro_series: focal

name: Deploy new machine with default OS and allocation constraints
canonical.maas.instance:
  state: deployed

name: Deploy new machine with custom OS and allocation constraints
canonical.maas.instance:
  state: deployed
  allocate_params:
    cpu: 1
    memory: 2
  deploy_params:
    osystem: ubuntu
    distro_series: focal
"""

RETURN = r"""
record:
  description:
    - The deployed/released machine instance
  returned: success
  type: dict
  sample:
   # ADD SAMPLE
"""
from time import sleep
from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient


def wait_ready_or_allocated_state(system_id, client: Client, check_mode=False):
    if check_mode:
        return
    while True:
        rest_client = RestClient(client)
        instance = rest_client.get_record(
            f"/api/2.0/machines/{system_id}/", must_exist=True
        )
        if get_instance_status(instance) in (
            "ready",
            "allocated",
        ):  # IMPLEMENT TIMEOUT?
            return instance
        sleep(1)


def get_instance_from_hostname(module, client: Client, must_exist):
    rest_client = RestClient(client)
    query = {"hostname": module.params["hostname"]}
    instance = rest_client.get_record(
        "/api/2.0/machines/", query, must_exist=must_exist
    )
    return instance


def allocate(module, client: Client):
    data = {}
    if module.params["allocate_params"]:
        if module.params["allocate_params"]["cpu"]:
            data["cpu_count"] = module.params["allocate_params"]["cpu"]
        if module.params["allocate_params"]["memory"]:
            data["mem"] = module.params["allocate_params"]["memory"]
        # here an error can occur:
        # HTTP Status Code : 409
        # Content : No machine matching the given constraints could be found.
        # instance can't be allocated if commissioning, the only action allowed is abort
    instance = client.post(
        "/api/2.0/machines/", query={"op": "allocate"}, data=data
    ).json
    return instance


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
    instance = client.post(
        f"/api/2.0/machines/{system_id}", query={"op": "commission"}
    ).json
    return instance


def get_instance_id(instance):
    return instance["boot_interface"]["system_id"]


def get_instance_status(instance):
    return instance["status_name"]


def delete(module, client: Client):
    instance = get_instance_from_hostname(module, client, must_exist=False)
    if instance:
        system_id = get_instance_id(instance)
        response = client.delete(f"/api/2.0/machines/{system_id}/").json
        return True, response  # CHECK WHAT IS RESPPONSE
    return False, dict()


def release(module, client: Client):
    if module.params["hostname"]:
        instance = get_instance_from_hostname(module, client, must_exist=True)
    else:
        # allocate random machine - IF THERE IS NO MACHINE TO ALLOCATE, NEW IS PRODUCED BUT IT CAN'T BE RELEASED!! - THIS NEEDS TO BE SOLVED!
        instance = allocate(module, client)
    system_id = get_instance_id(instance)
    status = get_instance_status(instance)
    if status == "ready" or "commissioning":
        # commissioning will bring machine to the ready state - SHOULD WE WAIT FO READY STATE?
        # if state == commissioning: "Unexpected response - 409 b\"Machine cannot be released in its current state ('Commissioning').\""
        return False, instance  # or empty dict?
    if status == "new":
        # commissioning will bring machine to the ready state - SHOULD WE WAIT FO READY STATE?
        instance = commission(system_id, client)
        return True, instance
    else:
        instance = client.post(
            f"/api/2.0/machines/{system_id}/", query={"op": "release"}, data={}
        ).json
        return True, instance


def deploy(module, client: Client):
    if module.params["hostname"]:
        instance = get_instance_from_hostname(module, client, must_exist=True)
    else:
        # allocate random machine # IF THERE IS NO MACHINE TO ALLOCATE, NEW IS PRODUCED BUT IT CAN'T BE RELEASED!! - THIS NEEDS TO BE SOLVED!
        instance = allocate(module, client)

    status = get_instance_status(instance)
    system_id = get_instance_id(instance)
    if status == "deployed":
        return False, instance  # or empty dict?
    if status == "new":
        commission(system_id, client)
    wait_ready_or_allocated_state(system_id, client)
    data = {}
    if module.params["deploy_params"]:
        if module.params["deploy_params"]["osystem"]:
            data["osystem"] = module.params["deploy_params"]["osystem"]
        if module.params["deploy_params"]["distro_series"]:
            data["distro_series"] = module.params["deploy_params"]["distro_series"]
    instance = client.post(
        f"/api/2.0/machines/{system_id}/", query={"op": "deploy"}, data=data
    ).json
    return True, instance


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
                ),
            ),
            allocate_params=dict(
                type="dict",
                options=dict(
                    cpu=dict(type="int"),
                    memory=dict(type="int"),
                ),
            ),
        ),
        required_if=[
            ("state", "absent", ("hostname"), False),
        ],
    )

    try:
        instance = module.params["instance"]
        host = instance["host"]
        client_key = instance["client_key"]
        token_key = instance["token_key"]
        token_secret = instance["token_secret"]

        client = Client(host, token_key, token_secret, client_key)
        changed, record = run(module, client)
        module.exit_json(changed=changed, record=record)
    except errors.MaasError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
