#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from jacket.objects import compute
from jacket.compute.pci import stats
from jacket.compute.scheduler.filters import pci_passthrough_filter
from jacket.compute import test
from jacket.tests.compute.unit.scheduler import fakes


class TestPCIPassthroughFilter(test.NoDBTestCase):

    def setUp(self):
        super(TestPCIPassthroughFilter, self).setUp()
        self.filt_cls = pci_passthrough_filter.PciPassthroughFilter()

    def test_pci_passthrough_pass(self):
        pci_stats_mock = mock.MagicMock()
        pci_stats_mock.support_requests.return_value = True
        request = compute.InstancePCIRequest(count=1,
            spec=[{'vendor_id': '8086'}])
        requests = compute.InstancePCIRequests(requests=[request])
        spec_obj = compute.RequestSpec(pci_requests=requests)
        host = fakes.FakeHostState(
            'host1', 'node1',
            attribute_dict={'pci_stats': pci_stats_mock})
        self.assertTrue(self.filt_cls.host_passes(host, spec_obj))
        pci_stats_mock.support_requests.assert_called_once_with(
            requests.requests)

    def test_pci_passthrough_fail(self):
        pci_stats_mock = mock.MagicMock()
        pci_stats_mock.support_requests.return_value = False
        request = compute.InstancePCIRequest(count=1,
            spec=[{'vendor_id': '8086'}])
        requests = compute.InstancePCIRequests(requests=[request])
        spec_obj = compute.RequestSpec(pci_requests=requests)
        host = fakes.FakeHostState(
            'host1', 'node1',
            attribute_dict={'pci_stats': pci_stats_mock})
        self.assertFalse(self.filt_cls.host_passes(host, spec_obj))
        pci_stats_mock.support_requests.assert_called_once_with(
            requests.requests)

    def test_pci_passthrough_no_pci_request(self):
        spec_obj = compute.RequestSpec(pci_requests=None)
        host = fakes.FakeHostState('h1', 'n1', {})
        self.assertTrue(self.filt_cls.host_passes(host, spec_obj))

    def test_pci_passthrough_compute_stats(self):
        request = compute.InstancePCIRequest(count=1,
                                             spec=[{'vendor_id': '8086'}])
        requests = compute.InstancePCIRequests(requests=[request])
        spec_obj = compute.RequestSpec(pci_requests=requests)
        host = fakes.FakeHostState(
            'host1', 'node1',
            attribute_dict={})
        self.assertRaises(AttributeError, self.filt_cls.host_passes,
                          host, spec_obj)

    def test_pci_passthrough_no_pci_stats(self):
        request = compute.InstancePCIRequest(count=1,
            spec=[{'vendor_id': '8086'}])
        requests = compute.InstancePCIRequests(requests=[request])
        spec_obj = compute.RequestSpec(pci_requests=requests)
        host = fakes.FakeHostState('host1', 'node1',
            attribute_dict={'pci_stats': stats.PciDeviceStats()})
        self.assertFalse(self.filt_cls.host_passes(host, spec_obj))
