#   Copyright 2011 OpenStack Foundation
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

from webob import exc

from jacket.api.compute.openstack import common
from jacket.api.compute.openstack.compute.schemas import reset_server_state
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.api.compute import validation
from jacket.compute import cloud
from jacket.compute.cloud import vm_states
from jacket.compute import exception

ALIAS = "os-admin-actions"

# States usable in resetState action
# NOTE: It is necessary to update the schema of cloud/api/openstack/cloud/
# schemas/reset_server_state.py, when updating this state_map.
state_map = dict(active=vm_states.ACTIVE, error=vm_states.ERROR)

authorize = extensions.os_compute_authorizer(ALIAS)


class AdminActionsController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(AdminActionsController, self).__init__(*args, **kwargs)
        self.compute_api = cloud.API(skip_policy_check=True)

    @wsgi.response(202)
    @extensions.expected_errors((404, 409))
    @wsgi.action('resetNetwork')
    def _reset_network(self, req, id, body):
        """Permit admins to reset networking on a server."""
        context = req.environ['cloud.context']
        authorize(context, action='reset_network')
        try:
            instance = common.get_instance(self.compute_api, context, id)
            self.compute_api.reset_network(context, instance)
        except exception.InstanceUnknownCell as e:
            raise exc.HTTPNotFound(explanation=e.format_message())
        except exception.InstanceIsLocked as e:
            raise exc.HTTPConflict(explanation=e.format_message())

    @wsgi.response(202)
    @extensions.expected_errors((404, 409))
    @wsgi.action('injectNetworkInfo')
    def _inject_network_info(self, req, id, body):
        """Permit admins to inject network info into a server."""
        context = req.environ['cloud.context']
        authorize(context, action='inject_network_info')
        try:
            instance = common.get_instance(self.compute_api, context, id)
            self.compute_api.inject_network_info(context, instance)
        except exception.InstanceUnknownCell as e:
            raise exc.HTTPNotFound(explanation=e.format_message())
        except exception.InstanceIsLocked as e:
            raise exc.HTTPConflict(explanation=e.format_message())

    @wsgi.response(202)
    @extensions.expected_errors(404)
    @wsgi.action('os-resetState')
    @validation.schema(reset_server_state.reset_state)
    def _reset_state(self, req, id, body):
        """Permit admins to reset the state of a server."""
        context = req.environ["cloud.context"]
        authorize(context, action='reset_state')

        # Identify the desired state from the body
        state = state_map[body["os-resetState"]["state"]]

        instance = common.get_instance(self.compute_api, context, id)
        instance.vm_state = state
        instance.task_state = None
        instance.save(admin_state_reset=True)


class AdminActions(extensions.V21APIExtensionBase):
    """Enable admin-only server actions

    Actions include: resetNetwork, injectNetworkInfo, os-resetState
    """

    name = "AdminActions"
    alias = ALIAS
    version = 1

    def get_controller_extensions(self):
        controller = AdminActionsController()
        extension = extensions.ControllerExtension(self, 'servers', controller)
        return [extension]

    def get_resources(self):
        return []
