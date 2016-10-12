# Copyright 2010 OpenStack Foundation
# Copyright 2015 Clinton Knight
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


import copy

from oslo_config import cfg

from jacket.api .extend import extensions
from jacket.api import openstack
from jacket.api.openstack import wsgi
from jacket.api.extend.views import versions as views_versions


CONF = cfg.CONF


_LINKS = [{
    "rel": "describedby",
    "type": "text/html",
    "href": "http://docs.openstack.org/",
}]

_MEDIA_TYPES = [{
    "base":
    "application/json",
    "type":
    "application/vnd.openstack.volume+json;version=1",
},
]

_KNOWN_VERSIONS = {
    "v1.0": {
        "id": "v1.0",
        "status": "CURRENT",
        "version": "",
        "min_version": "",
        "updated": "2016-08-16T20:25:19Z",
        "links": _LINKS,
        "media-types": _MEDIA_TYPES,
    },
}


class Versions(openstack.APIRouter):
    """Route versions requests."""

    ExtensionManager = extensions.ExtensionManager

    def _setup_routes(self, mapper, ext_mgr):
        self.resources['versions'] = create_resource()
        mapper.connect('versions', '/',
                       controller=self.resources['versions'],
                       action='all')
        mapper.redirect('', '/')


class VersionsController(wsgi.Controller):

    def __init__(self):
        super(VersionsController, self).__init__(None)

    @wsgi.Controller.api_version('1.0')
    def index(self, req):  # pylint: disable=E0102
        """Return versions supported prior to the microversions epoch."""
        builder = views_versions.get_view_builder(req)
        known_versions = copy.deepcopy(_KNOWN_VERSIONS)
        return builder.build_versions(known_versions)

    @wsgi.Controller.api_version('1.0')
    def show(self, req, id='v1.0'):
        builder = views_versions.get_view_builder(req)
        known_versions = copy.deepcopy(_KNOWN_VERSIONS)
        temp_version = known_versions[id]

        return {'version': builder._build_version(temp_version)}

    # NOTE (cknight): Calling the versions API without
    # /v1, /v2, or /v3 in the URL will lead to this unversioned
    # method, which should always return info about all
    # available versions.
    @wsgi.response(300)
    def all(self, req):
        """Return all known versions."""
        builder = views_versions.get_view_builder(req)
        known_versions = copy.deepcopy(_KNOWN_VERSIONS)
        return builder.build_versions(known_versions)


def create_resource():
    return wsgi.Resource(VersionsController())
