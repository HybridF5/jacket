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

from jacket.compute.compute import rpcapi as compute_rpcapi
from jacket.compute.conductor.tasks import migrate
from jacket.objects import compute
from jacket.objects.compute import base as obj_base
from jacket.compute.scheduler import client as scheduler_client
from jacket.compute.scheduler import utils as scheduler_utils
from jacket.compute import test
from jacket.tests.compute.unit.conductor.test_conductor import FakeContext
from jacket.tests.compute.unit import fake_flavor
from jacket.tests.compute.unit import fake_instance


class MigrationTaskTestCase(test.NoDBTestCase):
    def setUp(self):
        super(MigrationTaskTestCase, self).setUp()
        self.user_id = 'fake'
        self.project_id = 'fake'
        self.context = FakeContext(self.user_id, self.project_id)
        inst = fake_instance.fake_db_instance(image_ref='image_ref')
        self.instance = compute.Instance._from_db_object(
            self.context, compute.Instance(), inst, [])
        self.instance.system_metadata = {'image_hw_disk_bus': 'scsi'}
        self.flavor = fake_flavor.fake_flavor_obj(self.context)
        self.flavor.extra_specs = {'extra_specs': 'fake'}
        self.request_spec = {'instance_type':
                                 obj_base.obj_to_primitive(self.flavor),
                             'instance_properties': {},
                             'image': 'image'}
        self.hosts = [dict(host='host1', nodename=None, limits={})]
        self.filter_properties = {'limits': {}, 'retry': {'num_attempts': 1,
                                  'hosts': [['host1', None]]}}
        self.reservations = []
        self.clean_shutdown = True

    def _generate_task(self):
        return migrate.MigrationTask(self.context, self.instance, self.flavor,
                                     self.filter_properties, self.request_spec,
                                     self.reservations, self.clean_shutdown,
                                     compute_rpcapi.ComputeAPI(),
                                     scheduler_client.SchedulerClient())

    @mock.patch.object(scheduler_utils, 'build_request_spec')
    @mock.patch.object(scheduler_utils, 'setup_instance_group')
    @mock.patch.object(compute.RequestSpec, 'from_primitives')
    @mock.patch.object(scheduler_client.SchedulerClient, 'select_destinations')
    @mock.patch.object(compute_rpcapi.ComputeAPI, 'prep_resize')
    @mock.patch.object(compute.Quotas, 'from_reservations')
    def test_execute(self, quotas_mock, prep_resize_mock,
                     sel_dest_mock, spec_fp_mock, sig_mock, brs_mock):
        brs_mock.return_value = self.request_spec
        fake_spec = compute.RequestSpec()
        spec_fp_mock.return_value = fake_spec
        sel_dest_mock.return_value = self.hosts
        task = self._generate_task()

        task.execute()

        quotas_mock.assert_called_once_with(self.context, self.reservations,
                                            instance=self.instance)
        sig_mock.assert_called_once_with(self.context, self.request_spec,
                                         self.filter_properties)
        task.scheduler_client.select_destinations.assert_called_once_with(
            self.context, fake_spec)
        prep_resize_mock.assert_called_once_with(
            self.context, 'image', self.instance, self.flavor,
            self.hosts[0]['host'], self.reservations,
            request_spec=self.request_spec,
            filter_properties=self.filter_properties,
            node=self.hosts[0]['nodename'], clean_shutdown=self.clean_shutdown)
        self.assertFalse(quotas_mock.return_value.rollback.called)

    def test_rollback(self):
        task = self._generate_task()
        task.quotas = mock.MagicMock()
        task.rollback()
        task.quotas.rollback.assert_called_once_with()
