# -*- coding: utf-8 -*-
# # Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.canonical.maas.plugins.modules import network_interface_link
from ansible_collections.canonical.maas.plugins.module_utils import errors
from ansible_collections.canonical.maas.plugins.module_utils.network_interface import (
    NetworkInterface,
)
from ansible_collections.canonical.maas.plugins.module_utils.machine import Machine


pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


class TestMain:
    def test_minimal_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            machine="this-machine-fqdn",
            network_interface="this-interface",
            state="present",
            subnet="10.10.10.0/24",
        )

        success, results = run_main(network_interface_link, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }

    def test_maximum_set_of_params(self, run_main):
        params = dict(
            cluster_instance=dict(
                host="https://my.host.name",
                customer_key="client key",
                token_key="token key",
                token_secret="token secret",
            ),
            machine="this-machine-fqdn",
            network_interface="this-interface",
            state="present",
            subnet="10.10.10.0/24",
            mode="AUTO",
            default_gateway=True,
            ip_address="10.10.10.2",
        )

        success, results = run_main(network_interface_link, params)
        assert success is True
        assert results == {
            "changed": False,
            "record": {},
            "diff": {"before": {}, "after": {}},
        }


class TestRun:
    @staticmethod
    def get_machine_state_new():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=None,
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_machine_state_allocating():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=None,
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="Allocating",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_machine_state_ready():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=None,
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="Ready",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-pwoertype",
            architecture="this-architecture",
        )

    def test_run_with_present_with_machine_wrong_state(
        self, create_module, client, mocker
    ):
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="AUTO",
            )
        )
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_fqdn"
        ).return_value = machine_obj
        with pytest.raises(
            errors.MaasError,
            match=f"Machine {machine_obj.hostname} is not in the right state, needs to be in Ready, Allocated or Broken.",
        ):
            network_interface_link.run(module, client)

    def test_run_with_present_with_waiting_on_machine_state(
        self, create_module, client, mocker
    ):
        expected = (False, {}, {"before": {}, "after": {}})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="AUTO",
            )
        )
        machine_dict = self.get_machine_state_allocating()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_fqdn"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.wait_for_state"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.network_interface_link.ensure_present"
        ).return_value = (False, {}, {"before": {}, "after": {}})
        results = network_interface_link.run(module, client)
        assert results == expected

    def test_run_with_present_ensure_present(self, create_module, client, mocker):
        expected = (False, {}, {"before": {}, "after": {}})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="AUTO",
            )
        )
        machine_dict = self.get_machine_state_ready()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_fqdn"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.network_interface_link.ensure_present"
        ).return_value = (False, {}, {"before": {}, "after": {}})
        results = network_interface_link.run(module, client)
        assert results == expected

    def test_run_with_absent_ensure_absent(self, create_module, client, mocker):
        expected = (False, {}, {"before": {}, "after": {}})
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="AUTO",
            )
        )
        machine_dict = self.get_machine_state_ready()
        machine_obj = Machine.from_maas(machine_dict)
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_fqdn"
        ).return_value = machine_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.modules.network_interface_link.ensure_absent"
        ).return_value = (False, {}, {"before": {}, "after": {}})
        results = network_interface_link.run(module, client)
        assert results == expected


class TestEnsurePresent:
    @staticmethod
    def get_alias():
        return dict(
            id=14,
            mode="auto",
            subnet=dict(
                name="subnet-1",
                vlan=dict(
                    vid=0,
                    mtu=1500,
                    dhcp_on=False,
                    external_dhcp=None,
                    relay_vlan=None,
                    name="vlan-1",
                    space="management",
                    secondary_rack="76y7pg",
                    primary_rack="7xtf67",
                    fabric="fabric-1",
                    fabric_id=1,
                    id=5003,
                    resource_uri="/MAAS/api/2.0/vlans/5003/",
                ),
                cidr="10.10.10.0/24",
                rdns_mode=2,
                gateway_ip="10.10.10.1",
                dns_servers=[
                    "fcb0:c682:8c15:817d:7d80:2713:e225:5624",
                    "fd66:86c9:6a50:27cd:de13:3f1c:40d1:8aac",
                    "120.129.237.29",
                ],
                allow_dns=True,
                allow_proxy=True,
                active_discovery=False,
                managed=True,
                space="management",
                id=2,
                resource_uri="/MAAS/api/2.0/subnets/2/",
            ),
        )

    @staticmethod
    def get_updated_alias():
        return dict(
            id=15,
            mode="static",
            subnet=dict(
                name="subnet-1",
                vlan=dict(
                    vid=0,
                    mtu=1500,
                    dhcp_on=False,
                    external_dhcp=None,
                    relay_vlan=None,
                    name="vlan-1",
                    space="management",
                    secondary_rack="76y7pg",
                    primary_rack="7xtf67",
                    fabric="fabric-1",
                    fabric_id=1,
                    id=5003,
                    resource_uri="/MAAS/api/2.0/vlans/5003/",
                ),
                cidr="10.10.10.0/24",
                rdns_mode=2,
                gateway_ip="10.10.10.1",
                dns_servers=[
                    "fcb0:c682:8c15:817d:7d80:2713:e225:5624",
                    "fd66:86c9:6a50:27cd:de13:3f1c:40d1:8aac",
                    "120.129.237.29",
                ],
                allow_dns=True,
                allow_proxy=True,
                active_discovery=False,
                managed=True,
                space="management",
                id=2,
                resource_uri="/MAAS/api/2.0/subnets/2/",
            ),
        )

    @staticmethod
    def get_machine_state_new():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=[
                dict(
                    name="this-nic",
                    id=123,
                    mac_address="this-mac",
                    system_id=123,
                    tags=None,
                    effective_mtu=2000,
                    ip_address="this-ip",
                    cidr="this-cidr",
                    vlan=dict(name="this-vlan", fabric="this-fabric"),
                    links=[],
                )
            ],
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_machine_updated():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=[
                dict(
                    name="this-nic",
                    id=123,
                    mac_address="this-mac",
                    system_id=123,
                    tags=None,
                    effective_mtu=2000,
                    ip_address="this-ip",
                    cidr="this-cidr",
                    vlan=dict(name="this-vlan", fabric="this-fabric"),
                    links=[
                        dict(
                            id=14,
                            mode="auto",
                            subnet=dict(
                                name="subnet-1",
                                vlan=dict(
                                    vid=0,
                                    mtu=1500,
                                    dhcp_on=False,
                                    external_dhcp=None,
                                    relay_vlan=None,
                                    name="vlan-1",
                                    space="management",
                                    secondary_rack="76y7pg",
                                    primary_rack="7xtf67",
                                    fabric="fabric-1",
                                    fabric_id=1,
                                    id=5003,
                                    resource_uri="/MAAS/api/2.0/vlans/5003/",
                                ),
                                cidr="10.10.10.0/24",
                                rdns_mode=2,
                                gateway_ip="10.10.10.1",
                                dns_servers=[
                                    "fcb0:c682:8c15:817d:7d80:2713:e225:5624",
                                    "fd66:86c9:6a50:27cd:de13:3f1c:40d1:8aac",
                                    "120.129.237.29",
                                ],
                                allow_dns=True,
                                allow_proxy=True,
                                active_discovery=False,
                                managed=True,
                                space="management",
                                id=2,
                                resource_uri="/MAAS/api/2.0/subnets/2/",
                            ),
                        )
                    ],
                )
            ],
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_updated_nic():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=None,
            effective_mtu=1500,
            ip_address="this-ip",
            cidr="this-cidr",
            vlan=dict(name="this-vlan", fabric="this-fabric"),
            links=[
                dict(
                    id=14,
                    mode="auto",
                    subnet=dict(
                        name="subnet-1",
                        vlan=dict(
                            vid=0,
                            mtu=1500,
                            dhcp_on=False,
                            external_dhcp=None,
                            relay_vlan=None,
                            name="vlan-1",
                            space="management",
                            secondary_rack="76y7pg",
                            primary_rack="7xtf67",
                            fabric="fabric-1",
                            fabric_id=1,
                            id=5003,
                            resource_uri="/MAAS/api/2.0/vlans/5003/",
                        ),
                        cidr="10.10.10.0/24",
                        rdns_mode=2,
                        gateway_ip="10.10.10.1",
                        dns_servers=[
                            "fcb0:c682:8c15:817d:7d80:2713:e225:5624",
                            "fd66:86c9:6a50:27cd:de13:3f1c:40d1:8aac",
                            "120.129.237.29",
                        ],
                        allow_dns=True,
                        allow_proxy=True,
                        active_discovery=False,
                        managed=True,
                        space="management",
                        id=2,
                        resource_uri="/MAAS/api/2.0/subnets/2/",
                    ),
                )
            ],
        )

    @staticmethod
    def get_nic_existing():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=None,
            effective_mtu=1500,
            ip_address="this-ip",
            cidr="this-cidr",
            vlan=dict(name="this-vlan", fabric="this-fabric"),
            links=[],
        )

    @staticmethod
    def get_new_alias_ansible():
        return dict(
            network_interface="this-interface", subnet="10.10.10.0/24", mode="AUTO"
        )

    def test_ensure_present_when_nic_not_found(self, create_module, client, mocker):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        new_alias_dict = self.get_new_alias_ansible()
        new_alias_obj = NetworkInterface.from_ansible(new_alias_dict)
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="AUTO",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_name"
        ).side_effect = [None]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = new_alias_obj
        with pytest.raises(
            errors.MaasError,
            match=f"Network interface with name - {module.params['network_interface']} - not found",
        ):
            network_interface_link.ensure_present(module, client, machine_obj)

    def test_ensure_present_when_create_new_alias_on_existing_nic(
        self, create_module, client, mocker
    ):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        updated_machine_dict = self.get_machine_updated()
        updated_machine_obj = Machine.from_maas(updated_machine_dict)
        new_alias_dict = self.get_new_alias_ansible()
        new_nic_alias_obj = NetworkInterface.from_ansible(new_alias_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        updated_nic_dict = self.get_updated_nic()
        updated_nic_obj = NetworkInterface.from_maas(updated_nic_dict)
        created_alias = self.get_alias()
        expected = (
            True,
            created_alias,
            {"before": None, "after": created_alias},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="AUTO",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_name"
        ).side_effect = [existing_nic_obj, updated_nic_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = new_nic_alias_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.find_linked_alias_by_cidr"
        ).side_effect = [None, created_alias]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.payload_for_link_subnet"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_link_subnet_request"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_fqdn"
        ).return_value = updated_machine_obj
        results = network_interface_link.ensure_present(module, client, machine_obj)
        assert results == expected

    def test_ensure_present_when_update_existing_alias_on_existing_nic(
        self, create_module, client, mocker
    ):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        updated_machine_dict = self.get_machine_updated()
        updated_machine_obj = Machine.from_maas(updated_machine_dict)
        new_alias_dict = self.get_new_alias_ansible()
        new_nic_alias_obj = NetworkInterface.from_ansible(new_alias_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        updated_nic_dict = self.get_updated_nic()
        updated_nic_obj = NetworkInterface.from_maas(updated_nic_dict)
        existing_alias_dict = self.get_alias()
        updated_alias_dict = self.get_updated_alias()
        expected = (
            True,
            updated_alias_dict,
            {"before": existing_alias_dict, "after": updated_alias_dict},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="STATIC",
                ip_address="10.10.10.3",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_name"
        ).side_effect = [existing_nic_obj, updated_nic_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = new_nic_alias_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.find_linked_alias_by_cidr"
        ).side_effect = [existing_alias_dict, updated_alias_dict]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.alias_needs_update"
        ).return_value = True
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_unlink_subnet_request"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.payload_for_link_subnet"
        ).return_value = {}
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_link_subnet_request"
        ).return_value = None
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.get_by_fqdn"
        ).return_value = updated_machine_obj
        results = network_interface_link.ensure_present(module, client, machine_obj)
        assert results == expected

    def test_ensure_present_when_no_changes_nic(self, create_module, client, mocker):
        machine_dict = self.get_machine_state_new()
        machine_obj = Machine.from_maas(machine_dict)
        new_alias_dict = self.get_new_alias_ansible()
        new_nic_alias_obj = NetworkInterface.from_ansible(new_alias_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        updated_nic_dict = self.get_updated_nic()
        updated_nic_obj = NetworkInterface.from_maas(updated_nic_dict)
        existing_alias_dict = self.get_alias()
        updated_alias_dict = self.get_updated_alias()
        expected = (
            False,
            None,
            {"before": None, "after": None},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="present",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="STATIC",
                ip_address="10.10.10.3",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_name"
        ).side_effect = [existing_nic_obj, updated_nic_obj]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.from_ansible"
        ).return_value = new_nic_alias_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.find_linked_alias_by_cidr"
        ).side_effect = [existing_alias_dict, updated_alias_dict]
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.alias_needs_update"
        ).return_value = False
        results = network_interface_link.ensure_present(module, client, machine_obj)
        assert results == expected


class TestEsnureAbsent:
    @staticmethod
    def get_machine_state_new():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=None,
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-power-type",
            architecture="this-architecture",
        )

    @staticmethod
    def get_machine_updated():
        return dict(
            fqdn="this-machine-fqdn",
            hostname="this-machine",
            cpu_count=2,
            memory=5000,
            system_id="123",
            interface_set=[
                dict(
                    name="this-nic",
                    id=123,
                    mac_address="this-mac",
                    system_id=123,
                    tags=None,
                    effective_mtu=2000,
                    ip_address="this-ip",
                    cidr="this-cidr",
                    vlan=dict(name="this-vlan", fabric="this-fabric"),
                    links=[],
                )
            ],
            blockdevice_set=None,
            domain=dict(id=1),
            zone=dict(id=1),
            pool=dict(id=1),
            tag_names=["my_tag"],
            status_name="New",
            osystem="ubuntu",
            distro_series="jammy",
            hwe_kernel="ga-22.04",
            min_hwe_kernel="ga-22.04",
            power_type="this-powertype",
            architecture="this-architecture",
        )

    @staticmethod
    def get_nic():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=["tag1", "tag2"],
            effective_mtu=1500,
            ip_address="this-ip",
            subnet_cidr="this-subnet",
            vlan=None,
            links=[],
        )

    @staticmethod
    def get_nic_existing():
        return dict(
            name="this-nic",
            id=123,
            mac_address="this-mac",
            system_id=123,
            tags=["tag1", "tag2"],
            effective_mtu=1500,
            ip_address="this-ip",
            subnet_cidr="this-subnet",
            vlan=None,
            links=[],
        )

    @staticmethod
    def get_alias():
        return dict(
            id=14,
            mode="auto",
            subnet=dict(
                name="subnet-1",
                vlan=dict(
                    vid=0,
                    mtu=1500,
                    dhcp_on=False,
                    external_dhcp=None,
                    relay_vlan=None,
                    name="vlan-1",
                    space="management",
                    secondary_rack="76y7pg",
                    primary_rack="7xtf67",
                    fabric="fabric-1",
                    fabric_id=1,
                    id=5003,
                    resource_uri="/MAAS/api/2.0/vlans/5003/",
                ),
                cidr="10.10.10.0/24",
                rdns_mode=2,
                gateway_ip="10.10.10.1",
                dns_servers=[
                    "fcb0:c682:8c15:817d:7d80:2713:e225:5624",
                    "fd66:86c9:6a50:27cd:de13:3f1c:40d1:8aac",
                    "120.129.237.29",
                ],
                allow_dns=True,
                allow_proxy=True,
                active_discovery=False,
                managed=True,
                space="management",
                id=2,
                resource_uri="/MAAS/api/2.0/subnets/2/",
            ),
        )

    def test_ensure_absent_when_delete_existing_alias_on_existing_nic(
        self, create_module, client, mocker
    ):
        machine_dict = self.get_machine_updated()
        machine_obj = Machine.from_maas(machine_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        existing_alias_dict = self.get_alias()
        expected = (
            True,
            None,
            {"before": existing_alias_dict, "after": None},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="STATIC",
                ip_address="10.10.10.3",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_name"
        ).return_value = existing_nic_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.find_linked_alias_by_cidr"
        ).return_value = existing_alias_dict
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.send_unlink_subnet_request"
        ).return_value = None
        results = network_interface_link.ensure_absent(module, client, machine_obj)
        assert results == expected

    def test_ensure_absent_when_alias_not_exist(self, create_module, client, mocker):
        machine_dict = self.get_machine_updated()
        machine_obj = Machine.from_maas(machine_dict)
        existing_nic_dict = self.get_nic_existing()
        existing_nic_obj = NetworkInterface.from_maas(existing_nic_dict)
        expected = (
            False,
            None,
            {"before": None, "after": None},
        )
        module = create_module(
            params=dict(
                instance=dict(
                    host="https://0.0.0.0",
                    customer_key="client key",
                    token_key="token key",
                    token_secret="token secret",
                ),
                state="absent",
                machine="this-machine-fqdn",
                network_interface="this-interface",
                subnet="10.10.10.0/24",
                mode="STATIC",
                ip_address="10.10.10.3",
            )
        )
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.machine.Machine.find_nic_by_name"
        ).return_value = existing_nic_obj
        mocker.patch(
            "ansible_collections.canonical.maas.plugins.module_utils.network_interface.NetworkInterface.find_linked_alias_by_cidr"
        ).return_value = None
        results = network_interface_link.ensure_absent(module, client, machine_obj)
        assert results == expected
