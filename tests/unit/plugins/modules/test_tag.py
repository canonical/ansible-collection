# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.machine import (
    Machine,
)
from ansible_collections.canonical.maas.plugins.modules import tag

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            machines=[],
            name="this_name",
            state="present",
        )

        success, results = run_main(tag, params)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            machines=[],
            name="this_name",
            state="present",
        )

        success, results = run_main(tag, params)
        assert success is True
        assert results == {
            "changed": False,
            "records": {},
            "diff": {"before": {}, "after": {}},
        }


class TestRun:
    def test_run_with_present(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="customer key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.ensure_present"
        ).return_value = (False, {}, {"before": [], "after": []})
        results = tag.run(module, client)
        assert results == (False, {}, {"before": [], "after": []})

    def test_run_with_absent(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.ensure_absent"
        ).return_value = (False, {}, {"before": [], "after": []})
        results = tag.run(module, client)
        assert results == (False, {}, {"before": [], "after": []})

    def test_run_with_set(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.ensure_set"
        ).return_value = (False, {}, {"before": [], "after": []})
        results = tag.run(module, client)
        assert results == (False, {}, {"before": [], "after": []})


class TestEnsure:
    def test_ensure_present(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        machine_obj_list = ["this_machine", "that_machine"]
        before = []
        after = []
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_id_from_fqdn"
        ).return_value = machine_obj_list
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.get_tag_by_name"
        ).return_value = {"name": "this_tag"}
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.create_tag"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.add_tag_to_machine"
        ).return_value = (before, after)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.get_after"
        ).return_value = after
        results = tag.ensure_present(module, client)
        assert results == (False, [], {"before": [], "after": []})

    def test_ensure_absent_when_tag_exist(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        machine_obj_list = ["this_machine", "that_machine"]
        before = []
        after = []
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_id_from_fqdn"
        ).return_value = machine_obj_list
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.get_tag_by_name"
        ).return_value = {"name": "this_tag"}
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.remove_tag_from_machine"
        ).return_value = (before, after)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.get_after"
        ).return_value = after
        results = tag.ensure_absent(module, client)
        assert results == (False, [], {"before": [], "after": []})

    def test_ensure_absent_when_tag_not_exist(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        machine_obj_list = ["this_machine", "that_machine"]
        after = []
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_id_from_fqdn"
        ).return_value = machine_obj_list
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.get_tag_by_name"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.get_after"
        ).return_value = after
        results = tag.ensure_absent(module, client)
        assert results == (False, [], {"before": [], "after": []})

    def test_ensure_set(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        machine_obj_list = ["this_machine", "that_machine"]
        before = []
        after = []
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_id_from_fqdn"
        ).return_value = machine_obj_list
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.get_tag_by_name"
        ).return_value = {"name": "this_tag"}
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_tag"
        ).return_value = machine_obj_list
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.create_tag"
        ).return_value = after
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.add_tag_to_machine"
        ).return_value = (before, after)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.remove_unnecessary_tag_after_set"
        ).return_value = (before, after)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.get_after"
        ).return_value = after
        results = tag.ensure_set(module, client)
        assert results == (False, [], {"before": [], "after": []})


class TestUtils:
    def test_get_after_when_after(self, client, mocker):
        after = ["this", "that"]
        machine1 = Machine(fqdn="one", tags=["first", "second"])
        machine2 = Machine(fqdn="two", tags=["first", "second"])
        updated_machine_list = [machine1, machine2]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_id_from_fqdn"
        ).return_value = updated_machine_list
        results = tag.get_after(client, after)
        assert results == [
            dict(machine="one", tags=["first", "second"]),
            dict(machine="two", tags=["first", "second"]),
        ]

    def test_get_after_when_no_after(self, client):
        after = []
        results = tag.get_after(client, after)
        assert results == []

    def test_create_tag_when_existing(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        existing_tag = dict(name="this_tag")
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.send_create_request"
        ).return_value = None
        results = tag.create_tag(client, module, existing_tag)
        assert results is None

    def test_create_tag_when_no_existing(self, create_module, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        existing_tag = None
        results = tag.create_tag(client, module, existing_tag)
        assert results is None

    def test_add_tag_to_machine_when_add(self, create_module, client, mocker):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        before = ["this"]
        after = ["this"]
        machine1 = Machine(fqdn="one", tags=["first", "second"])
        machine2 = Machine(fqdn="two", tags=["first", "second", "this_tag"])
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.send_tag_request"
        ).return_value = None
        machine_list = [machine1, machine2]
        after.append(machine1.fqdn)
        results = tag.add_tag_to_machine(
            client, module, machine_list, before, after
        )
        assert results == (before, after)

    def test_add_tag_to_machine_when_no_add(self, create_module, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        before = ["this"]
        after = ["this"]
        machine_list = []
        results = tag.add_tag_to_machine(
            client, module, machine_list, before, after
        )
        assert results == (before, after)

    def test_remove_tag_from_machine_when_remove(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        before = ["this"]
        after = ["this"]
        machine1 = Machine(fqdn="one", id=123, tags=["first", "second"])
        machine2 = Machine(
            fqdn="two", id=456, tags=["first", "second", "this_tag"]
        )
        machine_list = [machine1, machine2]
        existing_tag = {"name": "this_tag"}
        after.append(machine2.fqdn)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.tag.Tag.send_untag_request"
        ).return_value = None
        results = tag.remove_tag_from_machine(
            client, module, machine_list, existing_tag, before, after
        )
        assert results == (before, after)

    def test_remove_tag_from_machine_when_no_remove(
        self, create_module, client
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        before = ["this"]
        after = ["this"]
        machine_list = []
        existing_tag = {"name": "this_tag"}
        results = tag.remove_tag_from_machine(
            client, module, machine_list, existing_tag, before, after
        )
        assert results == (before, after)

    def test_remove_unnecessary_tag_after_set_when_remove(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        existing_tag = {"name": "this_tag"}
        machine1_ansible = Machine(
            fqdn="one", tags=["first", "second", "this_tag"]
        )
        machine_list_from_ansible = [machine1_ansible]
        machine1_maas = Machine(
            fqdn="one", tags=["first", "second", "this_tag"]
        )
        machine2_maas = Machine(
            fqdn="two", tags=["first", "second", "this_tag"]
        )
        machine_list_from_maas = [machine1_maas, machine2_maas]
        before = ["this"]
        after = ["this"]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.remove_tag_from_machine"
        ).return_value = (before, after)
        results = tag.remove_unnecessary_tag_after_set(
            client,
            module,
            existing_tag,
            machine_list_from_ansible,
            machine_list_from_maas,
            before,
            after,
        )
        assert results == (before, after)

    def test_remove_unnecessary_tag_after_set_when_no_remove(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        existing_tag = {"name": "this_tag"}
        machine1_ansible = Machine(
            fqdn="one", tags=["first", "second", "this_tag"]
        )
        machine_list_from_ansible = [machine1_ansible]
        machine_list_from_maas = []
        before = ["this"]
        after = ["this"]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.tag.remove_tag_from_machine"
        ).return_value = (before, after)
        results = tag.remove_unnecessary_tag_after_set(
            client,
            module,
            existing_tag,
            machine_list_from_ansible,
            machine_list_from_maas,
            before,
            after,
        )
        assert results == (before, after)
