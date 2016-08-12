#    Copyright 2014 Objectif Libre
#    Copyright 2015 DotHill Systems
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
#

from jacket.storage.volume.drivers.dothill import dothill_fc
from jacket.storage.volume.drivers.lenovo import lenovo_common


class LenovoFCDriver(dothill_fc.DotHillFCDriver):
    """OpenStack Fibre Channel storage drivers for Lenovo Storage arrays.

    Version history:
        1.0    - Inheriting from DotHill storage drivers.

    """

    VERSION = "1.0"

    def __init__(self, *args, **kwargs):
        super(LenovoFCDriver, self).__init__(*args, **kwargs)
        self.configuration.append_config_values(lenovo_common.common_opts)

    def _init_common(self):
        return lenovo_common.LenovoCommon(self.configuration)
