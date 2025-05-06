# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Arkadiy Shinkarev | Tinkoff <a.shinkarev@tinkoff.ru>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

from ansible_collections.canonical.maas.plugins.modules import package_repository
from ansible_collections.canonical.maas.plugins.module_utils.package_repository import (
    PackageRepository,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_all_params(self, run_main):
        params = dict(
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

        success, result = run_main(package_repository, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            state="present",
            name="Ubuntu archive",
            url="http://archive.ubuntu.com/ubuntu",
        )

        success, result = run_main(package_repository, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(package_repository)

        assert success is False
        assert "missing required arguments: name, state, url" in result["msg"]


class TestDataForCreatePackageRepository:
    def test_data_for_create_package_repository(self, create_module):
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
                components=["main"],
                arches=["amd64", "i386"],
                key="",
                enabled=True,
            )
        )
        data = package_repository.data_for_create_package_repository(module)

        assert data == dict(
            name="Ubuntu archive",
            url="http://archive.ubuntu.com/ubuntu",
            distributions="focal",
            disabled_pockets="updates",
            disabled_components="restricted",
            disable_sources=True,
            components="main",
            arches="amd64,i386",
            enabled=True,
        )


class TestDataForUpdatePackageRepository:
    def test_data_for_update_package_repository(self, create_module):
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
                components=["main"],
                arches=["amd64"],
                key="",
                enabled=False,
            )
        )
        old_package_repository = PackageRepository(
            name="Ubuntu archive",
            url="http://archive.ubuntu.com/ubuntu",
            disable_sources=False,
            key="",
            enabled=True,
        )
        data = package_repository.data_for_update_package_repository(
            module, old_package_repository
        )

        assert data == dict(
            distributions="focal",
            disabled_pockets="updates",
            disabled_components="restricted",
            disable_sources=True,
            components="main",
            arches="amd64",
            enabled=False,
        )
