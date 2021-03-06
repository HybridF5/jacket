# Copyright (C) 2012 - 2014 EMC Corporation.
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

"""The consistencygroups api."""

from oslo_log import log as logging
from oslo_utils import strutils
import webob
from webob import exc

from jacket.api.storage import common
from jacket.api.storage import extensions
from jacket.api.storage.openstack import wsgi
from jacket.api.storage.views import consistencygroups as consistencygroup_views
from jacket.api.storage import xmlutil
from jacket.storage import consistencygroup as consistencygroupAPI
from jacket.storage import exception
from jacket.storage.i18n import _, _LI
from jacket.storage import utils

LOG = logging.getLogger(__name__)


def make_consistencygroup(elem):
    elem.set('id')
    elem.set('status')
    elem.set('availability_zone')
    elem.set('created_at')
    elem.set('name')
    elem.set('description')


def make_consistencygroup_from_src(elem):
    elem.set('id')
    elem.set('status')
    elem.set('created_at')
    elem.set('name')
    elem.set('description')
    elem.set('cgsnapshot_id')
    elem.set('source_cgid')


class ConsistencyGroupTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('consistencygroup',
                                       selector='consistencygroup')
        make_consistencygroup(root)
        alias = Consistencygroups.alias
        namespace = Consistencygroups.namespace
        return xmlutil.MasterTemplate(root, 1, nsmap={alias: namespace})


class ConsistencyGroupsTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('consistencygroups')
        elem = xmlutil.SubTemplateElement(root, 'consistencygroup',
                                          selector='consistencygroups')
        make_consistencygroup(elem)
        alias = Consistencygroups.alias
        namespace = Consistencygroups.namespace
        return xmlutil.MasterTemplate(root, 1, nsmap={alias: namespace})


class ConsistencyGroupFromSrcTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('consistencygroup-from-src',
                                       selector='consistencygroup-from-src')
        make_consistencygroup_from_src(root)
        alias = Consistencygroups.alias
        namespace = Consistencygroups.namespace
        return xmlutil.MasterTemplate(root, 1, nsmap={alias: namespace})


class CreateDeserializer(wsgi.MetadataXMLDeserializer):
    def default(self, string):
        dom = utils.safe_minidom_parse_string(string)
        consistencygroup = self._extract_consistencygroup(dom)
        return {'body': {'consistencygroup': consistencygroup}}

    def _extract_consistencygroup(self, node):
        consistencygroup = {}
        consistencygroup_node = self.find_first_child_named(
            node,
            'consistencygroup')

        attributes = ['name',
                      'description']

        for attr in attributes:
            if consistencygroup_node.getAttribute(attr):
                consistencygroup[attr] = consistencygroup_node.\
                    getAttribute(attr)
        return consistencygroup


class CreateFromSrcDeserializer(wsgi.MetadataXMLDeserializer):
    def default(self, string):
        dom = utils.safe_minidom_parse_string(string)
        consistencygroup = self._extract_consistencygroup(dom)
        retval = {'body': {'consistencygroup-from-src': consistencygroup}}
        return retval

    def _extract_consistencygroup(self, node):
        consistencygroup = {}
        consistencygroup_node = self.find_first_child_named(
            node, 'consistencygroup-from-src')

        attributes = ['cgsnapshot', 'source_cgid', 'name', 'description']

        for attr in attributes:
            if consistencygroup_node.getAttribute(attr):
                consistencygroup[attr] = (
                    consistencygroup_node.getAttribute(attr))
        return consistencygroup


class ConsistencyGroupsController(wsgi.Controller):
    """The ConsistencyGroups API controller for the OpenStack API."""

    _view_builder_class = consistencygroup_views.ViewBuilder

    def __init__(self):
        self.consistencygroup_api = consistencygroupAPI.API()
        super(ConsistencyGroupsController, self).__init__()

    @wsgi.serializers(xml=ConsistencyGroupTemplate)
    def show(self, req, id):
        """Return data about the given consistency group."""
        LOG.debug('show called for member %s', id)
        context = req.environ['storage.context']

        try:
            consistencygroup = self.consistencygroup_api.get(
                context,
                group_id=id)
        except exception.ConsistencyGroupNotFound as error:
            raise exc.HTTPNotFound(explanation=error.msg)

        return self._view_builder.detail(req, consistencygroup)

    def delete(self, req, id, body):
        """Delete a consistency group."""
        LOG.debug('delete called for member %s', id)
        context = req.environ['storage.context']
        force = False
        if body:
            if not self.is_valid_body(body, 'consistencygroup'):
                msg = _("Missing required element 'consistencygroup' in "
                        "request body.")
                raise exc.HTTPBadRequest(explanation=msg)

            cg_body = body['consistencygroup']
            try:
                force = strutils.bool_from_string(cg_body.get('force', False),
                                                  strict=True)
            except ValueError:
                msg = _("Invalid value '%s' for force.") % force
                raise exc.HTTPBadRequest(explanation=msg)

        LOG.info(_LI('Delete consistency group with id: %s'), id,
                 context=context)

        try:
            group = self.consistencygroup_api.get(context, id)
            self.consistencygroup_api.delete(context, group, force)
        except exception.ConsistencyGroupNotFound as error:
            raise exc.HTTPNotFound(explanation=error.msg)
        except exception.InvalidConsistencyGroup as error:
            raise exc.HTTPBadRequest(explanation=error.msg)

        return webob.Response(status_int=202)

    @wsgi.serializers(xml=ConsistencyGroupsTemplate)
    def index(self, req):
        """Returns a summary list of consistency groups."""
        return self._get_consistencygroups(req, is_detail=False)

    @wsgi.serializers(xml=ConsistencyGroupsTemplate)
    def detail(self, req):
        """Returns a detailed list of consistency groups."""
        return self._get_consistencygroups(req, is_detail=True)

    def _get_consistencygroups(self, req, is_detail):
        """Returns a list of consistency groups through view builder."""
        context = req.environ['storage.context']
        filters = req.params.copy()
        marker, limit, offset = common.get_pagination_params(filters)
        sort_keys, sort_dirs = common.get_sort_params(filters)

        consistencygroups = self.consistencygroup_api.get_all(
            context, filters=filters, marker=marker, limit=limit,
            offset=offset, sort_keys=sort_keys, sort_dirs=sort_dirs)

        if is_detail:
            consistencygroups = self._view_builder.detail_list(
                req, consistencygroups)
        else:
            consistencygroups = self._view_builder.summary_list(
                req, consistencygroups)
        return consistencygroups

    @wsgi.response(202)
    @wsgi.serializers(xml=ConsistencyGroupTemplate)
    @wsgi.deserializers(xml=CreateDeserializer)
    def create(self, req, body):
        """Create a new consistency group."""
        LOG.debug('Creating new consistency group %s', body)
        self.assert_valid_body(body, 'consistencygroup')

        context = req.environ['storage.context']
        consistencygroup = body['consistencygroup']
        self.validate_name_and_description(consistencygroup)
        name = consistencygroup.get('name', None)
        description = consistencygroup.get('description', None)
        volume_types = consistencygroup.get('volume_types', None)
        if not volume_types:
            msg = _("volume_types must be provided to create "
                    "consistency group %(name)s.") % {'name': name}
            raise exc.HTTPBadRequest(explanation=msg)
        availability_zone = consistencygroup.get('availability_zone', None)

        LOG.info(_LI("Creating consistency group %(name)s."),
                 {'name': name},
                 context=context)

        try:
            new_consistencygroup = self.consistencygroup_api.create(
                context, name, description, volume_types,
                availability_zone=availability_zone)
        except exception.InvalidConsistencyGroup as error:
            raise exc.HTTPBadRequest(explanation=error.msg)
        except exception.InvalidVolumeType as error:
            raise exc.HTTPBadRequest(explanation=error.msg)
        except exception.ConsistencyGroupNotFound as error:
            raise exc.HTTPNotFound(explanation=error.msg)

        retval = self._view_builder.summary(req, new_consistencygroup)
        return retval

    @wsgi.response(202)
    @wsgi.serializers(xml=ConsistencyGroupFromSrcTemplate)
    @wsgi.deserializers(xml=CreateFromSrcDeserializer)
    def create_from_src(self, req, body):
        """Create a new consistency group from a source.

        The source can be a CG snapshot or a CG. Note that
        this does not require volume_types as the "create"
        API above.
        """
        LOG.debug('Creating new consistency group %s.', body)
        self.assert_valid_body(body, 'consistencygroup-from-src')

        context = req.environ['storage.context']
        consistencygroup = body['consistencygroup-from-src']
        self.validate_name_and_description(consistencygroup)
        name = consistencygroup.get('name', None)
        description = consistencygroup.get('description', None)
        cgsnapshot_id = consistencygroup.get('cgsnapshot_id', None)
        source_cgid = consistencygroup.get('source_cgid', None)
        if not cgsnapshot_id and not source_cgid:
            msg = _("Either 'cgsnapshot_id' or 'source_cgid' must be "
                    "provided to create consistency group %(name)s "
                    "from source.") % {'name': name}
            raise exc.HTTPBadRequest(explanation=msg)

        if cgsnapshot_id and source_cgid:
            msg = _("Cannot provide both 'cgsnapshot_id' and 'source_cgid' "
                    "to create consistency group %(name)s from "
                    "source.") % {'name': name}
            raise exc.HTTPBadRequest(explanation=msg)

        if cgsnapshot_id:
            LOG.info(_LI("Creating consistency group %(name)s from "
                         "cgsnapshot %(snap)s."),
                     {'name': name, 'snap': cgsnapshot_id},
                     context=context)
        elif source_cgid:
            LOG.info(_LI("Creating consistency group %(name)s from "
                         "source consistency group %(source_cgid)s."),
                     {'name': name, 'source_cgid': source_cgid},
                     context=context)

        try:
            new_consistencygroup = self.consistencygroup_api.create_from_src(
                context, name, description, cgsnapshot_id, source_cgid)
        except exception.InvalidConsistencyGroup as error:
            raise exc.HTTPBadRequest(explanation=error.msg)
        except exception.CgSnapshotNotFound as error:
            raise exc.HTTPNotFound(explanation=error.msg)
        except exception.ConsistencyGroupNotFound as error:
            raise exc.HTTPNotFound(explanation=error.msg)
        except exception.CinderException as error:
            raise exc.HTTPBadRequest(explanation=error.msg)

        retval = self._view_builder.summary(req, new_consistencygroup)
        return retval

    @wsgi.serializers(xml=ConsistencyGroupTemplate)
    def update(self, req, id, body):
        """Update the consistency group.

        Expected format of the input parameter 'body':
        {
            "consistencygroup":
            {
                "name": "my_cg",
                "description": "My consistency group",
                "add_volumes": "volume-uuid-1,volume-uuid-2,..."
                "remove_volumes": "volume-uuid-8,volume-uuid-9,..."
            }
        }
        """
        LOG.debug('Update called for consistency group %s.', id)

        if not body:
            msg = _("Missing request body.")
            raise exc.HTTPBadRequest(explanation=msg)

        self.assert_valid_body(body, 'consistencygroup')
        context = req.environ['storage.context']

        consistencygroup = body.get('consistencygroup', None)
        self.validate_name_and_description(consistencygroup)
        name = consistencygroup.get('name', None)
        description = consistencygroup.get('description', None)
        add_volumes = consistencygroup.get('add_volumes', None)
        remove_volumes = consistencygroup.get('remove_volumes', None)

        if (not name and not description and not add_volumes
                and not remove_volumes):
            msg = _("Name, description, add_volumes, and remove_volumes "
                    "can not be all empty in the request body.")
            raise exc.HTTPBadRequest(explanation=msg)

        LOG.info(_LI("Updating consistency group %(id)s with name %(name)s "
                     "description: %(description)s add_volumes: "
                     "%(add_volumes)s remove_volumes: %(remove_volumes)s."),
                 {'id': id, 'name': name,
                  'description': description,
                  'add_volumes': add_volumes,
                  'remove_volumes': remove_volumes},
                 context=context)

        try:
            group = self.consistencygroup_api.get(context, id)
            self.consistencygroup_api.update(
                context, group, name, description,
                add_volumes, remove_volumes)
        except exception.ConsistencyGroupNotFound as error:
            raise exc.HTTPNotFound(explanation=error.msg)
        except exception.InvalidConsistencyGroup as error:
            raise exc.HTTPBadRequest(explanation=error.msg)

        return webob.Response(status_int=202)


class Consistencygroups(extensions.ExtensionDescriptor):
    """consistency groups support."""

    name = 'Consistencygroups'
    alias = 'consistencygroups'
    namespace = 'http://docs.openstack.org/volume/ext/consistencygroups/api/v1'
    updated = '2014-08-18T00:00:00+00:00'

    def get_resources(self):
        resources = []
        res = extensions.ResourceExtension(
            Consistencygroups.alias, ConsistencyGroupsController(),
            collection_actions={'detail': 'GET', 'create_from_src': 'POST'},
            member_actions={'delete': 'POST', 'update': 'PUT'})
        resources.append(res)
        return resources
