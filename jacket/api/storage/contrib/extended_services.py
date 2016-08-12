# Copyright 2014 IBM Corp.
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

from jacket.api.storage import extensions


class Extended_services(extensions.ExtensionDescriptor):
    """Extended services support."""

    name = "ExtendedServices"
    alias = "os-extended-services"
    namespace = ("http://docs.openstack.org/volume/ext/"
                 "extended_services/api/v2")
    updated = "2014-01-10T00:00:00-00:00"
