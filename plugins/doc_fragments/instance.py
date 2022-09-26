# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  cluster_instance:
    description:
      - Canonical MAAS instance information.
    type: dict
    suboptions:
      host:
        description:
          - The MAAS instance url.
          - If not set, the value of the C(MASS_HOST) environment
            variable will be used.
          - For example "http://localhost:5240/MAAS".
        required: true
        type: str
      token_key:
        description:
          - Token key used for authentication.
          - If not set, the value of the C(MASS_TOKEN_KEY) environment
            variable will be used.
        required: true
        type: str
      token_secret:
        description:
          - Token secret used for authentication.
          - If not set, the value of the C(MASS_TOKEN_SECRET) environment
            variable will be used.
        required: true
        type: str
      client_key:
        description:
          - Client secret used for authentication.
          - If not set, the value of the C(MASS_CLIENT_KEY) environment
            variable will be used.
        required: true
        type: str
"""
