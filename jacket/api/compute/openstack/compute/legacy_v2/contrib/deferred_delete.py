# Copyright 2011 OpenStack Foundation
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

"""The deferred instance delete extension."""

import webob

from jacket.api.compute.openstack import common
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.compute import cloud
from jacket.compute import exception


authorize = extensions.extension_authorizer('cloud', 'deferred_delete')


class DeferredDeleteController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(DeferredDeleteController, self).__init__(*args, **kwargs)
        self.compute_api = cloud.API()

    @wsgi.action('restore')
    def _restore(self, req, id, body):
        """Restore a previously deleted instance."""
        context = req.environ["cloud.context"]
        authorize(context)
        instance = common.get_instance(self.compute_api, context, id)

        try:
            self.compute_api.restore(context, instance)
        except exception.QuotaError as error:
            raise webob.exc.HTTPForbidden(explanation=error.format_message())
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(state_error,
                    'restore', id)
        return webob.Response(status_int=202)

    @wsgi.action('forceDelete')
    def _force_delete(self, req, id, body):
        """Force delete of instance before deferred cleanup."""
        context = req.environ["cloud.context"]
        authorize(context)
        instance = common.get_instance(self.compute_api, context, id)

        try:
            self.compute_api.force_delete(context, instance)
        except exception.InstanceIsLocked as e:
            raise webob.exc.HTTPConflict(explanation=e.format_message())
        return webob.Response(status_int=202)


class Deferred_delete(extensions.ExtensionDescriptor):
    """Instance deferred delete."""

    name = "DeferredDelete"
    alias = "os-deferred-delete"
    namespace = ("http://docs.openstack.org/cloud/ext/"
                 "deferred-delete/api/v1.1")
    updated = "2011-09-01T00:00:00Z"

    def get_controller_extensions(self):
        controller = DeferredDeleteController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]
