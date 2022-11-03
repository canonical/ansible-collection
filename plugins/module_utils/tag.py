# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ..module_utils import errors
from ..module_utils.rest_client import RestClient

class Tag():
    @staticmethod
    def send_tag_request(client, machine_id_list, tag_name):
        # Can't send a whole list, looped request is required.
        for machine_id in machine_id_list:
            payload = dict(add=machine_id)
            client.post(
                f"/api/2.0/tags/{tag_name}/",
                query={"op": "update_nodes"},
                data=payload,
            ).json
