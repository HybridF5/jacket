# Copyright 2012 Midokura Japan K.K.
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

import webob

from jacket.api.compute.openstack import common
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.compute import cloud
from jacket.compute import exception
from jacket.i18n import _
from jacket.objects import compute


class ServerStartStopActionController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(ServerStartStopActionController, self).__init__(*args, **kwargs)
        self.compute_api = cloud.API()

    def _get_instance(self, context, instance_uuid):
        try:
            attrs = ['system_metadata', 'metadata']
            return cloud.Instance.get_by_uuid(context, instance_uuid,
                                                expected_attrs=attrs)
        except exception.NotFound:
            msg = _("Instance not found")
            raise webob.exc.HTTPNotFound(explanation=msg)

    @wsgi.action('os-start')
    def _start_server(self, req, id, body):
        """Start an instance."""
        context = req.environ['cloud.context']
        instance = self._get_instance(context, id)
        extensions.check_compute_policy(context, 'start', instance)

        try:
            self.compute_api.start(context, instance)
        except (exception.InstanceNotReady, exception.InstanceIsLocked) as e:
            raise webob.exc.HTTPConflict(explanation=e.format_message())
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(state_error,
                'start', id)
        return webob.Response(status_int=202)

    @wsgi.action('os-stop')
    def _stop_server(self, req, id, body):
        """Stop an instance."""
        context = req.environ['cloud.context']
        instance = self._get_instance(context, id)
        extensions.check_compute_policy(context, 'stop', instance)

        try:
            self.compute_api.stop(context, instance)
        except (exception.InstanceNotReady, exception.InstanceIsLocked) as e:
            raise webob.exc.HTTPConflict(explanation=e.format_message())
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(state_error,
                'stop', id)
        return webob.Response(status_int=202)


class Server_start_stop(extensions.ExtensionDescriptor):
    """Start/Stop instance cloud API support."""

    name = "ServerStartStop"
    alias = "os-server-start-stop"
    namespace = "http://docs.openstack.org/cloud/ext/servers/api/v1.1"
    updated = "2012-01-23T00:00:00Z"

    def get_controller_extensions(self):
        controller = ServerStartStopActionController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]
