# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


def to_ansible(record, is_resource_record=False):
    resource_records = [record] if is_resource_record else record.get("resource_records", [])
    name, domain = record["fqdn"].rsplit(".", 1)

    if resource_records:
        result = [{
            "type": item["rrtype"],
            "data": item["rrdata"],
            "fqdn": record["fqdn"],
            "name": name,
            "domain": domain,
            "ttl": item["ttl"],
            "id": item["id"],
        } for item in resource_records]
        return result

    ip_addresses = [x["ip"] for x in record["ip_addresses"] if x["ip"]]
    if ip_addresses:
        return [{
            "type": "A/AAAA",
            "data": " ".join(ip_addresses),
            "fqdn": record["fqdn"],
            "name": name,
            "domain": domain,
            "ttl": record["address_ttl"],
            "id": record["id"],
        }]
    return []
