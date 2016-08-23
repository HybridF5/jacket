# Copyright (c) 2012 Nebula, Inc.
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

"""The server password extension."""

from jacket.api.compute.metadata import password
from jacket.api.compute.openstack import common
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.compute import cloud


ALIAS = 'os-server-password'
authorize = extensions.os_compute_authorizer(ALIAS)


class ServerPasswordController(wsgi.Controller):
    """The Server Password API controller for the OpenStack API."""
    def __init__(self):
        self.compute_api = cloud.API(skip_policy_check=True)

    @extensions.expected_errors(404)
    def index(self, req, server_id):
        context = req.environ['compute.context']
        authorize(context)
        instance = common.get_instance(self.compute_api, context, server_id)

        passw = password.extract_password(instance)
        return {'password': passw or ''}

    @extensions.expected_errors(404)
    @wsgi.response(204)
    def clear(self, req, server_id):
        """Removes the encrypted server password from the metadata server

        Note that this does not actually change the instance server
        password.
        """

        context = req.environ['compute.context']
        authorize(context)
        instance = common.get_instance(self.compute_api, context, server_id)
        meta = password.convert_password(context, None)
        instance.system_metadata.update(meta)
        instance.save()


class ServerPassword(extensions.V21APIExtensionBase):
    """Server password support."""

    name = "ServerPassword"
    alias = ALIAS
    version = 1

    def get_resources(self):
        resources = [
            extensions.ResourceExtension(
                ALIAS, ServerPasswordController(),
                collection_actions={'clear': 'DELETE'},
                parent=dict(member_name='server', collection_name='servers'))]
        return resources

    def get_controller_extensions(self):
        return []
