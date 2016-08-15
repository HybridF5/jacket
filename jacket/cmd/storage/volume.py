#!/usr/bin/env python
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Starter script for Cinder Volume."""

import logging as python_logging
import os

import eventlet

from jacket.objects import storage

if os.name == 'nt':
    # eventlet monkey patching the os module causes subprocess.Popen to fail
    # on Windows when using pipes due to missing non-blocking IO support.
    eventlet.monkey_patch(os=False)
else:
    eventlet.monkey_patch()

import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr
from oslo_reports import opts as gmr_opts

from jacket.storage import i18n
i18n.enable_lazy()

# Need to register global_opts
from jacket.common.storage import config  # noqa
from jacket.db.storage import api as session
from jacket.storage.i18n import _
from jacket.storage import service
from jacket.storage import utils
from jacket.storage import version


deprecated_host_opt = cfg.DeprecatedOpt('host')
host_opt = cfg.StrOpt('backend_host', help='Backend override of host value.',
                      deprecated_opts=[deprecated_host_opt])
cfg.CONF.register_cli_opt(host_opt)
CONF = cfg.CONF


def main():
    storage.register_all()
    gmr_opts.set_defaults(CONF)
    CONF(sys.argv[1:], project='storage',
         version=version.version_string())
    logging.setup(CONF, "storage")
    python_logging.captureWarnings(True)
    utils.monkey_patch()
    gmr.TextGuruMeditation.setup_autorun(version, conf=CONF)
    launcher = service.get_launcher()
    LOG = logging.getLogger(__name__)
    service_started = False

    if CONF.enabled_backends:
        for backend in CONF.enabled_backends:
            CONF.register_opt(host_opt, group=backend)
            backend_host = getattr(CONF, backend).backend_host
            host = "%s@%s" % (backend_host or CONF.host, backend)
            try:
                server = service.Service.create(host=host,
                                                service_name=backend,
                                                binary='storage-volume')
            except Exception:
                msg = _('Volume service %s failed to start.') % host
                LOG.exception(msg)
            else:
                # Dispose of the whole DB connection pool here before
                # starting another process.  Otherwise we run into cases where
                # child processes share DB connections which results in errors.
                session.dispose_engine()
                launcher.launch_service(server)
                service_started = True
    else:
        server = service.Service.create(binary='storage-volume')
        launcher.launch_service(server)
        service_started = True

    if not service_started:
        msg = _('No volume service(s) started successfully, terminating.')
        LOG.error(msg)
        sys.exit(1)

    launcher.wait()