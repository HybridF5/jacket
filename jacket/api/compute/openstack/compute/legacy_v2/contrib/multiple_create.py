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

from jacket.api.compute.openstack import extensions


class Multiple_create(extensions.ExtensionDescriptor):
    """Allow multiple create in the Create Server v1.1 API."""

    name = "MultipleCreate"
    alias = "os-multiple-create"
    namespace = ("http://docs.openstack.org/compute/ext/"
                 "multiplecreate/api/v1.1")
    updated = "2012-08-07T00:00:00Z"
