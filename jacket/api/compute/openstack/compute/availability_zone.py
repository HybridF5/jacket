# Copyright 2012 OpenStack Foundation
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

from jacket.api.compute.openstack.compute.schemas import availability_zone as schema
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.compute import availability_zones
import jacket.compute.conf
from jacket.objects import compute as objects
from jacket.compute import servicegroup

CONF = jacket.compute.conf.CONF
ALIAS = "os-availability-zone"
ATTRIBUTE_NAME = "availability_zone"
authorize = extensions.os_compute_authorizer(ALIAS)


class AvailabilityZoneController(wsgi.Controller):
    """The Availability Zone API controller for the OpenStack API."""

    def __init__(self):
        super(AvailabilityZoneController, self).__init__()
        self.servicegroup_api = servicegroup.API()

    def _get_filtered_availability_zones(self, zones, is_available):
        result = []
        for zone in zones:
            # Hide internal_service_availability_zone
            if zone == CONF.internal_service_availability_zone:
                continue
            result.append({'zoneName': zone,
                           'zoneState': {'available': is_available},
                           "hosts": None})
        return result

    def _describe_availability_zones(self, context, **kwargs):
        ctxt = context.elevated()
        available_zones, not_available_zones = \
            availability_zones.get_availability_zones(ctxt)

        filtered_available_zones = \
            self._get_filtered_availability_zones(available_zones, True)
        filtered_not_available_zones = \
            self._get_filtered_availability_zones(not_available_zones, False)
        return {'availabilityZoneInfo': filtered_available_zones +
                                        filtered_not_available_zones}

    def _describe_availability_zones_verbose(self, context, **kwargs):
        ctxt = context.elevated()
        available_zones, not_available_zones = \
            availability_zones.get_availability_zones(ctxt)

        # Available services
        enabled_services = objects.ServiceList.get_all(context, disabled=False,
                                                       set_zones=True)
        zone_hosts = {}
        host_services = {}
        api_services = ('compute-osapi_compute', 'compute-ec2', 'compute-metadata')
        for service in enabled_services:
            if service.binary in api_services:
                # Skip API services in the listing since they are not
                # maintained in the same way as other services
                continue
            zone_hosts.setdefault(service['availability_zone'], [])
            if service['host'] not in zone_hosts[service['availability_zone']]:
                zone_hosts[service['availability_zone']].append(
                    service['host'])

            host_services.setdefault(service['availability_zone'] +
                    service['host'], [])
            host_services[service['availability_zone'] + service['host']].\
                    append(service)

        result = []
        for zone in available_zones:
            hosts = {}
            for host in zone_hosts.get(zone, []):
                hosts[host] = {}
                for service in host_services[zone + host]:
                    alive = self.servicegroup_api.service_is_up(service)
                    hosts[host][service['binary']] = {'available': alive,
                                      'active': True != service['disabled'],
                                      'updated_at': service['updated_at']}
            result.append({'zoneName': zone,
                           'zoneState': {'available': True},
                           "hosts": hosts})

        for zone in not_available_zones:
            result.append({'zoneName': zone,
                           'zoneState': {'available': False},
                           "hosts": None})
        return {'availabilityZoneInfo': result}

    @extensions.expected_errors(())
    def index(self, req):
        """Returns a summary list of availability zone."""
        context = req.environ['compute.context']
        authorize(context, action='list')

        return self._describe_availability_zones(context)

    @extensions.expected_errors(())
    def detail(self, req):
        """Returns a detailed list of availability zone."""
        context = req.environ['compute.context']
        authorize(context, action='detail')

        return self._describe_availability_zones_verbose(context)


class AvailabilityZone(extensions.V21APIExtensionBase):
    """1. Add availability_zone to the Create Server API.
       2. Add availability zones describing.
    """

    name = "AvailabilityZone"
    alias = ALIAS
    version = 1

    def get_resources(self):
        resource = [extensions.ResourceExtension(ALIAS,
            AvailabilityZoneController(),
            collection_actions={'detail': 'GET'})]
        return resource

    def get_controller_extensions(self):
        """It's an abstract function V21APIExtensionBase and the extension
        will not be loaded without it.
        """
        return []

    # NOTE(gmann): This function is not supposed to use 'body_deprecated_param'
    # parameter as this is placed to handle scheduler_hint extension for V2.1.
    def server_create(self, server_dict, create_kwargs, body_deprecated_param):
        # NOTE(alex_xu): For v2.1 compat mode, we strip the spaces when create
        # availability_zone. But we don't strip at here for backward-compatible
        # with some users already created availability_zone with
        # leading/trailing spaces with legacy v2 API.
        create_kwargs['availability_zone'] = server_dict.get(ATTRIBUTE_NAME)

    def get_server_create_schema(self, version):
        if version == "2.0":
            return schema.server_create_v20
        return schema.server_create
