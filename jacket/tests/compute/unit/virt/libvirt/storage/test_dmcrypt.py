# Copyright (c) 2014 The Johns Hopkins University/Applied Physics Laboratory
# All Rights Reserved
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

from oslo_concurrency import processutils

from jacket.compute import test
from jacket.compute.virt.libvirt.storage import dmcrypt


class LibvirtDmcryptTestCase(test.NoDBTestCase):
    def setUp(self):
        super(LibvirtDmcryptTestCase, self).setUp()

        self.CIPHER = 'cipher'
        self.KEY_SIZE = 256
        self.NAME = 'disk'
        self.TARGET = dmcrypt.volume_name(self.NAME)
        self.PATH = '/dev/compute-lvm/instance_disk'
        self.KEY = range(0, self.KEY_SIZE)
        self.KEY_STR = ''.join(["%02x" % x for x in range(0, self.KEY_SIZE)])

    @mock.patch('compute.utils.execute')
    def test_create_volume(self, mock_execute):
        dmcrypt.create_volume(self.TARGET, self.PATH, self.CIPHER,
            self.KEY_SIZE, self.KEY)

        mock_execute.assert_has_calls([
            mock.call('cryptsetup', 'create', self.TARGET, self.PATH,
                      '--cipher=' + self.CIPHER,
                      '--key-size=' + str(self.KEY_SIZE),
                      '--key-file=-', process_input=self.KEY_STR,
                      run_as_root=True),
        ])

    @mock.patch('compute.virt.libvirt.storage.dmcrypt.LOG')
    @mock.patch('compute.utils.execute')
    def test_create_volume_fail(self, mock_execute, mock_log):
        mock_execute.side_effect = processutils.ProcessExecutionError()

        self.assertRaises(processutils.ProcessExecutionError,
                          dmcrypt.create_volume, self.TARGET, self.PATH,
                          self.CIPHER, self.KEY_SIZE, self.KEY)

        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_log.error.call_count)  # error logged

    @mock.patch('compute.utils.execute')
    def test_delete_volume(self, mock_execute):
        dmcrypt.delete_volume(self.TARGET)

        mock_execute.assert_has_calls([
            mock.call('cryptsetup', 'remove', self.TARGET, run_as_root=True),
        ])

    @mock.patch('compute.virt.libvirt.storage.dmcrypt.LOG')
    @mock.patch('compute.utils.execute')
    def test_delete_volume_fail(self, mock_execute, mock_log):
        mock_execute.side_effect = processutils.ProcessExecutionError()

        self.assertRaises(processutils.ProcessExecutionError,
                          dmcrypt.delete_volume, self.TARGET)

        self.assertEqual(1, mock_execute.call_count)
        self.assertEqual(1, mock_log.error.call_count)  # error logged

    @mock.patch('compute.virt.libvirt.storage.dmcrypt.LOG')
    @mock.patch('compute.utils.execute')
    def test_delete_missing_volume(self, mock_execute, mock_log):
        mock_execute.side_effect = \
                processutils.ProcessExecutionError(exit_code=4)

        dmcrypt.delete_volume(self.TARGET)

        self.assertEqual(1, mock_log.debug.call_count)
        self.assertEqual(0, mock_log.error.call_count)

    @mock.patch('os.listdir')
    def test_list_volumes(self, mock_listdir):
        mock_listdir.return_value = [self.TARGET, '/dev/mapper/disk']
        encrypted_volumes = dmcrypt.list_volumes()

        self.assertEqual(1, mock_listdir.call_count)
        self.assertEqual([self.TARGET], encrypted_volumes)
