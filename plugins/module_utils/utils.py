# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from abc import abstractmethod

__metaclass__ = type


class MaasValueMapper:

    """
    Represent abstract class.
    """

    @abstractmethod
    def to_ansible(self):
        """
        Transforms from python-native to ansible-native object.
        :return: ansible-native dictionary.
        """
        pass

    @abstractmethod
    def to_maas(self):
        """
        Transforms python-native to maas-native object.
        :return: maas-native dictionary.
        """
        pass

    @classmethod
    @abstractmethod
    def from_ansible(cls, module):
        """
        Transforms from ansible_data (module.params) to python-object.
        :param ansible_data: Field that is inputed from ansible playbook. Is most likely
        equivalent to "module.params" in python
        :return: python object
        """
        pass

    @classmethod
    @abstractmethod
    def from_maas(cls, maas_dict):
        """
        Transforms from maas-native dictionary to python-object.
        :param maas_dict: Dictionary from maas API
        :return: python object
        """
        pass


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


def get_query(module, *field_names, ansible_maas_map):
    """
    Wrapps filter_dict and transform_ansible_to_maas_query. Prefer to use 'get_query' over filter_dict
    even if there's no mapping between maas and ansible columns for the sake of verbosity and consistency
    """
    ansible_query = filter_dict(module.params, *field_names)
    maas_query = transform_query(ansible_query, ansible_maas_map)
    return maas_query


def transform_query(raw_query, query_map):
    # Transforms query by renaming raw_query's keys by specifying those keys and the new values in query_map
    return {query_map[key]: raw_query[key] for key, value in raw_query.items()}


def is_changed(before, after):
    return not before == after
