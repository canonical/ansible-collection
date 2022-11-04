# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils import errors


class Tag:
    @staticmethod
    def send_tag_request(client, machine_id, tag_name):
        payload = dict(add=machine_id)
        client.post(
            f"/api/2.0/tags/{tag_name}/",
            query={"op": "update_nodes"},
            data=payload,
        ).json

    @staticmethod
    def sent_untag_request(client, machine_id, tag_name):
        payload = dict(remove=machine_id)
        client.post(
            f"/api/2.0/tags/{tag_name}/",
            query={"op": "update_nodes"},
            data=payload,
        ).json

    @staticmethod
    def get_tag_by_name(client, module, must_exist=False):
        response = client.get("/api/2.0/tags/").json
        for tag in response:
            if tag["name"] == module.params["name"]:
                return tag
        if must_exist:
            raise errors.MaasError(f"Tag - {module.params['name']} - does not exist.")

    @staticmethod
    def send_create_request(client, module):
        payload = dict(name=module.params["name"])
        client.post(
            "/api/2.0/tags/",
            data=payload,
        )
