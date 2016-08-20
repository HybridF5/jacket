# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Starter script for Nova Metadata API."""

import sys

from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr

from jacket.compute.conductor import rpcapi as conductor_rpcapi
import jacket.compute.conf
from jacket.compute import config
from jacket.objects import compute
from jacket.objects.compute import base as objects_base
from jacket.compute import service
from jacket.compute import utils
from jacket import version


CONF = jacket.compute.conf.CONF
CONF.import_opt('enabled_ssl_apis', 'jacket.compute.service')


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, "compute")
    utils.monkey_patch()
    compute.register_all()

    gmr.TextGuruMeditation.setup_autorun(version)

    if not CONF.conductor.use_local:
        objects_base.NovaObject.indirection_api = \
            conductor_rpcapi.ConductorAPI()

    should_use_ssl = 'metadata' in CONF.enabled_ssl_apis
    server = service.WSGIService('metadata', use_ssl=should_use_ssl)
    service.serve(server, workers=server.workers)
    service.wait()
