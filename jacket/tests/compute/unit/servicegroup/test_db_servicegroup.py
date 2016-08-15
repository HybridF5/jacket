# Copyright 2012 IBM Corp.
#
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
from oslo_db import exception as db_exception
import oslo_messaging as messaging
from oslo_utils import fixture as utils_fixture
from oslo_utils import timeutils

from jacket.objects import compute
from jacket.compute import servicegroup
from jacket.compute import test


class DBServiceGroupTestCase(test.NoDBTestCase):

    def setUp(self):
        super(DBServiceGroupTestCase, self).setUp()
        self.down_time = 15
        self.flags(service_down_time=self.down_time,
                   servicegroup_driver='db')
        self.servicegroup_api = servicegroup.API()

    def test_is_up(self):
        now = timeutils.utcnow()
        service = compute.Service(
            host='fake-host',
            topic='compute',
            binary='compute-compute',
            created_at=now,
            updated_at=now,
            last_seen_up=now,
            forced_down=False,
        )
        time_fixture = self.useFixture(utils_fixture.TimeFixture(now))

        # Up (equal)
        result = self.servicegroup_api.service_is_up(service)
        self.assertTrue(result)

        # Up
        time_fixture.advance_time_seconds(self.down_time)
        result = self.servicegroup_api.service_is_up(service)
        self.assertTrue(result)

        # Down
        time_fixture.advance_time_seconds(1)
        result = self.servicegroup_api.service_is_up(service)
        self.assertFalse(result)

        # "last_seen_up" says down, "updated_at" says up.
        # This can happen if we do a service disable/enable while it's down.
        service.updated_at = timeutils.utcnow()
        result = self.servicegroup_api.service_is_up(service)
        self.assertFalse(result)

    def test_join(self):
        service = mock.MagicMock(report_interval=1)

        self.servicegroup_api.join('fake-host', 'fake-topic', service)
        fn = self.servicegroup_api._driver._report_state
        service.tg.add_timer.assert_called_once_with(1, fn, 5, service)

    @mock.patch.object(compute.Service, 'save')
    def test_report_state(self, upd_mock):
        service_ref = compute.Service(host='fake-host', topic='compute',
                                      report_count=10)
        service = mock.MagicMock(model_disconnected=False,
                                 service_ref=service_ref)
        fn = self.servicegroup_api._driver._report_state
        fn(service)
        upd_mock.assert_called_once_with()
        self.assertEqual(11, service_ref.report_count)
        self.assertFalse(service.model_disconnected)

    @mock.patch.object(compute.Service, 'save')
    def _test_report_state_error(self, exc_cls, upd_mock):
        upd_mock.side_effect = exc_cls("service save failed")
        service_ref = compute.Service(host='fake-host', topic='compute',
                                      report_count=10)
        service = mock.MagicMock(model_disconnected=False,
                                 service_ref=service_ref)
        fn = self.servicegroup_api._driver._report_state
        fn(service)  # fail if exception not caught
        self.assertTrue(service.model_disconnected)

    def test_report_state_remote_error_handling(self):
        # test error handling using remote conductor
        self.flags(use_local=False, group='conductor')
        self._test_report_state_error(messaging.RemoteError)

    def test_report_state_remote_error_handling_timeout(self):
        # test error handling using remote conductor
        self.flags(use_local=False, group='conductor')
        self._test_report_state_error(messaging.MessagingTimeout)

    def test_report_state_remote_unexpected_error(self):
        # unexpected errors must be handled, but disconnected flag not touched
        self.flags(use_local=False, group='conductor')
        self._test_report_state_error(RuntimeError)

    def test_report_state_local_error_handling(self):
        # if using local conductor, the db driver must handle DB errors
        self.flags(use_local=True, group='conductor')

        # mock an oslo.db DBError as it's an exception base class for
        # oslo.db DB errors (eg DBConnectionError)
        self._test_report_state_error(db_exception.DBError)

    def test_report_state_local_unexpected_error(self):
        # unexpected errors must be handled, but disconnected flag not touched
        self.flags(use_local=True, group='conductor')
        self._test_report_state_error(RuntimeError)