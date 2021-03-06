#    Copyright 2015 SimpliVity Corp.
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

from oslo_versionedobjects import fields

from jacket.objects import storage
from jacket.tests.storage.unit import fake_constants as fake


def fake_db_consistencygroup(**updates):
    db_values = {
        'id': fake.consistency_group_id,
        'user_id': fake.user_id,
        'project_id': fake.project_id,
        'host': 'FakeHost',
        'volumes': [],
    }
    for name, field in storage.ConsistencyGroup.fields.items():
        if name in db_values:
            continue
        if field.nullable:
            db_values[name] = None
        elif field.default != fields.UnspecifiedDefault:
            db_values[name] = field.default
        else:
            raise Exception('fake_db_consistencygroup needs help with %s' %
                            name)

    if updates:
        db_values.update(updates)

    return db_values


def fake_consistencyobject_obj(context, **updates):
    return storage.ConsistencyGroup._from_db_object(context,
                                                    storage.ConsistencyGroup(),
                                                    fake_db_consistencygroup(
                                                        **updates))
