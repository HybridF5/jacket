# Copyright 2012 OpenStack Foundation
# Copyright 2013 IBM Corp.
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

import base64
import datetime
import mock
import uuid

from oslo_config import cfg
from oslo_serialization import jsonutils

from jacket.api.compute.openstack.compute import extension_info
from jacket.api.compute.openstack.compute import servers
from jacket.api.compute.openstack.compute import user_data
from jacket.compute.cloud import api as compute_api
from jacket.compute.cloud import flavors
from jacket.compute import exception
from jacket.compute.network import manager
from jacket.compute import test
from jacket.tests.compute.unit.api.openstack import fakes
from jacket.tests.compute.unit import fake_instance
from jacket.tests.compute.unit.image import fake


CONF = cfg.CONF
FAKE_UUID = fakes.FAKE_UUID


def fake_gen_uuid():
    return FAKE_UUID


def return_security_group(context, instance_id, security_group_id):
    pass


class ServersControllerCreateTest(test.TestCase):

    def setUp(self):
        """Shared implementation for tests below that create instance."""
        super(ServersControllerCreateTest, self).setUp()

        self.flags(verbose=True,
                   enable_instance_password=True)
        self.instance_cache_num = 0
        self.instance_cache_by_id = {}
        self.instance_cache_by_uuid = {}

        ext_info = extension_info.LoadedExtensionInfo()
        self.controller = servers.ServersController(extension_info=ext_info)
        CONF.set_override('extensions_blacklist', 'os-user-data',
                          'osapi_v21')
        self.no_user_data_controller = servers.ServersController(
            extension_info=ext_info)

        def instance_create(context, inst):
            inst_type = flavors.get_flavor_by_flavor_id(3)
            image_uuid = '76fa36fc-c930-4bf3-8c8a-ea2a2420deb6'
            def_image_ref = 'http://localhost/images/%s' % image_uuid
            self.instance_cache_num += 1
            instance = fake_instance.fake_db_instance(**{
                'id': self.instance_cache_num,
                'display_name': inst['display_name'] or 'test',
                'uuid': FAKE_UUID,
                'instance_type': inst_type,
                'access_ip_v4': '1.2.3.4',
                'access_ip_v6': 'fead::1234',
                'image_ref': inst.get('image_ref', def_image_ref),
                'user_id': 'fake',
                'project_id': 'fake',
                'reservation_id': inst['reservation_id'],
                "created_at": datetime.datetime(2010, 10, 10, 12, 0, 0),
                "updated_at": datetime.datetime(2010, 11, 11, 11, 0, 0),
                user_data.ATTRIBUTE_NAME: None,
                "progress": 0,
                "fixed_ips": [],
                "task_state": "",
                "vm_state": "",
                "root_device_name": inst.get('root_device_name', 'vda'),
            })

            self.instance_cache_by_id[instance['id']] = instance
            self.instance_cache_by_uuid[instance['uuid']] = instance
            return instance

        def instance_get(context, instance_id):
            """Stub for compute/api create() pulling in instance after
            scheduling
            """
            return self.instance_cache_by_id[instance_id]

        def instance_update(context, uuid, values):
            instance = self.instance_cache_by_uuid[uuid]
            instance.update(values)
            return instance

        def server_update(context, instance_uuid, params):
            inst = self.instance_cache_by_uuid[instance_uuid]
            inst.update(params)
            return (inst, inst)

        def fake_method(*args, **kwargs):
            pass

        def project_get_networks(context, user_id):
            return dict(id='1', host='localhost')

        fakes.stub_out_rate_limiting(self.stubs)
        fakes.stub_out_key_pair_funcs(self.stubs)
        fake.stub_out_image_service(self)
        fakes.stub_out_nw_api(self)
        self.stubs.Set(uuid, 'uuid4', fake_gen_uuid)
        self.stub_out('compute.db.instance_add_security_group',
                      return_security_group)
        self.stub_out('compute.db.project_get_networks', project_get_networks)
        self.stub_out('compute.db.instance_create', instance_create)
        self.stub_out('compute.db.instance_system_metadata_update', fake_method)
        self.stub_out('compute.db.instance_get', instance_get)
        self.stub_out('compute.db.instance_update', instance_update)
        self.stub_out('compute.db.instance_update_and_get_original',
                      server_update)
        self.stubs.Set(manager.VlanManager, 'allocate_fixed_ip',
                       fake_method)

    def _test_create_extra(self, params, no_image=False,
                           override_controller=None, legacy_v2=False):
        image_uuid = 'c905cedb-7281-47e4-8a62-f26bc5fc4c77'
        server = dict(name='server_test', imageRef=image_uuid, flavorRef=2)
        if no_image:
            server.pop('imageRef', None)
        server.update(params)
        body = dict(server=server)
        req = fakes.HTTPRequestV21.blank('/servers')
        req.method = 'POST'
        req.body = jsonutils.dump_as_bytes(body)
        req.headers["content-type"] = "application/json"
        if legacy_v2:
            req.set_legacy_v2()
        if override_controller:
            server = override_controller.create(req, body=body).obj['server']
        else:
            server = self.controller.create(req, body=body).obj['server']
        return server

    def test_create_instance_with_user_data_disabled(self):
        params = {user_data.ATTRIBUTE_NAME: base64.b64encode('fake')}
        old_create = compute_api.API.create

        def create(*args, **kwargs):
            self.assertNotIn('user_data', kwargs)
            return old_create(*args, **kwargs)

        self.stubs.Set(compute_api.API, 'create', create)
        self._test_create_extra(
            params,
            override_controller=self.no_user_data_controller)

    def test_create_instance_with_user_data_enabled(self):
        params = {user_data.ATTRIBUTE_NAME: base64.b64encode('fake')}
        old_create = compute_api.API.create

        def create(*args, **kwargs):
            self.assertIn('user_data', kwargs)
            return old_create(*args, **kwargs)

        self.stubs.Set(compute_api.API, 'create', create)
        self._test_create_extra(params)

    def test_create_instance_with_user_data(self):
        value = base64.b64encode("A random string")
        params = {user_data.ATTRIBUTE_NAME: value}
        server = self._test_create_extra(params)
        self.assertEqual(FAKE_UUID, server['id'])

    def test_create_instance_with_bad_user_data(self):
        value = "A random string"
        params = {user_data.ATTRIBUTE_NAME: value}
        self.assertRaises(exception.ValidationError,
                          self._test_create_extra, params)

    @mock.patch('compute.compute.api.API.create')
    def test_create_instance_with_none_allowd_for_v20_compat_mode(self,
            mock_create):

        def create(context, *args, **kwargs):
            self.assertIsNone(kwargs['user_data'])
            return ([fakes.stub_instance_obj(context)], None)

        mock_create.side_effect = create
        params = {user_data.ATTRIBUTE_NAME: None}
        self._test_create_extra(params, legacy_v2=True)
