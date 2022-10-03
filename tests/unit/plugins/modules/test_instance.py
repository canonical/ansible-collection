# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>  # WHAT TO WRITE HERE?
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import instance

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)

"""
class TestGetInstanceFromHostname:
    def test_get_instance(self, create_module, mocker, client):
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
                allocation_params={
                    "memory": 512,
                    "cpu": 1,
                },
                deploy_params={
                    "osystem": "ubuntu",
                    "distro_series": "jammy",
                },
            ),
        )

        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.instance.get_instance_from_hostname.instance"
        ).return_value = dict(
            hostname="my_instance",
        )

        # rest_client.get_record.return_value = dict(
        #     hostname="my_instance",
        # )

        assert instance.get_instance_from_hostname(module, client) == dict(
            hostname="my_instance",
        )
"""
