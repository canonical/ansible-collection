# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.package_repository import (
    PackageRepository,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMapper:
    def test_from_maas(self):
        maas_package_repository_dict = get_package_repository()
        package_repository = PackageRepository(**get_package_repository())
        results = PackageRepository.from_maas(maas_package_repository_dict)
        assert results == package_repository

    def test_to_ansible(self):
        package_repository = PackageRepository(**get_package_repository())
        ansible_dict = get_package_repository()

        results = package_repository.to_ansible()
        assert results == ansible_dict


class TestGet:
    def test_get_by_name(self, create_module, mocker, client):
        module = create_module(
            params=dict(
                cluster_instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    customer_key="nzW4EBWjyDe",
                ),
                state="present",
                name="Ubuntu archive",
                url="http://archive.ubuntu.com/ubuntu",
                distributions=["focal"],
                disabled_pockets=["updates"],
                disabled_components=["restricted"],
                disable_sources=True,
                components="main",
                arches=["amd64"],
                key="",
                enabled=True,
            )
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.RestClient.get_record"
        ).return_value = dict(
            id=1,
            name="Ubuntu archive",
            url="http://archive.ubuntu.com/ubuntu",
            distributions=["focal"],
            disabled_pockets=["updates"],
            disabled_components=["restricted"],
            disable_sources=True,
            components="main",
            arches=["amd64"],
            key="",
            enabled=True,
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )

        assert PackageRepository.get_by_name(module, client, True) == PackageRepository(
            id=1,
            name="Ubuntu archive",
            url="http://archive.ubuntu.com/ubuntu",
            distributions=["focal"],
            disabled_pockets=["updates"],
            disabled_components=["restricted"],
            disable_sources=True,
            components="main",
            arches=["amd64"],
            key="",
            enabled=True,
            resource_uri="/MAAS/api/2.0/vlans/5014/",
        )


def get_package_repository():
    return dict(
        id=1,
        name="Ubuntu archive",
        url="http://archive.ubuntu.com/ubuntu",
        distributions=["focal"],
        disabled_pockets=["updates"],
        disabled_components=["restricted"],
        disable_sources=True,
        components="main",
        arches=["amd64"],
        key="",
        enabled=True,
        resource_uri="/MAAS/api/2.0/package-repositories/1/",
    )
