# Copyright 2016 HPE, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import jacket.compute.network
import jacket.compute.network.security_group.neutron_driver
import jacket.compute.network.security_group.openstack_driver as sgapi
import jacket.compute.test


class FileATicket(object):
    def __init__(self, **kwargs):
        pass


class NetworkAPIConfigTest(jacket.compute.test.NoDBTestCase):
    """Test the transition from legacy to use_neutron config options."""

    def test_default(self):
        netapi = jacket.compute.network.API()
        self.assertIsInstance(netapi, jacket.compute.network.api.API)

    def test_use_neutron(self):
        self.flags(use_neutron=True)
        netapi = jacket.compute.network.API()
        self.assertIsInstance(netapi, jacket.compute.network.neutronv2.api.API)

    def test_dont_use_neutron(self):
        self.flags(use_neutron=False)
        netapi = jacket.compute.network.API()
        self.assertIsInstance(netapi, jacket.compute.network.api.API)

    def test_legacy_use_neutron(self):
        """use neutron even if config is false because of legacy option."""
        self.flags(use_neutron=False)
        self.flags(network_api_class='jacket.compute.neutronv2.api.API')
        netapi = jacket.compute.network.API()
        self.assertIsInstance(netapi, jacket.compute.network.neutronv2.api.API)

    def test_legacy_custom_class(self):
        """use neutron even if config is false because of legacy option."""
        self.flags(network_api_class=
                   'compute.tests.unit.network.test_config.FileATicket')
        netapi = jacket.compute.network.API()
        self.assertIsInstance(netapi, FileATicket)


class SecurityGroupAPIConfigTest(jacket.compute.test.NoDBTestCase):

    def test_use_neutron(self):
        self.flags(use_neutron=True)
        driver = sgapi.get_openstack_security_group_driver()
        self.assertIsInstance(
            driver,
            jacket.compute.network.security_group.neutron_driver.SecurityGroupAPI)

    def test_sg_nova(self):
        self.flags(security_group_api='compute')
        driver = sgapi.get_openstack_security_group_driver()
        self.assertIsInstance(
            driver,
            jacket.compute.compute.api.SecurityGroupAPI)

    def test_sg_neutron(self):
        self.flags(security_group_api='neutron')
        driver = sgapi.get_openstack_security_group_driver()
        self.assertIsInstance(
            driver,
            jacket.compute.network.security_group.neutron_driver.SecurityGroupAPI)

    def test_sg_custom(self):
        self.flags(security_group_api=
                   'compute.tests.unit.network.test_config.FileATicket')
        driver = sgapi.get_openstack_security_group_driver()
        self.assertIsInstance(driver, FileATicket)
