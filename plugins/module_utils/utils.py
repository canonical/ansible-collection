# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def filter_dict(input, *field_names):
    output = {}
    for field_name in field_names:
        if field_name not in input:
            continue
        value = input[field_name]
        if value is not None:
            output[field_name] = value
    return output


def is_superset(superset, candidate):
    if not candidate:
        return True
    for k, v in candidate.items():
        if k in superset and superset[k] == v:
            continue
        return False
    return True


def filter_results(results, filter_data):
    return [element for element in results if is_superset(element, filter_data)]
