# Copyright 2016 OpenStack Foundation
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

from webob import exc

from jacket.api.compute.openstack import common
from jacket.api.compute.openstack.compute.schemas import server_migrations
from jacket.api.compute.openstack import extensions
from jacket.api.compute.openstack import wsgi
from jacket.api.compute import validation
from jacket.compute import cloud
from jacket.compute import exception
from jacket.i18n import _


ALIAS = 'servers:migrations'
authorize = extensions.os_compute_authorizer(ALIAS)


def output(migration):
    """Returns the desired output of the API from an object.

    From a Migrations's object this method returns the primitive
    object with the only necessary and expected fields.
    """
    return {
        "created_at": migration.created_at,
        "dest_compute": migration.dest_compute,
        "dest_host": migration.dest_host,
        "dest_node": migration.dest_node,
        "disk_processed_bytes": migration.disk_processed,
        "disk_remaining_bytes": migration.disk_remaining,
        "disk_total_bytes": migration.disk_total,
        "id": migration.id,
        "memory_processed_bytes": migration.memory_processed,
        "memory_remaining_bytes": migration.memory_remaining,
        "memory_total_bytes": migration.memory_total,
        "server_uuid": migration.instance_uuid,
        "source_compute": migration.source_compute,
        "source_node": migration.source_node,
        "status": migration.status,
        "updated_at": migration.updated_at
    }


class ServerMigrationsController(wsgi.Controller):
    """The server migrations API controller for the OpenStack API."""

    def __init__(self):
        self.compute_api = cloud.API(skip_policy_check=True)
        super(ServerMigrationsController, self).__init__()

    @wsgi.Controller.api_version("2.22")
    @wsgi.response(202)
    @extensions.expected_errors((400, 403, 404, 409))
    @wsgi.action('force_complete')
    @validation.schema(server_migrations.force_complete)
    def _force_complete(self, req, id, server_id, body):
        context = req.environ['cloud.context']
        authorize(context, action='force_complete')

        instance = common.get_instance(self.compute_api, context, server_id)
        try:
            self.compute_api.live_migrate_force_complete(context, instance, id)
        except exception.InstanceNotFound as e:
            raise exc.HTTPNotFound(explanation=e.format_message())
        except (exception.MigrationNotFoundByStatus,
                exception.InvalidMigrationState,
                exception.MigrationNotFoundForInstance) as e:
            raise exc.HTTPBadRequest(explanation=e.format_message())
        except exception.InstanceIsLocked as e:
            raise exc.HTTPConflict(explanation=e.format_message())
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(
                state_error, 'force_complete', server_id)

    @wsgi.Controller.api_version("2.23")
    @extensions.expected_errors(404)
    def index(self, req, server_id):
        """Return all migrations of an instance in progress."""
        context = req.environ['cloud.context']
        authorize(context, action="index")

        # NOTE(Shaohe Feng) just check the instance is available. To keep
        # consistency with other API, check it before get migrations.
        common.get_instance(self.compute_api, context, server_id)

        migrations = self.compute_api.get_migrations_in_progress_by_instance(
                context, server_id, 'live-migration')

        return {'migrations': [output(migration) for migration in migrations]}

    @wsgi.Controller.api_version("2.23")
    @extensions.expected_errors(404)
    def show(self, req, server_id, id):
        """Return the migration of an instance in progress by id."""
        context = req.environ['cloud.context']
        authorize(context, action="show")

        # NOTE(Shaohe Feng) just check the instance is available. To keep
        # consistency with other API, check it before get migrations.
        common.get_instance(self.compute_api, context, server_id)

        try:
            migration = self.compute_api.get_migration_by_id_and_instance(
                    context, id, server_id)
        except exception.MigrationNotFoundForInstance:
            msg = _("In-progress live migration %(id)s is not found for"
                    " server %(uuid)s.") % {"id": id, "uuid": server_id}
            raise exc.HTTPNotFound(explanation=msg)

        if migration.get("migration_type") != "live-migration":
            msg = _("Migration %(id)s for server %(uuid)s is not"
                    " live-migration.") % {"id": id, "uuid": server_id}
            raise exc.HTTPNotFound(explanation=msg)

        # TODO(Shaohe Feng) we should share the in-progress list.
        in_progress = ['queued', 'preparing', 'running', 'post-migrating']
        if migration.get("status") not in in_progress:
            msg = _("Live migration %(id)s for server %(uuid)s is not in"
                    " progress.") % {"id": id, "uuid": server_id}
            raise exc.HTTPNotFound(explanation=msg)

        return {'migration': output(migration)}

    @wsgi.Controller.api_version("2.24")
    @wsgi.response(202)
    @extensions.expected_errors((400, 404, 409))
    def delete(self, req, server_id, id):
        """Abort an in progress migration of an instance."""
        context = req.environ['cloud.context']
        authorize(context, action="delete")

        instance = common.get_instance(self.compute_api, context, server_id)
        try:
            self.compute_api.live_migrate_abort(context, instance, id)
        except exception.InstanceInvalidState as state_error:
            common.raise_http_conflict_for_instance_invalid_state(
                    state_error, "abort live migration", server_id)
        except exception.MigrationNotFoundForInstance as e:
            raise exc.HTTPNotFound(explanation=e.format_message())
        except exception.InvalidMigrationState as e:
            raise exc.HTTPBadRequest(explanation=e.format_message())


class ServerMigrations(extensions.V21APIExtensionBase):
    """Server Migrations API."""
    name = "ServerMigrations"
    alias = 'server-migrations'
    version = 1

    def get_resources(self):
        parent = {'member_name': 'server',
                  'collection_name': 'servers'}
        member_actions = {'action': 'POST'}
        resources = [extensions.ResourceExtension(
            'migrations', ServerMigrationsController(),
            parent=parent, member_actions=member_actions)]
        return resources

    def get_controller_extensions(self):
        return []
