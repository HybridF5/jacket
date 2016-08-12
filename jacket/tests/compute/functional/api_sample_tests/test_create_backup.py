# Copyright 2012 Nebula, Inc.
# Copyright 2013 IBM Corp.
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

from oslo_config import cfg

import mock

from jacket.tests.compute.functional.api_sample_tests import test_servers
from jacket.tests.compute.unit.image import fake

CONF = cfg.CONF
CONF.import_opt('osapi_compute_extension',
                'compute.api.openstack.compute.legacy_v2.extensions')


class CreateBackupSamplesJsonTest(test_servers.ServersSampleBase):
    extension_name = "os-create-backup"

    def _get_flags(self):
        f = super(CreateBackupSamplesJsonTest, self)._get_flags()
        f['osapi_compute_extension'] = CONF.osapi_compute_extension[:]
        f['osapi_compute_extension'].append(
            'compute.api.openstack.compute.contrib.admin_actions.Admin_actions')
        return f

    def setUp(self):
        """setUp Method for PauseServer api samples extension

        This method creates the server that will be used in each tests
        """
        super(CreateBackupSamplesJsonTest, self).setUp()
        self.uuid = self._post_server()

    @mock.patch.object(fake._FakeImageService, 'detail', return_value=[])
    def test_post_backup_server(self, mock_method):
        # Get api samples to backup server request.
        response = self._do_post('servers/%s/action' % self.uuid,
                                 'create-backup-req', {})
        self.assertEqual(202, response.status_code)
