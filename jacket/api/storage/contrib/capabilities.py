# Copyright (c) 2015 Hitachi Data Systems, Inc.
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

from oslo_log import log as logging
import oslo_messaging

from jacket.api.storage import extensions
from jacket.api.storage.openstack import wsgi
from jacket.api.storage.views import capabilities as capabilities_view
from jacket.storage import exception
from jacket.storage.i18n import _
from jacket.objects import storage
from jacket.storage.volume import rpcapi


LOG = logging.getLogger(__name__)


def authorize(context, action_name):
    extensions.extension_authorizer('volume', action_name)(context)


class CapabilitiesController(wsgi.Controller):
    """The Capabilities controller for the OpenStack API."""

    _view_builder_class = capabilities_view.ViewBuilder

    def __init__(self):
        # FIXME(jdg):  Is it kosher that this just
        # skips the volume.api and goes straight to RPC
        # from here?
        self.volume_api = rpcapi.VolumeAPI()
        super(CapabilitiesController, self).__init__()

    def show(self, req, id):
        """Return capabilities list of given backend."""
        context = req.environ['storage.context']
        authorize(context, 'capabilities')
        filters = {'host': id, 'binary': 'storage-volume'}
        service = storage.ServiceList.get_all(context, filters)
        if not service:
            msg = (_("Can't find service: %s") % id)
            raise exception.NotFound(msg)
        try:
            capabilities = self.volume_api.get_capabilities(context, id, False)
        except oslo_messaging.MessagingTimeout:
            raise exception.RPCTimeout(service=id)
        return self._view_builder.summary(req, capabilities, id)


class Capabilities(extensions.ExtensionDescriptor):
    """Capabilities support."""

    name = "Capabilities"
    alias = "capabilities"
    namespace = "http://docs.openstack.org/volume/ext/capabilities/api/v2"
    updated = "2015-08-31T00:00:00+00:00"

    def get_resources(self):
        resources = []
        res = extensions.ResourceExtension(
            Capabilities.alias,
            CapabilitiesController())

        resources.append(res)
        return resources