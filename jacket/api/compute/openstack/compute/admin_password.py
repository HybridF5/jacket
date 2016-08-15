# Copyright 2013 IBM Corp.
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

from webob import exc

from jacket.api.compute.openstack import common
from jacket.api.compute.openstack.compute.schemas import admin_password
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.api.compute import validation
from jacket.compute import cloud
from jacket.compute import exception
from jacket.i18n import _


ALIAS = "os-admin-password"
authorize = extensions.os_compute_authorizer(ALIAS)


class AdminPasswordController(wsgi.Controller):

    def __init__(self, *args, **kwargs):
        super(AdminPasswordController, self).__init__(*args, **kwargs)
        self.compute_api = cloud.API(skip_policy_check=True)

    # TODO(eliqiao): Here should be 204(No content) instead of 202 by v2.1
    # +micorversions because the password has been changed when returning
    # a response.
    @wsgi.action('changePassword')
    @wsgi.response(202)
    @extensions.expected_errors((400, 404, 409, 501))
    @validation.schema(admin_password.change_password)
    def change_password(self, req, id, body):
        context = req.environ['cloud.context']
        authorize(context)

        password = body['changePassword']['adminPass']
        instance = common.get_instance(self.compute_api, context, id)
        try:
            self.compute_api.set_admin_password(context, instance, password)
        except exception.InstanceUnknownCell as e:
            raise exc.HTTPNotFound(explanation=e.format_message())
        except exception.InstancePasswordSetFailed as e:
            raise exc.HTTPConflict(explanation=e.format_message())
        except exception.InstanceInvalidState as e:
            raise common.raise_http_conflict_for_instance_invalid_state(
                e, 'changePassword', id)
        except NotImplementedError:
            msg = _("Unable to set password on instance")
            common.raise_feature_not_supported(msg=msg)


class AdminPassword(extensions.V21APIExtensionBase):
    """Admin password management support."""

    name = "AdminPassword"
    alias = ALIAS
    version = 1

    def get_resources(self):
        return []

    def get_controller_extensions(self):
        controller = AdminPasswordController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]