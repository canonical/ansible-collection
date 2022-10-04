# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>  # WHAT TO WRITE HERE?
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from pyrsistent import b

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import instance
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestWaitForState:
    def test_wait_for_state(self, client, mocker):
        system_id = "system_id"
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_id"
        ).return_value = Machine(
            machine_name="my_instance",
            id=123,
            memory=2000,
            cores=2,
            network_interfaces=[],
            disks=[],
            status="Commissioning",
            osystem="ubuntu",
            distro_series="jammy",
        )

        machine = instance.wait_for_state(
            system_id, client, False, "Ready", "Commissioning"
        )

        assert machine.status == "Commissioning"


class TestAllocate:
    def test_allocate(self, client, create_module, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                hostname="my_instance",
                state="ready",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.from_maas"
        )

        instance.allocate(module, client)

        client.post.assert_called_with(
            "/api/2.0/machines/",
            query={"op": "allocate"},
            data={"cpu_count": 1, "mem": 2000},
        )


class TestCommission:
    def test_commission(self, client, mocker):
        system_id = "system_id"
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.from_maas"
        )

        instance.commission(system_id, client)

        client.post.assert_called_with(
            "/api/2.0/machines/system_id",
            query={"op": "commission"},
        )


class TestDelete:
    def test_delete(self, client, mocker, create_module):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                hostname="my_instance",
                state="absent",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            machine_name="my_instance",
            id=123456,
            memory=2000,
            cores=2,
            network_interfaces=[],
            disks=[],
            status="Commissioning",
            osystem="ubuntu",
            distro_series="jammy",
        )

        changed = instance.delete(module, client)[0]

        client.delete.assert_called_with(
            "/api/2.0/machines/123456/",
        )
        assert changed is True

    def test_delete_no_instance(self, client, mocker, create_module):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                hostname="my_instance",
                state="absent",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = None

        changed = instance.delete(module, client)[0]

        assert changed is False


class TestRelease:
    def test_release_name_provided_status_ready(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                name="my_instance",
                state="ready",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            status="Ready",
        )

        result = instance.release(module, client)

        assert result[0] is False

    def test_release_name_provided_status_commissioning(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                name="my_instance",
                state="ready",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status="Commissioning",
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.wait_for_state"
        )

        result = instance.release(module, client)

        assert result[0] is False

    def test_release_name_provided_status_new(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                name="my_instance",
                state="ready",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status="New",
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.commission"
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.wait_for_state"
        )

        result = instance.release(module, client)

        assert result[0] is True

    def test_release_name_provided_status_deployed(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                name="my_instance",
                state="ready",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status="Deployed",
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.wait_for_state"
        )

        changed = instance.release(module, client)[0]

        client.post.assert_called_with(
            "/api/2.0/machines/123456/", query={"op": "release"}, data={}
        )
        assert changed is True

    def test_release_name_not_provided(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                name=None,
                state="ready",
                allocate_params={
                    "memory": 2000,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.allocate"
        ).return_value = Machine(
            id=123456,
            status="Allocated",
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.wait_for_state"
        )

        changed = instance.release(module, client)[0]

        client.post.assert_called_with(
            "/api/2.0/machines/123456/", query={"op": "release"}, data={}
        )
        assert changed is True


class TestMain:
    # in module diff needs to be added for this to work
    def test_all_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                client_key="nzW4EBWjyDe",
            ),
            name=None,
            state="ready",
            allocate_params={
                "memory": 2000,
                "cpu": 1,
            },
            deploy_params={
                "osystem": "ubuntu",
                "distro_series": "jammy",
            },
        )

        success, result = run_main(instance, params)

        assert success is True

    # in module diff needs to be added for this to work
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                client_key="nzW4EBWjyDe",
            ),
            state="ready",
        )

        success, result = run_main(instance, params)

        assert success is True

    def test_fail(self, run_main):
        success, result = run_main(instance)

        assert success is False
        assert "missing required arguments: state" in result["msg"]
