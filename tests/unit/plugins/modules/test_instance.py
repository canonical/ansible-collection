# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>  # WHAT TO WRITE HERE?
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest
from ansible_collections.canonical.maas.plugins.modules import instance
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


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
                    "cores": 1,
                    "zone": "my_zone",
                    "pool": "my_pool",
                    "tags": None,
                },
                network_interfaces={
                    "name": "my_network",
                    "subnet_cidr": "10.10.10.10/24",
                    "ip_address": "10.10.10.190",
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
            data={
                "cpu_count": 1,
                "mem": 2000,
                "zone": "my_zone",
                "pool": "my_pool",
                "interfaces": "my_network:subnet_cidr=10.10.10.10/24,ip=10.10.10.190",
            },
        )

    def test_allocate_tags(self, client, create_module, mocker):
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
                    "memory": None,
                    "cores": None,
                    "zone": None,
                    "pool": None,
                    "tags": ["my_tag"],
                },
                network_interfaces=None,
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.from_maas"
        )

        instance.allocate(module, client)

        client.post.assert_called_with(
            "/api/2.0/machines/",
            query={"op": "allocate"},
            data={
                "tag_names": "my_tag",
            },
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
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            hostname="my_instance",
            id=123456,
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
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = None

        changed = instance.delete(module, client)[0]

        assert changed is False


class TestRelease:
    def test_release_status_ready(self, create_module, client, mocker):
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
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            status="Ready",
        )

        result = instance.release(module, client)

        assert result[0] is False

    def test_release_status_commissioning(self, create_module, client, mocker):
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
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status="Commissioning",
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        result = instance.release(module, client)

        assert result[0] is False

    @pytest.mark.parametrize("status", ["New", "Failed"])
    def test_release_status_new_or_failed(self, create_module, client, mocker, status):
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
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status=status,
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.commission"
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        result = instance.release(module, client)

        assert result[0] is True

    def test_release_status_deployed(self, create_module, client, mocker):
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
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status="Deployed",
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        changed = instance.release(module, client)[0]

        client.post.assert_called_with(
            "/api/2.0/machines/123456/", query={"op": "release"}, data={}
        )
        assert changed is True


class TestDeploy:
    def test_deploy_name_not_provided(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    token_key="URCfn6EhdZ",
                    token_secret="PhXz3ncACvkcK",
                    client_key="nzW4EBWjyDe",
                ),
                hostname=None,
                state="ready",
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                    "timeout": 30,
                    "hwe_kernel": "my_kernel",
                    "user_data": "my_data",
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
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        result = instance.deploy(module, client)

        client.post.assert_called_with(
            "/api/2.0/machines/123456/",
            query={"op": "deploy"},
            data={
                "osystem": "ubuntu",
                "distro_series": "jammy",
                "hwe_kernel": "my_kernel",
                "user_data": "my_data",
            },
            timeout=30,
        )
        assert result[0] is True

    def test_deploy_status_deployed(self, create_module, client, mocker):
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
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                    "timeout": 30,
                    "hwe_kernel": "my_kernel",
                    "user_data": "my_data",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            status="Deployed",
        )

        changed = instance.deploy(module, client)[0]

        assert changed is False

    def test_deploy_status_commissioning(self, create_module, client, mocker):
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
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                    "timeout": 30,
                    "hwe_kernel": "my_kernel",
                    "user_data": "my_data",
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
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        result = instance.deploy(module, client)

        client.post.assert_called_with(
            "/api/2.0/machines/123456/",
            query={"op": "deploy"},
            data={
                "osystem": "ubuntu",
                "distro_series": "jammy",
                "hwe_kernel": "my_kernel",
                "user_data": "my_data",
            },
            timeout=30,
        )
        assert result[0] is True

    @pytest.mark.parametrize("status", ["New", "Failed"])
    def test_release_status_new_or_failed(self, create_module, client, mocker, status):
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
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                    "timeout": 30,
                    "hwe_kernel": "my_kernel",
                    "user_data": "my_data",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status=status,
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.commission"
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        result = instance.deploy(module, client)
        client.post.assert_called_with(
            "/api/2.0/machines/123456/",
            query={"op": "deploy"},
            data={
                "osystem": "ubuntu",
                "distro_series": "jammy",
                "hwe_kernel": "my_kernel",
                "user_data": "my_data",
            },
            timeout=30,
        )
        assert result[0] is True

    def test_deploy_status_ready(self, create_module, client, mocker):
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
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                    "timeout": 30,
                    "hwe_kernel": "my_kernel",
                    "user_data": "my_data",
                },
            ),
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.get_by_name"
        ).return_value = Machine(
            id=123456,
            status="Ready",
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.Machine.wait_for_state"
        )

        result = instance.deploy(module, client)

        client.post.assert_called_with(
            "/api/2.0/machines/123456/",
            query={"op": "deploy"},
            data={
                "osystem": "ubuntu",
                "distro_series": "jammy",
                "hwe_kernel": "my_kernel",
                "user_data": "my_data",
            },
            timeout=30,
        )
        assert result[0] is True


class TestMain:
    # in module diff needs to be added for this to work
    def test_all_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            hostname=None,
            state="ready",
            allocate_params={
                "memory": 2000,
                "cores": 1,
                "zone": "my_zone",
                "pool": "my_pool",
                "tags": None,
            },
            network_interfaces={
                "name": "my_network",
                "subnet_cidr": "10.10.10.10/24",
                "ip_address": "10.10.10.190",
            },
            deploy_params={
                "osystem": "ubuntu",
                "distro_series": "jammy",
                "timeout": 30,
                "hwe_kernel": "my_kernel",
                "user_data": "my_data",
            },
        )

        success, result = run_main(instance, params)

        assert success is True

    def test_minimal_set_of_params(self, run_main):
        params = dict(
            instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            state="deployed",
        )

        success, result = run_main(instance, params)

        assert success is True

    @pytest.mark.parametrize("state", ["ready", "absent"])
    def test_required_if(self, run_main, state):
        params = dict(
            instance=dict(
                host="https://0.0.0.0",
                token_key="URCfn6EhdZ",
                token_secret="PhXz3ncACvkcK",
                customer_key="nzW4EBWjyDe",
            ),
            state=state,
        )

        success, result = run_main(instance, params)

        assert success is False

    def test_fail(self, run_main):
        success, result = run_main(instance)

        assert success is False
        assert "missing required arguments: state" in result["msg"]
