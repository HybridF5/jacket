# Copyright 2013 Nebula, Inc.
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

from jacket.api.compute.openstack import extensions


class Volume_attachment_update(extensions.ExtensionDescriptor):
    """Support for updating a volume attachment."""

    name = "VolumeAttachmentUpdate"
    alias = "os-volume-attachment-update"
    namespace = ("http://docs.openstack.org/compute/ext/"
                "os-volume-attachment-update/api/v2")
    updated = "2013-06-20T00:00:00Z"