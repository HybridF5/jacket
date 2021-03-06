# Copyright (c) 2015 Alex Meade
# Copyright (c) 2015 Yogesh Kshirsagar
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

import mock

from jacket.storage import test
from jacket.tests.storage.unit.volume.drivers.netapp.eseries import test_driver
import jacket.storage.volume.drivers.netapp.eseries.fc_driver as fc
from jacket.storage.volume.drivers.netapp import utils as na_utils


class NetAppESeriesFibreChannelDriverTestCase(test_driver
                                              .NetAppESeriesDriverTestCase,
                                              test.TestCase):

    PROTOCOL = 'fc'

    @mock.patch.object(na_utils, 'validate_instantiation')
    def test_instantiation(self, mock_validate_instantiation):
        fc.NetAppEseriesFibreChannelDriver(configuration=mock.Mock())

        self.assertTrue(mock_validate_instantiation.called)
