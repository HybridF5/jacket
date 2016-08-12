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
from jacket.compute.scheduler.filters import availability_zone_filter
from jacket.compute import test
from jacket.tests.compute.unit.scheduler import fakes


@mock.patch('compute.scheduler.filters.utils.aggregate_metadata_get_by_host')
class TestAvailabilityZoneFilter(test.NoDBTestCase):

    def setUp(self):
        super(TestAvailabilityZoneFilter, self).setUp()
        self.filt_cls = availability_zone_filter.AvailabilityZoneFilter()

    @staticmethod
    def _make_zone_request(zone):
        return compute.RequestSpec(
            context=mock.sentinel.ctx,
            availability_zone=zone)

    def test_availability_zone_filter_same(self, agg_mock):
        agg_mock.return_value = {'availability_zone': 'compute'}
        request = self._make_zone_request('compute')
        host = fakes.FakeHostState('host1', 'node1', {})
        self.assertTrue(self.filt_cls.host_passes(host, request))

    def test_availability_zone_filter_same_comma(self, agg_mock):
        agg_mock.return_value = {'availability_zone': 'compute,nova2'}
        request = self._make_zone_request('compute')
        host = fakes.FakeHostState('host1', 'node1', {})
        self.assertTrue(self.filt_cls.host_passes(host, request))

    def test_availability_zone_filter_different(self, agg_mock):
        agg_mock.return_value = {'availability_zone': 'compute'}
        request = self._make_zone_request('bad')
        host = fakes.FakeHostState('host1', 'node1', {})
        self.assertFalse(self.filt_cls.host_passes(host, request))
