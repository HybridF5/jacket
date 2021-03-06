# Copyright 2012 IBM Corp.
# All Rights Reserved.
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


import datetime

from iso8601 import iso8601
from oslo_utils import timeutils
import webob.exc

from jacket.api.storage.storage.contrib import services
from jacket.api.storage.storage import extensions
from jacket import context
from jacket import db
from jacket.storage import exception
from jacket.storage import policy
from jacket.storage import test
from jacket.tests.storage.unit.api import fakes


fake_services_list = [
    {'binary': 'storage-scheduler',
     'host': 'host1',
     'availability_zone': 'storage',
     'id': 1,
     'disabled': True,
     'updated_at': datetime.datetime(2012, 10, 29, 13, 42, 2),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 27),
     'disabled_reason': 'test1',
     'modified_at': ''},
    {'binary': 'storage-volume',
     'host': 'host1',
     'availability_zone': 'storage',
     'id': 2,
     'disabled': True,
     'updated_at': datetime.datetime(2012, 10, 29, 13, 42, 5),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 27),
     'disabled_reason': 'test2',
     'modified_at': ''},
    {'binary': 'storage-scheduler',
     'host': 'host2',
     'availability_zone': 'storage',
     'id': 3,
     'disabled': False,
     'updated_at': datetime.datetime(2012, 9, 19, 6, 55, 34),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 28),
     'disabled_reason': '',
     'modified_at': ''},
    {'binary': 'storage-volume',
     'host': 'host2',
     'availability_zone': 'storage',
     'id': 4,
     'disabled': True,
     'updated_at': datetime.datetime(2012, 9, 18, 8, 3, 38),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 28),
     'disabled_reason': 'test4',
     'modified_at': ''},
    {'binary': 'storage-volume',
     'host': 'host2',
     'availability_zone': 'storage',
     'id': 5,
     'disabled': True,
     'updated_at': datetime.datetime(2012, 9, 18, 8, 3, 38),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 28),
     'disabled_reason': 'test5',
     'modified_at': datetime.datetime(2012, 10, 29, 13, 42, 5)},
    {'binary': 'storage-volume',
     'host': 'host2',
     'availability_zone': 'storage',
     'id': 6,
     'disabled': False,
     'updated_at': datetime.datetime(2012, 9, 18, 8, 3, 38),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 28),
     'disabled_reason': '',
     'modified_at': datetime.datetime(2012, 9, 18, 8, 1, 38)},
    {'binary': 'storage-scheduler',
     'host': 'host2',
     'availability_zone': 'storage',
     'id': 6,
     'disabled': False,
     'updated_at': None,
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 28),
     'disabled_reason': '',
     'modified_at': None},
]


class FakeRequest(object):
    environ = {"storage.context": context.get_admin_context()}
    GET = {}


# NOTE(uni): deprecating service request key, binary takes precedence
# Still keeping service key here for API compatibility sake.
class FakeRequestWithService(object):
    environ = {"storage.context": context.get_admin_context()}
    GET = {"service": "storage-volume"}


class FakeRequestWithBinary(object):
    environ = {"storage.context": context.get_admin_context()}
    GET = {"binary": "storage-volume"}


class FakeRequestWithHost(object):
    environ = {"storage.context": context.get_admin_context()}
    GET = {"host": "host1"}


# NOTE(uni): deprecating service request key, binary takes precedence
# Still keeping service key here for API compatibility sake.
class FakeRequestWithHostService(object):
    environ = {"storage.context": context.get_admin_context()}
    GET = {"host": "host1", "service": "storage-volume"}


class FakeRequestWithHostBinary(object):
    environ = {"storage.context": context.get_admin_context()}
    GET = {"host": "host1", "binary": "storage-volume"}


def fake_service_get_all(context, filters=None):
    filters = filters or {}
    host = filters.get('host')
    binary = filters.get('binary')
    return [s for s in fake_services_list
            if (not host or s['host'] == host or
                s['host'].startswith(host + '@'))
            and (not binary or s['binary'] == binary)]


def fake_service_get_by_host_binary(context, host, binary):
    for service in fake_services_list:
        if service['host'] == host and service['binary'] == binary:
            return service
    return None


def fake_service_get_by_id(value):
    for service in fake_services_list:
        if service['id'] == value:
            return service
    return None


def fake_service_update(context, service_id, values):
    service = fake_service_get_by_id(service_id)
    if service is None:
        raise exception.ServiceNotFound(service_id=service_id)
    else:
        {'host': 'host1', 'service': 'storage-volume',
         'disabled': values['disabled']}


def fake_policy_enforce(context, action, target):
    pass


def fake_utcnow(with_timezone=False):
    tzinfo = iso8601.Utc() if with_timezone else None
    return datetime.datetime(2012, 10, 29, 13, 42, 11, tzinfo=tzinfo)


class ServicesTest(test.TestCase):

    def setUp(self):
        super(ServicesTest, self).setUp()

        self.stubs.Set(storage, "service_get_all", fake_service_get_all)
        self.stubs.Set(timeutils, "utcnow", fake_utcnow)
        self.stubs.Set(storage, "service_get_by_args",
                       fake_service_get_by_host_binary)
        self.stubs.Set(storage, "service_update", fake_service_update)
        self.stubs.Set(policy, "enforce", fake_policy_enforce)

        self.context = context.get_admin_context()
        self.ext_mgr = extensions.ExtensionManager()
        self.ext_mgr.extensions = {}
        self.controller = services.ServiceController(self.ext_mgr)

    def test_services_list(self):
        req = FakeRequest()
        res_dict = self.controller.index(req)

        response = {'services': [{'binary': 'storage-scheduler',
                                  'host': 'host1', 'zone': 'storage',
                                  'status': 'disabled', 'state': 'up',
                                  'updated_at': datetime.datetime(
                                      2012, 10, 29, 13, 42, 2)},
                                 {'binary': 'storage-volume',
                                  'host': 'host1', 'zone': 'storage',
                                  'status': 'disabled', 'state': 'up',
                                  'updated_at': datetime.datetime(
                                      2012, 10, 29, 13, 42, 5)},
                                 {'binary': 'storage-scheduler',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'enabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 9, 19, 6, 55, 34)},
                                 {'binary': 'storage-volume',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'disabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 9, 18, 8, 3, 38)},
                                 {'binary': 'storage-volume',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'disabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 10, 29, 13, 42, 5)},
                                 {'binary': 'storage-volume',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'enabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 9, 18, 8, 3, 38)},
                                 {'binary': 'storage-scheduler',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'enabled', 'state': 'down',
                                  'updated_at': None},
                                 ]}
        self.assertEqual(response, res_dict)

    def test_services_detail(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = FakeRequest()
        res_dict = self.controller.index(req)

        response = {'services': [{'binary': 'storage-scheduler',
                                  'host': 'host1', 'zone': 'storage',
                                  'status': 'disabled', 'state': 'up',
                                  'updated_at': datetime.datetime(
                                      2012, 10, 29, 13, 42, 2),
                                  'disabled_reason': 'test1'},
                                 {'binary': 'storage-volume',
                                  'replication_status': None,
                                  'active_backend_id': None,
                                  'frozen': False,
                                  'host': 'host1', 'zone': 'storage',
                                  'status': 'disabled', 'state': 'up',
                                  'updated_at': datetime.datetime(
                                      2012, 10, 29, 13, 42, 5),
                                  'disabled_reason': 'test2'},
                                 {'binary': 'storage-scheduler',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'enabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 9, 19, 6, 55, 34),
                                  'disabled_reason': ''},
                                 {'binary': 'storage-volume',
                                  'replication_status': None,
                                  'active_backend_id': None,
                                  'frozen': False,
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'disabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 9, 18, 8, 3, 38),
                                  'disabled_reason': 'test4'},
                                 {'binary': 'storage-volume',
                                  'replication_status': None,
                                  'active_backend_id': None,
                                  'frozen': False,
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'disabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 10, 29, 13, 42, 5),
                                  'disabled_reason': 'test5'},
                                 {'binary': 'storage-volume',
                                  'replication_status': None,
                                  'active_backend_id': None,
                                  'frozen': False,
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'enabled', 'state': 'down',
                                  'updated_at': datetime.datetime(
                                      2012, 9, 18, 8, 3, 38),
                                  'disabled_reason': ''},
                                 {'binary': 'storage-scheduler',
                                  'host': 'host2',
                                  'zone': 'storage',
                                  'status': 'enabled', 'state': 'down',
                                  'updated_at': None,
                                  'disabled_reason': ''},
                                 ]}
        self.assertEqual(response, res_dict)

    def test_services_list_with_host(self):
        req = FakeRequestWithHost()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-scheduler',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled', 'state': 'up',
             'updated_at': datetime.datetime(2012, 10,
                                             29, 13, 42, 2)},
            {'binary': 'storage-volume',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled', 'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)}]}
        self.assertEqual(response, res_dict)

    def test_services_detail_with_host(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = FakeRequestWithHost()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-scheduler',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled', 'state': 'up',
             'updated_at': datetime.datetime(2012, 10,
                                             29, 13, 42, 2),
             'disabled_reason': 'test1'},
            {'binary': 'storage-volume',
             'frozen': False,
             'replication_status': None,
             'active_backend_id': None,
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled', 'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test2'}]}
        self.assertEqual(response, res_dict)

    def test_services_list_with_service(self):
        req = FakeRequestWithService()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)},
            {'binary': 'storage-volume',
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38)},
            {'binary': 'storage-volume',
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)},
            {'binary': 'storage-volume',
             'host': 'host2',
             'zone': 'storage',
             'status': 'enabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38)}]}
        self.assertEqual(response, res_dict)

    def test_services_detail_with_service(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = FakeRequestWithService()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'frozen': False,
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test2'},
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'frozen': False,
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38),
             'disabled_reason': 'test4'},
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'frozen': False,
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test5'},
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'frozen': False,
             'host': 'host2',
             'zone': 'storage',
             'status': 'enabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38),
             'disabled_reason': ''}]}
        self.assertEqual(response, res_dict)

    def test_services_list_with_binary(self):
        req = FakeRequestWithBinary()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)},
            {'binary': 'storage-volume',
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38)},
            {'binary': 'storage-volume',
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)},
            {'binary': 'storage-volume',
             'host': 'host2',
             'zone': 'storage',
             'status': 'enabled',
             'state': 'down',
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38)}]}
        self.assertEqual(response, res_dict)

    def test_services_detail_with_binary(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = FakeRequestWithBinary()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'frozen': False,
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test2'},
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'frozen': False,
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38),
             'disabled_reason': 'test4'},
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'host': 'host2',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'down',
             'frozen': False,
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test5'},
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'host': 'host2',
             'zone': 'storage',
             'status': 'enabled',
             'state': 'down',
             'frozen': False,
             'updated_at': datetime.datetime(2012, 9, 18,
                                             8, 3, 38),
             'disabled_reason': ''}]}
        self.assertEqual(response, res_dict)

    def test_services_list_with_host_service(self):
        req = FakeRequestWithHostService()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)}]}
        self.assertEqual(response, res_dict)

    def test_services_detail_with_host_service(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = FakeRequestWithHostService()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test2',
             'frozen': False}]}
        self.assertEqual(response, res_dict)

    def test_services_list_with_host_binary(self):
        req = FakeRequestWithHostBinary()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5)}]}
        self.assertEqual(response, res_dict)

    def test_services_detail_with_host_binary(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = FakeRequestWithHostBinary()
        res_dict = self.controller.index(req)

        response = {'services': [
            {'binary': 'storage-volume',
             'replication_status': None,
             'active_backend_id': None,
             'frozen': False,
             'host': 'host1',
             'zone': 'storage',
             'status': 'disabled',
             'state': 'up',
             'updated_at': datetime.datetime(2012, 10, 29,
                                             13, 42, 5),
             'disabled_reason': 'test2'}]}
        self.assertEqual(response, res_dict)

    def test_services_enable_with_service_key(self):
        body = {'host': 'host1', 'service': 'storage-volume'}
        req = fakes.HTTPRequest.blank('/v2/fake/os-services/enable')
        res_dict = self.controller.update(req, "enable", body)

        self.assertEqual('enabled', res_dict['status'])

    def test_services_enable_with_binary_key(self):
        body = {'host': 'host1', 'binary': 'storage-volume'}
        req = fakes.HTTPRequest.blank('/v2/fake/os-services/enable')
        res_dict = self.controller.update(req, "enable", body)

        self.assertEqual('enabled', res_dict['status'])

    def test_services_disable_with_service_key(self):
        req = fakes.HTTPRequest.blank('/v2/fake/os-services/disable')
        body = {'host': 'host1', 'service': 'storage-volume'}
        res_dict = self.controller.update(req, "disable", body)

        self.assertEqual('disabled', res_dict['status'])

    def test_services_disable_with_binary_key(self):
        req = fakes.HTTPRequest.blank('/v2/fake/os-services/disable')
        body = {'host': 'host1', 'binary': 'storage-volume'}
        res_dict = self.controller.update(req, "disable", body)

        self.assertEqual('disabled', res_dict['status'])

    def test_services_disable_log_reason(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = (
            fakes.HTTPRequest.blank('v1/fake/os-services/disable-log-reason'))
        body = {'host': 'host1',
                'binary': 'storage-scheduler',
                'disabled_reason': 'test-reason',
                }
        res_dict = self.controller.update(req, "disable-log-reason", body)

        self.assertEqual('disabled', res_dict['status'])
        self.assertEqual('test-reason', res_dict['disabled_reason'])

    def test_services_disable_log_reason_none(self):
        self.ext_mgr.extensions['os-extended-services'] = True
        self.controller = services.ServiceController(self.ext_mgr)
        req = (
            fakes.HTTPRequest.blank('v1/fake/os-services/disable-log-reason'))
        body = {'host': 'host1',
                'binary': 'storage-scheduler',
                'disabled_reason': None,
                }
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self.controller.update,
                          req, "disable-log-reason", body)

    def test_invalid_reason_field(self):
        reason = ' '
        self.assertFalse(self.controller._is_valid_as_reason(reason))
        reason = 'a' * 256
        self.assertFalse(self.controller._is_valid_as_reason(reason))
        reason = 'it\'s a valid reason.'
        self.assertTrue(self.controller._is_valid_as_reason(reason))
        reason = None
        self.assertFalse(self.controller._is_valid_as_reason(reason))
