# Copyright (c) 2011 Zadara Storage Inc.
# Copyright (c) 2011 OpenStack Foundation
# Copyright 2011 University of Southern California
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
"""
Unit Tests for volume types extra specs code
"""

from jacket import context
from jacket import db
from jacket.storage import exception
from jacket.objects import storage
from jacket.storage import test
from jacket.tests.storage.unit import fake_constants as fake


class VolumeGlanceMetadataTestCase(test.TestCase):

    def setUp(self):
        super(VolumeGlanceMetadataTestCase, self).setUp()
        self.ctxt = context.get_admin_context()
        storage.register_all()

    def test_vol_glance_metadata_bad_vol_id(self):
        ctxt = context.get_admin_context()
        self.assertRaises(exception.VolumeNotFound,
                          storage.volume_glance_metadata_create,
                          ctxt, fake.volume_id, 'key1', 'value1')
        self.assertRaises(exception.VolumeNotFound,
                          storage.volume_glance_metadata_get, ctxt, fake.volume_id)
        storage.volume_glance_metadata_delete_by_volume(ctxt, fake.volume2_id)

    def test_vol_update_glance_metadata(self):
        ctxt = context.get_admin_context()
        storage.volume_create(ctxt, {'id': fake.volume_id})
        storage.volume_create(ctxt, {'id': fake.volume2_id})
        storage.volume_glance_metadata_create(ctxt, fake.volume_id, 'key1',
                                         'value1')
        storage.volume_glance_metadata_create(ctxt, fake.volume2_id, 'key1',
                                         'value1')
        storage.volume_glance_metadata_create(ctxt, fake.volume2_id, 'key2',
                                         'value2')
        storage.volume_glance_metadata_create(ctxt, fake.volume2_id, 'key3', 123)

        expected_metadata_1 = {'volume_id': fake.volume_id,
                               'key': 'key1',
                               'value': 'value1'}

        metadata = storage.volume_glance_metadata_get(ctxt, fake.volume_id)
        self.assertEqual(1, len(metadata))
        for key, value in expected_metadata_1.items():
            self.assertEqual(value, metadata[0][key])

        expected_metadata_2 = ({'volume_id': fake.volume2_id,
                                'key': 'key1',
                                'value': 'value1'},
                               {'volume_id': fake.volume2_id,
                                'key': 'key2',
                                'value': 'value2'},
                               {'volume_id': fake.volume2_id,
                                'key': 'key3',
                                'value': '123'})

        metadata = storage.volume_glance_metadata_get(ctxt, fake.volume2_id)
        self.assertEqual(3, len(metadata))
        for expected, meta in zip(expected_metadata_2, metadata):
            for key, value in expected.items():
                self.assertEqual(value, meta[key])

        self.assertRaises(exception.GlanceMetadataExists,
                          storage.volume_glance_metadata_create,
                          ctxt, fake.volume_id, 'key1', 'value1a')

        metadata = storage.volume_glance_metadata_get(ctxt, fake.volume_id)
        self.assertEqual(1, len(metadata))
        for key, value in expected_metadata_1.items():
            self.assertEqual(value, metadata[0][key])

    def test_vols_get_glance_metadata(self):
        ctxt = context.get_admin_context()
        storage.volume_create(ctxt, {'id': fake.volume_id})
        storage.volume_create(ctxt, {'id': fake.volume2_id})
        storage.volume_create(ctxt, {'id': '3'})
        storage.volume_glance_metadata_create(ctxt, fake.volume_id, 'key1',
                                         'value1')
        storage.volume_glance_metadata_create(ctxt, fake.volume2_id, 'key2',
                                         'value2')
        storage.volume_glance_metadata_create(ctxt, fake.volume2_id, 'key22',
                                         'value22')

        metadata = storage.volume_glance_metadata_get_all(ctxt)
        self.assertEqual(3, len(metadata))
        self._assert_metadata_equals(fake.volume_id, 'key1', 'value1',
                                     metadata[0])
        self._assert_metadata_equals(fake.volume2_id, 'key2', 'value2',
                                     metadata[1])
        self._assert_metadata_equals(fake.volume2_id, 'key22', 'value22',
                                     metadata[2])

    def _assert_metadata_equals(self, volume_id, key, value, observed):
        self.assertEqual(volume_id, observed.volume_id)
        self.assertEqual(key, observed.key)
        self.assertEqual(value, observed.value)

    def test_vol_delete_glance_metadata(self):
        ctxt = context.get_admin_context()
        storage.volume_create(ctxt, {'id': fake.volume_id})
        storage.volume_glance_metadata_delete_by_volume(ctxt, fake.volume_id)
        storage.volume_glance_metadata_create(ctxt, fake.volume_id, 'key1',
                                         'value1')
        storage.volume_glance_metadata_delete_by_volume(ctxt, fake.volume_id)
        self.assertRaises(exception.GlanceMetadataNotFound,
                          storage.volume_glance_metadata_get, ctxt, fake.volume_id)

    def test_vol_glance_metadata_copy_to_snapshot(self):
        ctxt = context.get_admin_context()
        storage.volume_create(ctxt, {'id': fake.volume_id})
        snap = storage.Snapshot(ctxt, volume_id=fake.volume_id)
        snap.create()
        storage.volume_glance_metadata_create(ctxt, fake.volume_id, 'key1',
                                         'value1')
        storage.volume_glance_metadata_copy_to_snapshot(ctxt, snap.id,
                                                   fake.volume_id)

        expected_meta = {'snapshot_id': snap.id,
                         'key': 'key1',
                         'value': 'value1'}

        for meta in storage.volume_snapshot_glance_metadata_get(ctxt, snap.id):
            for (key, value) in expected_meta.items():
                self.assertEqual(value, meta[key])
        snap.destroy()

    def test_vol_glance_metadata_copy_from_volume_to_volume(self):
        ctxt = context.get_admin_context()
        storage.volume_create(ctxt, {'id': fake.volume_id})
        storage.volume_create(ctxt, {'id': fake.volume2_id,
                                'source_volid': fake.volume_id})
        storage.volume_glance_metadata_create(ctxt, fake.volume_id, 'key1',
                                         'value1')
        storage.volume_glance_metadata_copy_from_volume_to_volume(ctxt,
                                                             fake.volume_id,
                                                             fake.volume2_id)

        expected_meta = {'key': 'key1',
                         'value': 'value1'}

        for meta in storage.volume_glance_metadata_get(ctxt, fake.volume2_id):
            for (key, value) in expected_meta.items():
                self.assertEqual(value, meta[key])

    def test_volume_glance_metadata_copy_to_volume(self):
        vol1 = storage.volume_create(self.ctxt, {})
        vol2 = storage.volume_create(self.ctxt, {})
        storage.volume_glance_metadata_create(self.ctxt, vol1['id'], 'm1', 'v1')
        snapshot = storage.Snapshot(self.ctxt, volume_id=vol1['id'])
        snapshot.create()
        storage.volume_glance_metadata_copy_to_snapshot(self.ctxt, snapshot.id,
                                                   vol1['id'])
        storage.volume_glance_metadata_copy_to_volume(self.ctxt, vol2['id'],
                                                 snapshot.id)
        metadata = storage.volume_glance_metadata_get(self.ctxt, vol2['id'])
        metadata = {m['key']: m['value'] for m in metadata}
        self.assertEqual({'m1': 'v1'}, metadata)

    def test_volume_snapshot_glance_metadata_get_nonexistent(self):
        vol = storage.volume_create(self.ctxt, {})
        snapshot = storage.Snapshot(self.ctxt, volume_id=vol['id'])
        snapshot.create()
        self.assertRaises(exception.GlanceMetadataNotFound,
                          storage.volume_snapshot_glance_metadata_get,
                          self.ctxt, snapshot.id)
        snapshot.destroy()
