# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type


from .client import Client


def get_oauth1_client(params):
    cluster_instance = params["cluster_instance"]
    host = cluster_instance["host"]
    consumer_key = cluster_instance["customer_key"]
    token_key = cluster_instance["token_key"]
    token_secret = cluster_instance["token_secret"]

    client = Client(host, token_key, token_secret, consumer_key)
    return client
