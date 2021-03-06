# Copyright 2013 Netease, LLC.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""The Extended Availability Zone Status API extension."""

from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.compute import availability_zones as avail_zone

ALIAS = "os-extended-availability-zone"
authorize = extensions.os_compute_soft_authorizer(ALIAS)
PREFIX = "OS-EXT-AZ"


class ExtendedAZController(wsgi.Controller):
    def _extend_server(self, context, server, instance):
        # NOTE(mriedem): The OS-EXT-AZ prefix should not be used for new
        # attributes after v2.1. They are only in v2.1 for backward compat
        # with v2.0.
        key = "%s:availability_zone" % PREFIX
        az = avail_zone.get_instance_availability_zone(context, instance)
        server[key] = az or ''

    @wsgi.extends
    def show(self, req, resp_obj, id):
        context = req.environ['compute.context']
        if authorize(context):
            server = resp_obj.obj['server']
            db_instance = req.get_db_instance(server['id'])
            self._extend_server(context, server, db_instance)

    @wsgi.extends
    def detail(self, req, resp_obj):
        context = req.environ['compute.context']
        if authorize(context):
            servers = list(resp_obj.obj['servers'])
            for server in servers:
                db_instance = req.get_db_instance(server['id'])
                self._extend_server(context, server, db_instance)


class ExtendedAvailabilityZone(extensions.V21APIExtensionBase):
    """Extended Availability Zone support."""

    name = "ExtendedAvailabilityZone"
    alias = ALIAS
    version = 1

    def get_controller_extensions(self):
        controller = ExtendedAZController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]

    def get_resources(self):
        return []
