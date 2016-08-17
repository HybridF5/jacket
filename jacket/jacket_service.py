# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Justin Santa Barbara
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

"""Generic Node base class for all workers that run on hosts."""


import os

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_service import service
from oslo_service import wsgi
from oslo_utils import importutils

osprofiler_notifier = importutils.try_import('osprofiler.notifier')
profiler = importutils.try_import('osprofiler.profiler')
osprofiler_web = importutils.try_import('osprofiler.web')
profiler_opts = importutils.try_import('osprofiler.opts')


from jacket import context
from jacket import exception
from jacket.i18n import _, _LW
from jacket import base_rpc
from jacket.wsgi import common as wsgi_common


LOG = logging.getLogger(__name__)

service_opts = [
    cfg.IntOpt('report_interval',
               default=10,
               help='Interval, in seconds, between nodes reporting state '
                    'to datastore'),
    cfg.IntOpt('periodic_interval',
               default=60,
               help='Interval, in seconds, between running periodic tasks'),
    cfg.IntOpt('periodic_fuzzy_delay',
               default=60,
               help='Range, in seconds, to randomly delay when starting the'
                    ' periodic task scheduler to reduce stampeding.'
                    ' (Disable by setting to 0)'),
    cfg.StrOpt('osapi_jacket_listen',
               default="0.0.0.0",
               help='IP address on which OpenStack jacket API listens'),
    cfg.PortOpt('osapi_jacket_listen_port',
                default=9776,
                help='Port on which OpenStack jacket API listens'),
    cfg.IntOpt('osapi_jacket_workers',
               help='Number of workers for OpenStack Jacket API service. '
                    'The default is equal to the number of CPUs available.'), ]


CONF = cfg.CONF
CONF.register_opts(service_opts)
if profiler_opts:
    profiler_opts.set_defaults(CONF)


def setup_profiler(binary, host):
    if (osprofiler_notifier is None or
            profiler is None or
            osprofiler_web is None or
            profiler_opts is None):
        LOG.debug('osprofiler is not present')
        return

    if CONF.profiler.enabled:
        _notifier = osprofiler_notifier.create(
            "Messaging", messaging, context.get_admin_context().to_dict(),
            base_rpc.TRANSPORT, "jacket", binary, host)
        osprofiler_notifier.set(_notifier)
        osprofiler_web.enable(CONF.profiler.hmac_keys)
        LOG.warning(
            _LW("OSProfiler is enabled.\nIt means that person who knows "
                "any of hmac_keys that are specified in "
                "/etc/jacket/jacket.conf can trace his requests. \n"
                "In real life only operator can read this file so there "
                "is no security issue. Note that even if person can "
                "trigger profiler, only admin user can retrieve trace "
                "information.\n"
                "To disable OSprofiler set in jacket.conf:\n"
                "[profiler]\nenabled=false"))
    else:
        osprofiler_web.disable()


class WSGIService(service.ServiceBase):
    """Provides ability to launch API from a 'paste' configuration."""

    def __init__(self, name, loader=None):
        """Initialize, but do not start the WSGI server.

        :param name: The name of the WSGI server given to the loader.
        :param loader: Loads the WSGI application using the given name.
        :returns: None

        """
        self.name = name
        self.manager = self._get_manager()
        self.loader = loader or wsgi_common.Loader()
        self.app = self.loader.load_app(name)
        self.host = getattr(CONF, '%s_listen' % name, "0.0.0.0")
        self.port = getattr(CONF, '%s_listen_port' % name, 0)
        self.workers = (getattr(CONF, '%s_workers' % name, None) or
                        processutils.get_worker_count())
        if self.workers and self.workers < 1:
            worker_name = '%s_workers' % name
            msg = (_("%(worker_name)s value of %(workers)d is invalid, "
                     "must be greater than 0.") %
                   {'worker_name': worker_name,
                    'workers': self.workers})
            raise exception.InvalidInput(msg)
        setup_profiler(name, self.host)

        self.server = wsgi.Server(CONF,
                                  name,
                                  self.app,
                                  host=self.host,
                                  port=self.port)

    def _get_manager(self):
        """Initialize a Manager object appropriate for this service.

        Use the service name to look up a Manager subclass from the
        configuration and initialize an instance. If no class name
        is configured, just return None.

        :returns: a Manager instance, or None.

        """
        fl = '%s_manager' % self.name
        if fl not in CONF:
            return None

        manager_class_name = CONF.get(fl, None)
        if not manager_class_name:
            return None

        manager_class = importutils.import_class(manager_class_name)
        return manager_class()

    def start(self):
        """Start serving this service using loaded configuration.

        Also, retrieve updated port number in case '0' was passed in, which
        indicates a random port should be used.

        :returns: None

        """
        if self.manager:
            self.manager.init_host()
        self.server.start()
        self.port = self.server.port

    def stop(self):
        """Stop serving this API.

        :returns: None

        """
        self.server.stop()

    def wait(self):
        """Wait for the service to stop serving this API.

        :returns: None

        """
        self.server.wait()

    def reset(self):
        """Reset server greenpool size to default.

        :returns: None

        """
        self.server.reset()


def process_launcher():
    return service.ProcessLauncher(CONF)


# NOTE(vish): the global launcher is to maintain the existing
#             functionality of calling service.serve +
#             service.wait
_launcher = None


def serve(server, workers=None):
    global _launcher
    if _launcher:
        raise RuntimeError(_('serve() can only be called once'))

    _launcher = service.launch(CONF, server, workers=workers)


def wait():
    LOG.debug('Full set of CONF:')
    for flag in CONF:
        flag_get = CONF.get(flag, None)
        # hide flag contents from log if contains a password
        # should use secret flag when switch over to openstack-common
        if ("_password" in flag or "_key" in flag or
                (flag == "sql_connection" and
                    ("mysql:" in flag_get or "postgresql:" in flag_get))):
            LOG.debug('%s : FLAG SET ', flag)
        else:
            LOG.debug('%(flag)s : %(flag_get)s',
                      {'flag': flag, 'flag_get': flag_get})
    try:
        _launcher.wait()
    except KeyboardInterrupt:
        _launcher.stop()
    base_rpc.cleanup()


class Launcher(object):
    def __init__(self):
        self.launch_service = serve
        self.wait = wait


def get_launcher():
    # Note(lpetrut): ProcessLauncher uses green pipes which fail on Windows
    # due to missing support of non-blocking I/O pipes. For this reason, the
    # service must be spawned differently on Windows, using the ServiceLauncher
    # class instead.
    if os.name == 'nt':
        return Launcher()
    else:
        return process_launcher()
