# Copyright (c) 2011 Zadara Storage Inc.
# Copyright (c) 2011 OpenStack Foundation
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

"""The volume type & volume types extra specs extension."""

from webob import exc

from jacket.api.storage.openstack import wsgi
from jacket.api.storage.views import types as views_types
from jacket.api.storage import xmlutil
from jacket.storage import exception
from jacket.storage.volume import volume_types


def make_voltype(elem):
    elem.set('id')
    elem.set('name')
    extra_specs = xmlutil.make_flat_dict('extra_specs', selector='extra_specs')
    elem.append(extra_specs)


class VolumeTypeTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('volume_type', selector='volume_type')
        make_voltype(root)
        return xmlutil.MasterTemplate(root, 1)


class VolumeTypesTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('volume_types')
        elem = xmlutil.SubTemplateElement(root, 'volume_type',
                                          selector='volume_types')
        make_voltype(elem)
        return xmlutil.MasterTemplate(root, 1)


class VolumeTypesController(wsgi.Controller):
    """The volume types API controller for the OpenStack API."""

    _view_builder_class = views_types.ViewBuilder

    @wsgi.serializers(xml=VolumeTypesTemplate)
    def index(self, req):
        """Returns the list of volume types."""
        context = req.environ['storage.context']
        vol_types = volume_types.get_all_types(context)
        vol_types = list(vol_types.values())
        req.cache_resource(vol_types, name='types')
        return self._view_builder.index(req, vol_types)

    @wsgi.serializers(xml=VolumeTypeTemplate)
    def show(self, req, id):
        """Return a single volume type item."""
        context = req.environ['storage.context']

        try:
            vol_type = volume_types.get_volume_type(context, id)
            req.cache_resource(vol_type, name='types')
        except exception.NotFound:
            raise exc.HTTPNotFound()

        return self._view_builder.show(req, vol_type)


def create_resource():
    return wsgi.Resource(VolumeTypesController())
