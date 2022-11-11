# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.module_utils.tag import Tag
from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.module_utils.client import (
    Response,
)

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestRequest:
    def test_send_tag_request(self, client):
        machine_id = "test-id"
        tag_name = "test"
        client.post.return_value = Response(200, "[]")
        results = Tag.send_tag_request(client, machine_id, tag_name)
        assert results is None

    def test_send_untag_request(self, client):
        machine_id = "test-id"
        tag_name = "test"
        client.post.return_value = Response(200, "[]")
        results = Tag.send_untag_request(client, machine_id, tag_name)
        assert results is None

    def test_send_create_request(self, create_module, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="this_tag",
                machines=["this_machine", "that_machine"],
            )
        )
        client.post.return_value = Response(200, "[]")
        results = Tag.send_create_request(client, module)
        assert results is None


class TestGet:
    def test_get_tag_by_name_must_exist_true(self, create_module, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="one",
                machines=["this_machine", "that_machine"],
            )
        )
        client.get.return_value = Response(200, '[{"name":"one"}, {"name":"two"}]')
        results = Tag.get_tag_by_name(client, module, must_exist=True)
        assert results == {"name": "one"}

    def test_get_tag_by_name_must_exist_true_and_not_exist(self, create_module, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="one",
                machines=["this_machine", "that_machine"],
            )
        )
        client.get.return_value = Response(200, "[]")
        with pytest.raises(
            errors.MaasError,
            match=f"Tag - {module.params['name']} - does not exist.",
        ):
            Tag.get_tag_by_name(client, module, must_exist=True)

    def test_get_tag_by_name_must_exist_false(self, create_module, client):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="one",
                machines=["this_machine", "that_machine"],
            )
        )
        client.get.return_value = Response(200, '[{"name":"one"}, {"name":"two"}]')
        results = Tag.get_tag_by_name(client, module, must_exist=False)
        assert results == {"name": "one"}

    def test_get_tag_by_name_must_exist_false_and_not_exist(
        self, create_module, client
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    client_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="set",
                name="one",
                machines=["this_machine", "that_machine"],
            )
        )
        client.get.return_value = Response(200, "[]")
        results = Tag.get_tag_by_name(client, module, must_exist=False)
        assert results is None
