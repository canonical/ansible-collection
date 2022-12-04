#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: package_repository

author:
  - Arkadiy Shinkarev (@k3nny0ne)
short_description: Creates, updates or deletes MAAS Package Repositories.
description:
  - If I(state) is C(present) and I(name) is provided but not found, new Package Repository
    with specified options is created.
  - If I(state) is C(present) and I(name) is found, updates an existing Package Repository.
  - If I(state) is C(absent) Package Repository selected by I(name) is deleted.
version_added: 1.0.0
extends_documentation_fragment:
  - canonical.maas.cluster_instance
seealso: []
options:
  state:
    description:
      - Desired state of the Package Repository.
    choices: [ present, absent ]
    type: str
    required: True
  name:
    description:
      - The name of the package repository.
    type: str
    required: True
  url:
    description:
      - The url of the package repository.
    type: str
    required: True
  distributions:
    description:
      - List of package distributions to include.
    type: list
    elements: str
  disabled_pockets:
    description:
      - The list of pockets to disable.
    type: list
    elements: str
  disabled_components:
    description:
      - The list of components to disable.
      - Only applicable to the default Ubuntu repositories.
    type: list
    elements: str
  disable_sources:
    description:
      - Disable deb-src lines.
    type: bool
  components:
    description:
      - The list of components to enable.
      - Only applicable to custom repositories.
    type: list
    elements: str
  arches:
    description:
      - The list of supported architectures.
    type: list
    elements: str
  key:
    description:
      - The authentication key to use with the repository.
    type: str
  enabled:
    description:
      - Whether or not the repository is enabled.
    type: bool
"""

EXAMPLES = r"""
- name: Create Package Repository
  canonical.maas.package_repository:
    state: present
    name: Ubuntu archive
    url: http://archive.ubuntu.com/ubuntu
    arches:
      - amd64
      - i386
    disable_sources: true

- name: Update Package Repository
  canonical.maas.package_repository:
    state: present
    name: Ubuntu archive
    url: http://archive.ubuntu.com/ubuntu
    arches:
      - amd64
      - i386
    disable_sources: true
    disabled_components:
      - universe
      - multiverse

- name: Remove Package Repository
  canonical.maas.package_repository:
    state: absent
    name: Ubuntu archive
    url: http://archive.ubuntu.com/ubuntu
"""

RETURN = r"""
record:
  description:
    - Created or updated Package Repository.
  returned: success
  type: dict
  sample:
    id: 1
    name: Ubuntu archive
    url: http://archive.ubuntu.com/ubuntu
    distributions: []
    disabled_pockets: []
    disabled_components: []
    disable_sources: true
    components: []
    arches:
      - amd64
      - i386
    key: ""
    enabled: true
    resource_uri: /MAAS/api/2.0/package-repositories/1/
"""


from ansible.module_utils.basic import AnsibleModule

from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.package_repository import PackageRepository
from ..module_utils.cluster_instance import get_oauth1_client


def data_for_create_package_repository(module):
    data = {}
    data["name"] = module.params["name"]  # required
    data["url"] = module.params["url"]  # required
    if module.params["distributions"]:
        data["distributions"] = ",".join(module.params["distributions"])
    if module.params["disabled_pockets"]:
        data["disabled_pockets"] = ",".join(module.params["disabled_pockets"])
    if module.params["disabled_components"]:
        data["disabled_components"] = ",".join(module.params["disabled_components"])
    if module.params["disable_sources"] is not None:
        data["disable_sources"] = module.params["disable_sources"]
    if module.params["components"]:
        data["components"] = ",".join(module.params["components"])
    if module.params["arches"]:
        data["arches"] = ",".join(module.params["arches"])
    if module.params["key"]:
        data["key"] = module.params["key"]
    if module.params["enabled"] is not None:
        data["enabled"] = module.params["enabled"]

    return data


def create_package_repository(module, client: Client):
    data = data_for_create_package_repository(module)
    package_repository = PackageRepository.create(client, data)
    if module.params["disable_sources"]:  # this parameter can only be set with put
        data = data_for_update_package_repository(module, package_repository)
        package_repository.update(client, data)
    return (
        True,
        package_repository.to_ansible(),
        dict(before={}, after=package_repository.to_ansible()),
    )


def data_for_update_package_repository(module, package_repository):
    data = {}
    if module.params["name"]:
        if package_repository.name != module.params["name"]:
            data["name"] = module.params["name"]
    if module.params["url"]:
        if package_repository.url != module.params["url"]:
            data["url"] = module.params["url"]
    if module.params["distributions"]:
        if package_repository.distributions != module.params["distributions"]:
            data["distributions"] = ",".join(module.params["distributions"])
    if module.params["disabled_pockets"]:
        if package_repository.disabled_pockets != module.params["disabled_pockets"]:
            data["disabled_pockets"] = ",".join(module.params["disabled_pockets"])
    if module.params["disabled_components"]:
        if (
            package_repository.disabled_components
            != module.params["disabled_components"]
        ):
            data["disabled_components"] = ",".join(module.params["disabled_components"])
    if module.params["disable_sources"] is not None:
        if package_repository.disable_sources != module.params["disable_sources"]:
            data["disable_sources"] = module.params["disable_sources"]
    if module.params["components"]:
        if package_repository.components != module.params["components"]:
            data["components"] = ",".join(module.params["components"])
    if module.params["arches"]:
        if package_repository.arches != module.params["arches"]:
            data["arches"] = ",".join(module.params["arches"])
    if module.params["key"]:
        if package_repository.key != module.params["key"].rstrip("\n"):
            data["key"] = module.params["key"]
    if module.params["enabled"] is not None:
        if package_repository.enabled != module.params["enabled"]:
            data["enabled"] = module.params["enabled"]
    return data


def update_package_repository(module, client: Client, package_repository):
    data = data_for_update_package_repository(module, package_repository)
    if data:
        updated_package_repository_maas_dict = package_repository.update(client, data)
        package_repository_after = PackageRepository.from_maas(
            updated_package_repository_maas_dict
        )
        return (
            True,
            package_repository_after.to_ansible(),
            dict(
                before=package_repository.to_ansible(),
                after=package_repository_after.to_ansible(),
            ),
        )
    return (
        False,
        package_repository.to_ansible(),
        dict(
            before=package_repository.to_ansible(),
            after=package_repository.to_ansible(),
        ),
    )


def delete_package_repository(module, client: Client):
    package_repository = PackageRepository.get_by_name(module, client, must_exist=False)
    if package_repository:
        package_repository.delete(client)
        return True, dict(), dict(before=package_repository.to_ansible(), after={})
    return False, dict(), dict(before={}, after={})


def run(module, client: Client):
    if module.params["state"] == "present":
        package_repository = PackageRepository.get_by_name(
            module, client, must_exist=False
        )
        if package_repository:
            return update_package_repository(module, client, package_repository)
        return create_package_repository(module, client)
    if module.params["state"] == "absent":
        return delete_package_repository(module, client)


def main():
    module = AnsibleModule(
        supports_check_mode=False,
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            state=dict(type="str", choices=["present", "absent"], required=True),
            name=dict(type="str", required=True),
            url=dict(type="str", required=True),
            distributions=dict(type="list", elements="str"),
            disabled_pockets=dict(type="list", elements="str"),
            disabled_components=dict(type="list", elements="str"),
            disable_sources=dict(type="bool"),
            components=dict(type="list", elements="str"),
            arches=dict(type="list", elements="str"),
            key=dict(type="str", no_log=False),
            enabled=dict(type="bool"),
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
