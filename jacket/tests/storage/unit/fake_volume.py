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


def fake_db_volume(**updates):
    db_volume = {
        'id': fake.volume_id,
        'size': 1,
        'name': 'volume-%s' % fake.volume_id,
        'availability_zone': 'fake_availability_zone',
        'status': 'available',
        'attach_status': 'detached',
        'previous_status': None,
        'volume_attachment': [],
        'volume_metadata': [],
        'volume_admin_metadata': [],
        'volume_glance_metadata': [],
        'snapshots': [],
    }

    for name, field in storage.Volume.fields.items():
        if name in db_volume:
            continue
        if field.nullable:
            db_volume[name] = None
        elif field.default != fields.UnspecifiedDefault:
            db_volume[name] = field.default
        else:
            raise Exception('fake_db_volume needs help with %s.' % name)

    if updates:
        db_volume.update(updates)

    return db_volume


def fake_db_volume_type(**updates):
    db_volume_type = {
        'id': fake.volume_type_id,
        'name': 'type-1',
        'description': 'A fake volume type',
        'is_public': True,
        'projects': [],
        'extra_specs': {},
    }

    for name, field in storage.VolumeType.fields.items():
        if name in db_volume_type:
            continue
        if field.nullable:
            db_volume_type[name] = None
        elif field.default != fields.UnspecifiedDefault:
            db_volume_type[name] = field.default
        else:
            raise Exception('fake_db_volume_type needs help with %s.' % name)

    if updates:
        db_volume_type.update(updates)

    return db_volume_type


def fake_db_volume_attachment(**updates):
    db_volume_attachment = {
        'id': fake.attachment_id,
        'volume_id': fake.volume_id,
    }

    for name, field in storage.VolumeAttachment.fields.items():
        if name in db_volume_attachment:
            continue
        if field.nullable:
            db_volume_attachment[name] = None
        elif field.default != fields.UnspecifiedDefault:
            db_volume_attachment[name] = field.default
        else:
            raise Exception(
                'fake_db_volume_attachment needs help with %s.' % name)

    if updates:
        db_volume_attachment.update(updates)

    return db_volume_attachment


def fake_volume_obj(context, **updates):
    expected_attrs = updates.pop('expected_attrs',
                                 ['metadata', 'admin_metadata'])
    vol = storage.Volume._from_db_object(context, storage.Volume(),
                                         fake_db_volume(**updates),
                                         expected_attrs=expected_attrs)
    return vol


def fake_volume_type_obj(context, **updates):
    return storage.VolumeType._from_db_object(
        context, storage.VolumeType(), fake_db_volume_type(**updates))


def fake_volume_attachment_obj(context, **updates):
    return storage.VolumeAttachment._from_db_object(
        context, storage.VolumeAttachment(),
        fake_db_volume_attachment(**updates))
