# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from . import errors, utils

__metaclass__ = type


def _query(original=None):
    # Make sure the query isn't equal to None
    # If any default query values need to added in the future, they may be added here
    return dict(original or {})


class RestClient:
    def __init__(self, client):
        self.client = client

    def list_records(self, endpoint, query=None, timeout=120):
        """Results are obtained so that first off, all records are obtained and
        then filtered manually"""
        try:
            records = self.client.get(path=endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.MaasError(f"Request timed out: {e}")
        return utils.filter_results(records, query)

    def get_record(self, endpoint, query=None, must_exist=False, timeout=120):
        records = self.list_records(
            endpoint=endpoint, query=query, timeout=timeout
        )
        if len(records) > 1:
            raise errors.MaasError(
                "{0} records from endpoint {1} match the {2} query.".format(
                    len(records), endpoint, query
                )
            )
        if must_exist and not records:
            raise errors.MaasError(
                "No records from endpoint {0} match the {1} query.".format(
                    endpoint, query
                )
            )
        return records[0] if records else None

    def create_record(self, endpoint, payload, check_mode, timeout=120):
        if check_mode:
            return payload
        try:
            response = self.client.post(
                endpoint, payload, query=_query(), timeout=timeout
            ).json
        except TimeoutError as e:
            raise errors.MaasError(f"Request timed out: {e}")
        return response

    def update_record(
        self, endpoint, payload, check_mode, record=None, timeout=120
    ):
        # No action is possible when updating a record
        if check_mode:
            return payload
        try:
            response = self.client.patch(
                endpoint, payload, query=_query(), timeout=timeout
            ).json
        except TimeoutError as e:
            raise errors.MaasError(f"Request timed out: {e}")
        return response

    def delete_record(self, endpoint, check_mode, timeout=120):
        # No action is possible when deleting a record
        if check_mode:
            return
        try:
            response = self.client.delete(endpoint, timeout=timeout).json
        except TimeoutError as e:
            raise errors.MaasError(f"Request timed out: {e}")
        return response

    def put_record(
        self,
        endpoint,
        payload,
        check_mode,
        timeout=120,
        binary_data=None,
        headers=None,
    ):
        if check_mode:
            return payload

        try:
            response = self.client.put(
                endpoint,
                data=payload,
                query=_query(),
                timeout=timeout,
                binary_data=binary_data,
                headers=headers,
            )
        except TimeoutError as e:
            raise errors.MaasError(f"Request timed out: {e}")
        return response
