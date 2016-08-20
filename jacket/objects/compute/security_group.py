#    Copyright 2013 IBM Corp.
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

from jacket import db
from jacket.objects import compute
from jacket.objects.compute import base
from jacket.objects.compute import fields


# TODO(berrange): Remove NovaObjectDictCompat
@base.NovaObjectRegistry.register
class SecurityGroup(base.NovaPersistentObject, base.NovaObject,
                    base.NovaObjectDictCompat):
    # Version 1.0: Initial version
    # Version 1.1: String attributes updated to support unicode
    VERSION = '1.1'

    fields = {
        'id': fields.IntegerField(),
        'name': fields.StringField(),
        'description': fields.StringField(),
        'user_id': fields.StringField(),
        'project_id': fields.StringField(),
        }

    @staticmethod
    def _from_db_object(context, secgroup, db_secgroup):
        # NOTE(danms): These are identical right now
        for field in secgroup.fields:
            secgroup[field] = db_secgroup[field]
        secgroup._context = context
        secgroup.obj_reset_changes()
        return secgroup

    @base.remotable_classmethod
    def get(cls, context, secgroup_id):
        db_secgroup = compute.security_group_get(context, secgroup_id)
        return cls._from_db_object(context, cls(), db_secgroup)

    @base.remotable_classmethod
    def get_by_name(cls, context, project_id, group_name):
        db_secgroup = compute.security_group_get_by_name(context,
                                                    project_id,
                                                    group_name)
        return cls._from_db_object(context, cls(), db_secgroup)

    @base.remotable
    def in_use(self):
        return compute.security_group_in_use(self._context, self.id)

    @base.remotable
    def save(self):
        updates = self.obj_get_changes()
        if updates:
            db_secgroup = compute.security_group_update(self._context, self.id,
                                                   updates)
            self._from_db_object(self._context, self, db_secgroup)
        self.obj_reset_changes()

    @base.remotable
    def refresh(self):
        self._from_db_object(self._context, self,
                             compute.security_group_get(self._context, self.id))


@base.NovaObjectRegistry.register
class SecurityGroupList(base.ObjectListBase, base.NovaObject):
    # Version 1.0: Initial version
    #              SecurityGroup <= version 1.1
    VERSION = '1.0'

    fields = {
        'compute': fields.ListOfObjectsField('SecurityGroup'),
        }

    def __init__(self, *args, **kwargs):
        super(SecurityGroupList, self).__init__(*args, **kwargs)
        self.objects = []
        self.obj_reset_changes()

    @base.remotable_classmethod
    def get_all(cls, context):
        groups = compute.security_group_get_all(context)
        return base.obj_make_list(context, cls(context),
                                  compute.SecurityGroup, groups)

    @base.remotable_classmethod
    def get_by_project(cls, context, project_id):
        groups = compute.security_group_get_by_project(context, project_id)
        return base.obj_make_list(context, cls(context),
                                  compute.SecurityGroup, groups)

    @base.remotable_classmethod
    def get_by_instance(cls, context, instance):
        groups = compute.security_group_get_by_instance(context, instance.uuid)
        return base.obj_make_list(context, cls(context),
                                  compute.SecurityGroup, groups)


def make_secgroup_list(security_groups):
    """A helper to make security group compute from a list of names.

    Note that this does not make them save-able or have the rest of the
    attributes they would normally have, but provides a quick way to fill,
    for example, an instance object during create.
    """
    secgroups = compute.SecurityGroupList()
    secgroups.objects = []
    for name in security_groups:
        secgroup = compute.SecurityGroup()
        secgroup.name = name
        secgroups.objects.append(secgroup)
    return secgroups
