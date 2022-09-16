# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback

SHARED_SPECS = dict(
    instance=dict(
        type="dict",
        apply_defaults=True,
        options=dict(
            host=dict(
                type="str",
                required=True,
                fallback=(env_fallback, ["MASS_HOST"]),
            ),
            token_key=dict(
                type="str",
                required=True,
                fallback=(env_fallback, ["MASS_TOKEN_KEY"]),
            ),
            token_secret=dict(
                type="str",
                required=True,
                fallback=(env_fallback, ["MASS_TOKEN_SECRET"]),
            ),
            client_key=dict(
                type="str",
                required=True,
                fallback=(env_fallback, ["MASS_CLIENT_KEY"]),
            )            
        )
    )
)


def get_spec(*param_names):
    return dict((p, SHARED_SPECS[p]) for p in param_names)
