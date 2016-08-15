#    Copyright (c) 2015 Dell Inc.
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

import ddt
import mock
from requests import models
import uuid

from jacket.storage import context
from jacket.storage import exception
from jacket.storage import test
from jacket.storage.volume.drivers.dell import dell_storagecenter_api


# We patch these here as they are used by every test to keep
# from trying to contact a Dell Storage Center.
@ddt.ddt
@mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                   '__init__',
                   return_value=None)
@mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                   'open_connection')
@mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                   'close_connection')
class DellSCSanAPITestCase(test.TestCase):

    """DellSCSanAPITestCase

    Class to test the Storage Center API using Mock.
    """

    SC = {u'IPv6ManagementIPPrefix': 128,
          u'connectionError': u'',
          u'instanceId': u'64702',
          u'scSerialNumber': 64702,
          u'dataProgressionRunning': False,
          u'hostOrIpAddress': u'192.168.0.80',
          u'userConnected': True,
          u'portsBalanced': True,
          u'managementIp': u'192.168.0.80',
          u'version': u'6.5.1.269',
          u'location': u'',
          u'objectType': u'StorageCenter',
          u'instanceName': u'Storage Center 64702',
          u'statusMessage': u'',
          u'status': u'Up',
          u'flashOptimizedConfigured': False,
          u'connected': True,
          u'operationMode': u'Normal',
          u'userName': u'Admin',
          u'nonFlashOptimizedConfigured': True,
          u'name': u'Storage Center 64702',
          u'scName': u'Storage Center 64702',
          u'notes': u'',
          u'serialNumber': 64702,
          u'raidRebalanceRunning': False,
          u'userPasswordExpired': False,
          u'contact': u'',
          u'IPv6ManagementIP': u'::'}

    VOLUME = {u'instanceId': u'64702.3494',
              u'scSerialNumber': 64702,
              u'replicationSource': False,
              u'liveVolume': False,
              u'vpdId': 3496,
              u'objectType': u'ScVolume',
              u'index': 3494,
              u'volumeFolderPath': u'devstackvol/fcvm/',
              u'hostCacheEnabled': False,
              u'usedByLegacyFluidFsNasVolume': False,
              u'inRecycleBin': False,
              u'volumeFolderIndex': 17,
              u'instanceName': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
              u'statusMessage': u'',
              u'status': u'Up',
              u'storageType': {u'instanceId': u'64702.1',
                               u'instanceName': u'Assigned - Redundant - 2 MB',
                               u'objectType': u'ScStorageType'},
              u'cmmDestination': False,
              u'replicationDestination': False,
              u'volumeFolder': {u'instanceId': u'64702.17',
                                u'instanceName': u'fcvm',
                                u'objectType': u'ScVolumeFolder'},
              u'deviceId': u'6000d31000fcbe000000000000000da8',
              u'active': True,
              u'portableVolumeDestination': False,
              u'deleteAllowed': True,
              u'name': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
              u'scName': u'Storage Center 64702',
              u'secureDataUsed': False,
              u'serialNumber': u'0000fcbe-00000da8',
              u'replayAllowed': True,
              u'flashOptimized': False,
              u'configuredSize': u'1.073741824E9 Bytes',
              u'mapped': False,
              u'cmmSource': False}

    VOLUME_LIST = [{u'instanceId': u'64702.3494',
                    u'scSerialNumber': 64702,
                    u'replicationSource': False,
                    u'liveVolume': False,
                    u'vpdId': 3496,
                    u'objectType': u'ScVolume',
                    u'index': 3494,
                    u'volumeFolderPath': u'devstackvol/fcvm/',
                    u'hostCacheEnabled': False,
                    u'usedByLegacyFluidFsNasVolume': False,
                    u'inRecycleBin': False,
                    u'volumeFolderIndex': 17,
                    u'instanceName':
                        u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
                    u'statusMessage': u'',
                    u'status': u'Up',
                    u'storageType': {u'instanceId': u'64702.1',
                                     u'instanceName':
                                     u'Assigned - Redundant - 2 MB',
                                     u'objectType': u'ScStorageType'},
                    u'cmmDestination': False,
                    u'replicationDestination': False,
                    u'volumeFolder': {u'instanceId': u'64702.17',
                                      u'instanceName': u'fcvm',
                                      u'objectType': u'ScVolumeFolder'},
                    u'deviceId': u'6000d31000fcbe000000000000000da8',
                    u'active': True,
                    u'portableVolumeDestination': False,
                    u'deleteAllowed': True,
                    u'name': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
                    u'scName': u'Storage Center 64702',
                    u'secureDataUsed': False,
                    u'serialNumber': u'0000fcbe-00000da8',
                    u'replayAllowed': True,
                    u'flashOptimized': False,
                    u'configuredSize': u'1.073741824E9 Bytes',
                    u'mapped': False,
                    u'cmmSource': False}]

    # Volume list that contains multiple volumes
    VOLUME_LIST_MULTI_VOLS = [
        {u'instanceId': u'64702.3494',
         u'scSerialNumber': 64702,
         u'replicationSource': False,
         u'liveVolume': False,
         u'vpdId': 3496,
         u'objectType': u'ScVolume',
         u'index': 3494,
         u'volumeFolderPath': u'devstackvol/fcvm/',
         u'hostCacheEnabled': False,
         u'usedByLegacyFluidFsNasVolume': False,
         u'inRecycleBin': False,
         u'volumeFolderIndex': 17,
         u'instanceName':
                        u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
         u'statusMessage': u'',
         u'status': u'Up',
                    u'storageType': {u'instanceId': u'64702.1',
                                     u'instanceName':
                                     u'Assigned - Redundant - 2 MB',
                                     u'objectType': u'ScStorageType'},
                    u'cmmDestination': False,
                    u'replicationDestination': False,
                    u'volumeFolder': {u'instanceId': u'64702.17',
                                      u'instanceName': u'fcvm',
                                      u'objectType': u'ScVolumeFolder'},
                    u'deviceId': u'6000d31000fcbe000000000000000da8',
                    u'active': True,
                    u'portableVolumeDestination': False,
                    u'deleteAllowed': True,
                    u'name': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
                    u'scName': u'Storage Center 64702',
                    u'secureDataUsed': False,
                    u'serialNumber': u'0000fcbe-00000da8',
                    u'replayAllowed': True,
                    u'flashOptimized': False,
                    u'configuredSize': u'1.073741824E9 Bytes',
                    u'mapped': False,
                    u'cmmSource': False},
        {u'instanceId': u'64702.3495',
         u'scSerialNumber': 64702,
         u'replicationSource': False,
         u'liveVolume': False,
         u'vpdId': 3496,
         u'objectType': u'ScVolume',
         u'index': 3495,
         u'volumeFolderPath': u'devstackvol/fcvm/',
         u'hostCacheEnabled': False,
         u'usedByLegacyFluidFsNasVolume': False,
         u'inRecycleBin': False,
         u'volumeFolderIndex': 17,
         u'instanceName':
         u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
         u'statusMessage': u'',
         u'status': u'Up',
         u'storageType': {u'instanceId': u'64702.1',
                          u'instanceName':
                          u'Assigned - Redundant - 2 MB',
                          u'objectType': u'ScStorageType'},
         u'cmmDestination': False,
         u'replicationDestination': False,
         u'volumeFolder': {u'instanceId': u'64702.17',
                           u'instanceName': u'fcvm',
                           u'objectType': u'ScVolumeFolder'},
         u'deviceId': u'6000d31000fcbe000000000000000da9',
         u'active': True,
         u'portableVolumeDestination': False,
         u'deleteAllowed': True,
         u'name': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
         u'scName': u'Storage Center 64702',
         u'secureDataUsed': False,
         u'serialNumber': u'0000fcbe-00000da8',
         u'replayAllowed': True,
         u'flashOptimized': False,
         u'configuredSize': u'1.073741824E9 Bytes',
         u'mapped': False,
         u'cmmSource': False}]

    VOLUME_CONFIG = \
        {u'instanceId': u'64702.3494',
         u'scSerialNumber': 64702,
         u'maximumSiblingCount': 100,
         u'writeCacheStatus': u'Up',
         u'objectType': u'ScVolumeConfiguration',
         u'currentSiblingConfiguredSize': u'2.147483648E9 Bytes',
         u'compressionPaused': False,
         u'enforceConsumptionLimit': False,
         u'volumeSpaceConsumptionLimit': u'2.147483648E9 Bytes',
         u'readCacheEnabled': True,
         u'writeCacheEnabled': True,
         u'instanceName': u'volume-ff9589d3-2d41-48d5-9ef5-2713a875e85b',
         u'dateModified': u'04/03/2015 12:01:08 AM',
         u'modifyUser': u'Admin',
         u'replayExpirationPaused': False,
         u'currentSiblingCount': 1,
         u'replayCreationPaused': False,
         u'replayProfileList': [{u'instanceId': u'64702.2',
                                 u'instanceName': u'Daily',
                                 u'objectType': u'ScReplayProfile'}],
         u'dateCreated': u'04/04/2014 03:54:26 AM',
         u'volume': {u'instanceId': u'64702.3494',
                     u'instanceName':
                     u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
                     u'objectType': u'ScVolume'},
         u'controller': {u'instanceId': u'64702.64703',
                         u'instanceName': u'SN 64703',
                         u'objectType': u'ScController'},
         u'coalesceIntoActive': False,
         u'createUser': u'Admin',
         u'importToLowestTier': False,
         u'readCacheStatus': u'Up',
         u'maximumSiblingConfiguredSpace': u'5.49755813888E14 Bytes',
         u'storageProfile': {u'instanceId': u'64702.1',
                             u'instanceName': u'Recommended',
                             u'objectType': u'ScStorageProfile'},
         u'scName': u'Storage Center 64702',
         u'notes': u'',
         u'diskFolder': {u'instanceId': u'64702.3',
                         u'instanceName': u'Assigned',
                         u'objectType': u'ScDiskFolder'},
         u'openVmsUniqueDiskId': 48,
         u'compressionEnabled': False}

    INACTIVE_VOLUME = \
        {u'instanceId': u'64702.3494',
         u'scSerialNumber': 64702,
         u'replicationSource': False,
         u'liveVolume': False,
         u'vpdId': 3496,
         u'objectType': u'ScVolume',
         u'index': 3494,
         u'volumeFolderPath': u'devstackvol/fcvm/',
         u'hostCacheEnabled': False,
         u'usedByLegacyFluidFsNasVolume': False,
         u'inRecycleBin': False,
         u'volumeFolderIndex': 17,
         u'instanceName': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
         u'statusMessage': u'',
         u'status': u'Up',
         u'storageType': {u'instanceId': u'64702.1',
                          u'instanceName': u'Assigned - Redundant - 2 MB',
                          u'objectType': u'ScStorageType'},
         u'cmmDestination': False,
         u'replicationDestination': False,
         u'volumeFolder': {u'instanceId': u'64702.17',
                           u'instanceName': u'fcvm',
                           u'objectType': u'ScVolumeFolder'},
         u'deviceId': u'6000d31000fcbe000000000000000da8',
         u'active': False,
         u'portableVolumeDestination': False,
         u'deleteAllowed': True,
         u'name': u'volume-37883deb-85cd-426a-9a98-62eaad8671ea',
         u'scName': u'Storage Center 64702',
         u'secureDataUsed': False,
         u'serialNumber': u'0000fcbe-00000da8',
         u'replayAllowed': True,
         u'flashOptimized': False,
         u'configuredSize': u'1.073741824E9 Bytes',
         u'mapped': False,
         u'cmmSource': False}

    SCSERVER = {u'scName': u'Storage Center 64702',
                u'volumeCount': 0,
                u'removeHbasAllowed': True,
                u'legacyFluidFs': False,
                u'serverFolderIndex': 4,
                u'alertOnConnectivity': True,
                u'objectType': u'ScPhysicalServer',
                u'instanceName': u'Server_21000024ff30441d',
                u'instanceId': u'64702.47',
                u'serverFolderPath': u'devstacksrv/',
                u'portType': [u'FibreChannel'],
                u'type': u'Physical',
                u'statusMessage': u'Only 5 of 6 expected paths are up',
                u'status': u'Degraded',
                u'scSerialNumber': 64702,
                u'serverFolder': {u'instanceId': u'64702.4',
                                  u'instanceName': u'devstacksrv',
                                  u'objectType': u'ScServerFolder'},
                u'parentIndex': 0,
                u'connectivity': u'Partial',
                u'hostCacheIndex': 0,
                u'deleteAllowed': True,
                u'pathCount': 5,
                u'name': u'Server_21000024ff30441d',
                u'hbaPresent': True,
                u'hbaCount': 2,
                u'notes': u'Created by Dell Cinder Driver',
                u'mapped': False,
                u'operatingSystem': {u'instanceId': u'64702.38',
                                     u'instanceName': u'Red Hat Linux 6.x',
                                     u'objectType': u'ScServerOperatingSystem'}
                }

    # ScServer where deletedAllowed=False (not allowed to be deleted)
    SCSERVER_NO_DEL = {u'scName': u'Storage Center 64702',
                       u'volumeCount': 0,
                       u'removeHbasAllowed': True,
                       u'legacyFluidFs': False,
                       u'serverFolderIndex': 4,
                       u'alertOnConnectivity': True,
                       u'objectType': u'ScPhysicalServer',
                       u'instanceName': u'Server_21000024ff30441d',
                       u'instanceId': u'64702.47',
                       u'serverFolderPath': u'devstacksrv/',
                       u'portType': [u'FibreChannel'],
                       u'type': u'Physical',
                       u'statusMessage': u'Only 5 of 6 expected paths are up',
                       u'status': u'Degraded',
                       u'scSerialNumber': 64702,
                       u'serverFolder': {u'instanceId': u'64702.4',
                                         u'instanceName': u'devstacksrv',
                                         u'objectType': u'ScServerFolder'},
                       u'parentIndex': 0,
                       u'connectivity': u'Partial',
                       u'hostCacheIndex': 0,
                       u'deleteAllowed': False,
                       u'pathCount': 5,
                       u'name': u'Server_21000024ff30441d',
                       u'hbaPresent': True,
                       u'hbaCount': 2,
                       u'notes': u'Created by Dell Cinder Driver',
                       u'mapped': False,
                       u'operatingSystem':
                           {u'instanceId': u'64702.38',
                            u'instanceName': u'Red Hat Linux 6.x',
                            u'objectType': u'ScServerOperatingSystem'}
                       }

    SCSERVERS = [{u'scName': u'Storage Center 64702',
                  u'volumeCount': 5,
                  u'removeHbasAllowed': True,
                  u'legacyFluidFs': False,
                  u'serverFolderIndex': 0,
                  u'alertOnConnectivity': True,
                  u'objectType': u'ScPhysicalServer',
                  u'instanceName': u'openstack4',
                  u'instanceId': u'64702.1',
                  u'serverFolderPath': u'',
                  u'portType': [u'Iscsi'],
                  u'type': u'Physical',
                  u'statusMessage': u'',
                  u'status': u'Up',
                  u'scSerialNumber': 64702,
                  u'serverFolder': {u'instanceId': u'64702.0',
                                    u'instanceName': u'Servers',
                                    u'objectType': u'ScServerFolder'},
                  u'parentIndex': 0,
                  u'connectivity': u'Up',
                  u'hostCacheIndex': 0,
                  u'deleteAllowed': True,
                  u'pathCount': 0,
                  u'name': u'openstack4',
                  u'hbaPresent': True,
                  u'hbaCount': 1,
                  u'notes': u'',
                  u'mapped': True,
                  u'operatingSystem':
                      {u'instanceId': u'64702.3',
                       u'instanceName': u'Other Multipath',
                       u'objectType': u'ScServerOperatingSystem'}},
                 {u'scName': u'Storage Center 64702',
                  u'volumeCount': 1,
                  u'removeHbasAllowed': True,
                  u'legacyFluidFs': False,
                  u'serverFolderIndex': 0,
                  u'alertOnConnectivity': True,
                  u'objectType': u'ScPhysicalServer',
                  u'instanceName': u'openstack5',
                  u'instanceId': u'64702.2',
                  u'serverFolderPath': u'',
                  u'portType': [u'Iscsi'],
                  u'type': u'Physical',
                  u'statusMessage': u'',
                  u'status': u'Up',
                  u'scSerialNumber': 64702,
                  u'serverFolder': {u'instanceId': u'64702.0',
                                    u'instanceName': u'Servers',
                                    u'objectType': u'ScServerFolder'},
                  u'parentIndex': 0,
                  u'connectivity': u'Up',
                  u'hostCacheIndex': 0,
                  u'deleteAllowed': True,
                  u'pathCount': 0, u'name': u'openstack5',
                  u'hbaPresent': True,
                  u'hbaCount': 1,
                  u'notes': u'',
                  u'mapped': True,
                  u'operatingSystem':
                      {u'instanceId': u'64702.2',
                       u'instanceName': u'Other Singlepath',
                       u'objectType': u'ScServerOperatingSystem'}}]

    # ScServers list where status = Down
    SCSERVERS_DOWN = \
        [{u'scName': u'Storage Center 64702',
          u'volumeCount': 5,
          u'removeHbasAllowed': True,
          u'legacyFluidFs': False,
          u'serverFolderIndex': 0,
          u'alertOnConnectivity': True,
          u'objectType': u'ScPhysicalServer',
          u'instanceName': u'openstack4',
          u'instanceId': u'64702.1',
          u'serverFolderPath': u'',
          u'portType': [u'Iscsi'],
          u'type': u'Physical',
          u'statusMessage': u'',
          u'status': u'Down',
          u'scSerialNumber': 64702,
          u'serverFolder': {u'instanceId': u'64702.0',
                            u'instanceName': u'Servers',
                            u'objectType': u'ScServerFolder'},
          u'parentIndex': 0,
          u'connectivity': u'Up',
          u'hostCacheIndex': 0,
          u'deleteAllowed': True,
          u'pathCount': 0,
          u'name': u'openstack4',
          u'hbaPresent': True,
          u'hbaCount': 1,
          u'notes': u'',
          u'mapped': True,
          u'operatingSystem':
          {u'instanceId': u'64702.3',
           u'instanceName': u'Other Multipath',
           u'objectType': u'ScServerOperatingSystem'}}]

    MAP_PROFILE = {u'instanceId': u'64702.2941',
                   u'scName': u'Storage Center 64702',
                   u'scSerialNumber': 64702,
                   u'controller': {u'instanceId': u'64702.64703',
                                   u'instanceName': u'SN 64703',
                                   u'objectType': u'ScController'},
                   u'lunUsed': [1],
                   u'server': {u'instanceId': u'64702.47',
                               u'instanceName': u'Server_21000024ff30441d',
                               u'objectType': u'ScPhysicalServer'},
                   u'volume':
                       {u'instanceId': u'64702.6025',
                        u'instanceName': u'Server_21000024ff30441d Test Vol',
                        u'objectType': u'ScVolume'},
                   u'connectivity': u'Up',
                   u'readOnly': False,
                   u'objectType': u'ScMappingProfile',
                   u'hostCache': False,
                   u'mappedVia': u'Server',
                   u'mapCount': 3,
                   u'instanceName': u'6025-47',
                   u'lunRequested': u'N/A'}

    MAP_PROFILES = [MAP_PROFILE]

    MAPPINGS = [{u'profile': {u'instanceId': u'64702.104',
                              u'instanceName': u'92-30',
                              u'objectType': u'ScMappingProfile'},
                 u'status': u'Down',
                 u'statusMessage': u'',
                 u'instanceId': u'64702.969.64702',
                 u'scName': u'Storage Center 64702',
                 u'scSerialNumber': 64702,
                 u'controller': {u'instanceId': u'64702.64702',
                                 u'instanceName': u'SN 64702',
                                 u'objectType': u'ScController'},
                 u'server': {u'instanceId': u'64702.30',
                             u'instanceName':
                             u'Server_iqn.1993-08.org.debian:01:3776df826e4f',
                             u'objectType': u'ScPhysicalServer'},
                 u'volume': {u'instanceId': u'64702.92',
                             u'instanceName':
                             u'volume-74a21934-60ad-4cf2-b89b-1f0dda309ddf',
                             u'objectType': u'ScVolume'},
                 u'readOnly': False,
                 u'lun': 1,
                 u'lunUsed': [1],
                 u'serverHba': {u'instanceId': u'64702.3454975614',
                                u'instanceName':
                                u'iqn.1993-08.org.debian:01:3776df826e4f',
                                u'objectType': u'ScServerHba'},
                 u'path': {u'instanceId': u'64702.64702.64702.31.8',
                           u'instanceName':
                           u'iqn.1993-08.org.debian:'
                           '01:3776df826e4f-5000D31000FCBE43',
                           u'objectType': u'ScServerHbaPath'},
                 u'controllerPort': {u'instanceId':
                                     u'64702.5764839588723736131.91',
                                     u'instanceName': u'5000D31000FCBE43',
                                     u'objectType': u'ScControllerPort'},
                 u'instanceName': u'64702-969',
                 u'transport': u'Iscsi',
                 u'objectType': u'ScMapping'}]

    # Multiple mappings to test find_iscsi_properties with multiple portals
    MAPPINGS_MULTI_PORTAL = \
        [{u'profile': {u'instanceId': u'64702.104',
                       u'instanceName': u'92-30',
                       u'objectType': u'ScMappingProfile'},
          u'status': u'Down',
          u'statusMessage': u'',
          u'instanceId': u'64702.969.64702',
          u'scName': u'Storage Center 64702',
          u'scSerialNumber': 64702,
          u'controller': {u'instanceId': u'64702.64702',
                          u'instanceName': u'SN 64702',
                          u'objectType': u'ScController'},
          u'server': {u'instanceId': u'64702.30',
                      u'instanceName':
                      u'Server_iqn.1993-08.org.debian:01:3776df826e4f',
                      u'objectType': u'ScPhysicalServer'},
          u'volume': {u'instanceId': u'64702.92',
                      u'instanceName':
                      u'volume-74a21934-60ad-4cf2-b89b-1f0dda309ddf',
                      u'objectType': u'ScVolume'},
          u'readOnly': False,
          u'lun': 1,
          u'lunUsed': [1],
          u'serverHba': {u'instanceId': u'64702.3454975614',
                         u'instanceName':
                         u'iqn.1993-08.org.debian:01:3776df826e4f',
                         u'objectType': u'ScServerHba'},
          u'path': {u'instanceId': u'64702.64702.64702.31.8',
                    u'instanceName':
                    u'iqn.1993-08.org.debian:'
                    '01:3776df826e4f-5000D31000FCBE43',
                    u'objectType': u'ScServerHbaPath'},
          u'controllerPort': {u'instanceId':
                              u'64702.5764839588723736131.91',
                              u'instanceName': u'5000D31000FCBE43',
                              u'objectType': u'ScControllerPort'},
          u'instanceName': u'64702-969',
          u'transport': u'Iscsi',
          u'objectType': u'ScMapping'},
         {u'profile': {u'instanceId': u'64702.104',
                       u'instanceName': u'92-30',
                       u'objectType': u'ScMappingProfile'},
          u'status': u'Down',
          u'statusMessage': u'',
          u'instanceId': u'64702.969.64702',
          u'scName': u'Storage Center 64702',
          u'scSerialNumber': 64702,
          u'controller': {u'instanceId': u'64702.64702',
                          u'instanceName': u'SN 64702',
                          u'objectType': u'ScController'},
          u'server': {u'instanceId': u'64702.30',
                      u'instanceName':
                      u'Server_iqn.1993-08.org.debian:01:3776df826e4f',
                      u'objectType': u'ScPhysicalServer'},
          u'volume': {u'instanceId': u'64702.92',
                      u'instanceName':
                      u'volume-74a21934-60ad-4cf2-b89b-1f0dda309ddf',
                      u'objectType': u'ScVolume'},
          u'readOnly': False,
          u'lun': 1,
          u'lunUsed': [1],
          u'serverHba': {u'instanceId': u'64702.3454975614',
                         u'instanceName':
                         u'iqn.1993-08.org.debian:01:3776df826e4f',
                         u'objectType': u'ScServerHba'},
          u'path': {u'instanceId': u'64702.64702.64702.31.8',
                    u'instanceName':
                    u'iqn.1993-08.org.debian:'
                    '01:3776df826e4f-5000D31000FCBE43',
                    u'objectType': u'ScServerHbaPath'},
          u'controllerPort': {u'instanceId':
                              u'64702.5764839588723736131.91',
                              u'instanceName': u'5000D31000FCBE43',
                              u'objectType': u'ScControllerPort'},
          u'instanceName': u'64702-969',
          u'transport': u'Iscsi',
          u'objectType': u'ScMapping'}]

    MAPPINGS_READ_ONLY = \
        [{u'profile': {u'instanceId': u'64702.104',
                       u'instanceName': u'92-30',
                       u'objectType': u'ScMappingProfile'},
          u'status': u'Down',
          u'statusMessage': u'',
          u'instanceId': u'64702.969.64702',
          u'scName': u'Storage Center 64702',
          u'scSerialNumber': 64702,
          u'controller': {u'instanceId': u'64702.64702',
                          u'instanceName': u'SN 64702',
                                           u'objectType': u'ScController'},
          u'server': {u'instanceId': u'64702.30',
                      u'instanceName':
                      u'Server_iqn.1993-08.org.debian:01:3776df826e4f',
                      u'objectType': u'ScPhysicalServer'},
          u'volume': {u'instanceId': u'64702.92',
                      u'instanceName':
                      u'volume-74a21934-60ad-4cf2-b89b-1f0dda309ddf',
                      u'objectType': u'ScVolume'},
          u'readOnly': True,
          u'lun': 1,
          u'lunUsed': [1],
          u'serverHba': {u'instanceId': u'64702.3454975614',
                         u'instanceName':
                         u'iqn.1993-08.org.debian:01:3776df826e4f',
                         u'objectType': u'ScServerHba'},
          u'path': {u'instanceId': u'64702.64702.64702.31.8',
                    u'instanceName':
                    u'iqn.1993-08.org.debian:'
                    '01:3776df826e4f-5000D31000FCBE43',
                    u'objectType': u'ScServerHbaPath'},
          u'controllerPort': {u'instanceId':
                              u'64702.5764839588723736131.91',
                              u'instanceName':
                              u'5000D31000FCBE43',
                              u'objectType': u'ScControllerPort'},
          u'instanceName': u'64702-969',
                           u'transport': u'Iscsi',
                           u'objectType': u'ScMapping'}]

    FC_MAPPINGS = [{u'profile': {u'instanceId': u'64702.2941',
                                 u'instanceName': u'6025-47',
                                 u'objectType': u'ScMappingProfile'},
                    u'status': u'Up',
                    u'statusMessage': u'',
                    u'instanceId': u'64702.7639.64702',
                    u'scName': u'Storage Center 64702',
                    u'scSerialNumber': 64702,
                    u'controller': {u'instanceId': u'64702.64703',
                                    u'instanceName': u'SN 64703',
                                    u'objectType': u'ScController'},
                    u'server': {u'instanceId': u'64702.47',
                                u'instanceName': u'Server_21000024ff30441d',
                                u'objectType': u'ScPhysicalServer'},
                    u'volume': {u'instanceId': u'64702.6025',
                                u'instanceName':
                                    u'Server_21000024ff30441d Test Vol',
                                u'objectType': u'ScVolume'},
                    u'readOnly': False,
                    u'lun': 1,
                    u'serverHba': {u'instanceId': u'64702.3282218607',
                                   u'instanceName': u'21000024FF30441C',
                                   u'objectType': u'ScServerHba'},
                    u'path': {u'instanceId': u'64702.64702.64703.27.73',
                              u'instanceName':
                                  u'21000024FF30441C-5000D31000FCBE36',
                              u'objectType': u'ScServerHbaPath'},
                    u'controllerPort':
                        {u'instanceId': u'64702.5764839588723736118.50',
                         u'instanceName': u'5000D31000FCBE36',
                         u'objectType': u'ScControllerPort'},
                    u'instanceName': u'64702-7639',
                    u'transport': u'FibreChannel',
                    u'objectType': u'ScMapping'},
                   {u'profile': {u'instanceId': u'64702.2941',
                                 u'instanceName': u'6025-47',
                                 u'objectType': u'ScMappingProfile'},
                    u'status': u'Up',
                    u'statusMessage': u'',
                    u'instanceId': u'64702.7640.64702',
                    u'scName': u'Storage Center 64702',
                    u'scSerialNumber': 64702,
                    u'controller': {u'instanceId': u'64702.64703',
                                    u'instanceName': u'SN 64703',
                                    u'objectType': u'ScController'},
                    u'server': {u'instanceId': u'64702.47',
                                u'instanceName': u'Server_21000024ff30441d',
                                u'objectType': u'ScPhysicalServer'},
                    u'volume':
                        {u'instanceId': u'64702.6025',
                         u'instanceName': u'Server_21000024ff30441d Test Vol',
                         u'objectType': u'ScVolume'},
                    u'readOnly': False,
                    u'lun': 1,
                    u'serverHba': {u'instanceId': u'64702.3282218606',
                                   u'instanceName': u'21000024FF30441D',
                                   u'objectType': u'ScServerHba'},
                    u'path':
                    {u'instanceId': u'64702.64702.64703.27.78',
                       u'instanceName': u'21000024FF30441D-5000D31000FCBE36',
                       u'objectType': u'ScServerHbaPath'},
                    u'controllerPort':
                        {u'instanceId': u'64702.5764839588723736118.50',
                         u'instanceName': u'5000D31000FCBE36',
                         u'objectType': u'ScControllerPort'},
                    u'instanceName': u'64702-7640',
                    u'transport': u'FibreChannel',
                    u'objectType': u'ScMapping'},
                   {u'profile': {u'instanceId': u'64702.2941',
                                 u'instanceName': u'6025-47',
                                 u'objectType': u'ScMappingProfile'},
                    u'status': u'Up',
                    u'statusMessage': u'',
                    u'instanceId': u'64702.7638.64702',
                    u'scName': u'Storage Center 64702',
                    u'scSerialNumber': 64702,
                    u'controller': {u'instanceId': u'64702.64703',
                                    u'instanceName': u'SN 64703',
                                    u'objectType': u'ScController'},
                    u'server': {u'instanceId': u'64702.47',
                                u'instanceName': u'Server_21000024ff30441d',
                                u'objectType': u'ScPhysicalServer'},
                    u'volume': {u'instanceId': u'64702.6025',
                                u'instanceName':
                                    u'Server_21000024ff30441d Test Vol',
                                u'objectType': u'ScVolume'},
                    u'readOnly': False,
                    u'lun': 1,
                    u'serverHba': {u'instanceId': u'64702.3282218606',
                                   u'instanceName': u'21000024FF30441D',
                                   u'objectType': u'ScServerHba'},
                    u'path':
                        {u'instanceId': u'64702.64702.64703.28.76',
                         u'instanceName': u'21000024FF30441D-5000D31000FCBE3E',
                         u'objectType': u'ScServerHbaPath'},
                    u'controllerPort': {u'instanceId':
                                        u'64702.5764839588723736126.60',
                                        u'instanceName': u'5000D31000FCBE3E',
                                        u'objectType': u'ScControllerPort'},
                    u'instanceName': u'64702-7638',
                    u'transport': u'FibreChannel',
                    u'objectType': u'ScMapping'}]

    FC_MAPPINGS_LUN_MISMATCH = \
        [{u'profile': {u'instanceId': u'64702.2941',
                       u'instanceName': u'6025-47',
                       u'objectType': u'ScMappingProfile'},
          u'status': u'Up',
          u'statusMessage': u'',
          u'instanceId': u'64702.7639.64702',
          u'scName': u'Storage Center 64702',
          u'scSerialNumber': 64702,
          u'controller': {u'instanceId': u'64702.64703',
                          u'instanceName': u'SN 64703',
                          u'objectType': u'ScController'},
          u'server': {u'instanceId': u'64702.47',
                      u'instanceName': u'Server_21000024ff30441d',
                      u'objectType': u'ScPhysicalServer'},
          u'volume': {u'instanceId': u'64702.6025',
                      u'instanceName':
                      u'Server_21000024ff30441d Test Vol',
                      u'objectType': u'ScVolume'},
          u'readOnly': False,
          u'lun': 1,
          u'serverHba': {u'instanceId': u'64702.3282218607',
                         u'instanceName': u'21000024FF30441C',
                         u'objectType': u'ScServerHba'},
          u'path': {u'instanceId': u'64702.64702.64703.27.73',
                    u'instanceName':
                    u'21000024FF30441C-5000D31000FCBE36',
                    u'objectType': u'ScServerHbaPath'},
          u'controllerPort':
          {u'instanceId': u'64702.5764839588723736118.50',
           u'instanceName': u'5000D31000FCBE36',
           u'objectType': u'ScControllerPort'},
          u'instanceName': u'64702-7639',
          u'transport': u'FibreChannel',
          u'objectType': u'ScMapping'},
         {u'profile': {u'instanceId': u'64702.2941',
                       u'instanceName': u'6025-47',
                       u'objectType': u'ScMappingProfile'},
          u'status': u'Up',
          u'statusMessage': u'',
          u'instanceId': u'64702.7640.64702',
          u'scName': u'Storage Center 64702',
          u'scSerialNumber': 64702,
          u'controller': {u'instanceId': u'64702.64703',
                          u'instanceName': u'SN 64703',
                          u'objectType': u'ScController'},
          u'server': {u'instanceId': u'64702.47',
                      u'instanceName': u'Server_21000024ff30441d',
                      u'objectType': u'ScPhysicalServer'},
          u'volume':
          {u'instanceId': u'64702.6025',
           u'instanceName': u'Server_21000024ff30441d Test Vol',
           u'objectType': u'ScVolume'},
          u'readOnly': False,
          u'lun': 1,
          u'serverHba': {u'instanceId': u'64702.3282218606',
                         u'instanceName': u'21000024FF30441D',
                         u'objectType': u'ScServerHba'},
          u'path':
          {u'instanceId': u'64702.64702.64703.27.78',
           u'instanceName': u'21000024FF30441D-5000D31000FCBE36',
           u'objectType': u'ScServerHbaPath'},
          u'controllerPort':
          {u'instanceId': u'64702.5764839588723736118.50',
           u'instanceName': u'5000D31000FCBE36',
           u'objectType': u'ScControllerPort'},
          u'instanceName': u'64702-7640',
          u'transport': u'FibreChannel',
          u'objectType': u'ScMapping'},
            {u'profile': {u'instanceId': u'64702.2941',
                          u'instanceName': u'6025-47',
                          u'objectType': u'ScMappingProfile'},
             u'status': u'Up',
             u'statusMessage': u'',
             u'instanceId': u'64702.7638.64702',
             u'scName': u'Storage Center 64702',
             u'scSerialNumber': 64702,
             u'controller': {u'instanceId': u'64702.64703',
                             u'instanceName': u'SN 64703',
                             u'objectType': u'ScController'},
             u'server': {u'instanceId': u'64702.47',
                         u'instanceName': u'Server_21000024ff30441d',
                         u'objectType': u'ScPhysicalServer'},
             u'volume': {u'instanceId': u'64702.6025',
                         u'instanceName':
                         u'Server_21000024ff30441d Test Vol',
                         u'objectType': u'ScVolume'},
             u'readOnly': False,
             u'lun': 2,
             u'serverHba': {u'instanceId': u'64702.3282218606',
                            u'instanceName': u'21000024FF30441D',
                            u'objectType': u'ScServerHba'},
             u'path':
                        {u'instanceId': u'64702.64702.64703.28.76',
                         u'instanceName': u'21000024FF30441D-5000D31000FCBE3E',
                         u'objectType': u'ScServerHbaPath'},
             u'controllerPort': {u'instanceId':
                                 u'64702.5764839588723736126.60',
                                 u'instanceName': u'5000D31000FCBE3E',
                                 u'objectType': u'ScControllerPort'},
             u'instanceName': u'64702-7638',
             u'transport': u'FibreChannel',
             u'objectType': u'ScMapping'}]

    RPLAY = {u'scSerialNumber': 64702,
             u'globalIndex': u'64702-46-250',
             u'description': u'Cinder Clone Replay',
             u'parent': {u'instanceId': u'64702.46.249',
                         u'instanceName': u'64702-46-249',
                         u'objectType': u'ScReplay'},
             u'instanceId': u'64702.46.250',
             u'scName': u'Storage Center 64702',
             u'consistent': False,
             u'expires': True,
             u'freezeTime': u'12/09/2014 03:52:08 PM',
             u'createVolume': {u'instanceId': u'64702.46',
                               u'instanceName':
                               u'volume-ff9589d3-2d41-48d5-9ef5-2713a875e85b',
                               u'objectType': u'ScVolume'},
             u'expireTime': u'12/09/2014 04:52:08 PM',
             u'source': u'Manual',
             u'spaceRecovery': False,
             u'writesHeldDuration': 7910,
             u'active': False,
             u'markedForExpiration': False,
             u'objectType': u'ScReplay',
             u'instanceName': u'12/09/2014 03:52:08 PM',
             u'size': u'0.0 Bytes'
             }

    RPLAYS = [{u'scSerialNumber': 64702,
               u'globalIndex': u'64702-6025-5',
               u'description': u'Manually Created',
               u'parent': {u'instanceId': u'64702.6025.4',
                           u'instanceName': u'64702-6025-4',
                           u'objectType': u'ScReplay'},
               u'instanceId': u'64702.6025.5',
               u'scName': u'Storage Center 64702',
               u'consistent': False,
               u'expires': True,
               u'freezeTime': u'02/02/2015 08:23:55 PM',
               u'createVolume': {u'instanceId': u'64702.6025',
                                 u'instanceName':
                                     u'Server_21000024ff30441d Test Vol',
                                 u'objectType': u'ScVolume'},
               u'expireTime': u'02/02/2015 09:23:55 PM',
               u'source': u'Manual',
               u'spaceRecovery': False,
               u'writesHeldDuration': 7889,
               u'active': False,
               u'markedForExpiration': False,
               u'objectType': u'ScReplay',
               u'instanceName': u'02/02/2015 08:23:55 PM',
               u'size': u'0.0 Bytes'},
              {u'scSerialNumber': 64702,
               u'globalIndex': u'64702-6025-4',
               u'description': u'Cinder Test Replay012345678910',
               u'parent': {u'instanceId': u'64702.6025.3',
                           u'instanceName': u'64702-6025-3',
                           u'objectType': u'ScReplay'},
               u'instanceId': u'64702.6025.4',
               u'scName': u'Storage Center 64702',
               u'consistent': False,
               u'expires': True,
               u'freezeTime': u'02/02/2015 08:23:47 PM',
               u'createVolume': {u'instanceId': u'64702.6025',
                                 u'instanceName':
                                     u'Server_21000024ff30441d Test Vol',
                                 u'objectType': u'ScVolume'},
               u'expireTime': u'02/02/2015 09:23:47 PM',
               u'source': u'Manual',
               u'spaceRecovery': False,
               u'writesHeldDuration': 7869,
               u'active': False,
               u'markedForExpiration': False,
               u'objectType': u'ScReplay',
               u'instanceName': u'02/02/2015 08:23:47 PM',
               u'size': u'0.0 Bytes'}]

    TST_RPLAY = {u'scSerialNumber': 64702,
                 u'globalIndex': u'64702-6025-4',
                 u'description': u'Cinder Test Replay012345678910',
                 u'parent': {u'instanceId': u'64702.6025.3',
                             u'instanceName': u'64702-6025-3',
                             u'objectType': u'ScReplay'},
                 u'instanceId': u'64702.6025.4',
                 u'scName': u'Storage Center 64702',
                 u'consistent': False,
                 u'expires': True,
                 u'freezeTime': u'02/02/2015 08:23:47 PM',
                 u'createVolume': {u'instanceId': u'64702.6025',
                                   u'instanceName':
                                       u'Server_21000024ff30441d Test Vol',
                                   u'objectType': u'ScVolume'},
                 u'expireTime': u'02/02/2015 09:23:47 PM',
                 u'source': u'Manual',
                 u'spaceRecovery': False,
                 u'writesHeldDuration': 7869,
                 u'active': False,
                 u'markedForExpiration': False,
                 u'objectType': u'ScReplay',
                 u'instanceName': u'02/02/2015 08:23:47 PM',
                 u'size': u'0.0 Bytes'}

    FLDR = {u'status': u'Up',
            u'instanceName': u'opnstktst',
            u'name': u'opnstktst',
            u'parent':
                {u'instanceId': u'64702.0',
                 u'instanceName': u'Volumes',
                 u'objectType': u'ScVolumeFolder'},
            u'instanceId': u'64702.43',
            u'scName': u'Storage Center 64702',
            u'notes': u'Folder for OpenStack Cinder Driver',
            u'scSerialNumber': 64702,
            u'parentIndex': 0,
            u'okToDelete': True,
            u'folderPath': u'',
            u'root': False,
            u'statusMessage': u'',
            u'objectType': u'ScVolumeFolder'}

    SVR_FLDR = {u'status': u'Up',
                u'instanceName': u'devstacksrv',
                u'name': u'devstacksrv',
                u'parent': {u'instanceId': u'64702.0',
                            u'instanceName': u'Servers',
                            u'objectType': u'ScServerFolder'},
                u'instanceId': u'64702.4',
                u'scName': u'Storage Center 64702',
                u'notes': u'Folder for OpenStack Cinder Driver',
                u'scSerialNumber': 64702,
                u'parentIndex': 0,
                u'okToDelete': False,
                u'folderPath': u'',
                u'root': False,
                u'statusMessage': u'',
                u'objectType': u'ScServerFolder'}

    ISCSI_HBA = {u'portWwnList': [],
                 u'iscsiIpAddress': u'0.0.0.0',
                 u'pathCount': 1,
                 u'name': u'iqn.1993-08.org.debian:01:52332b70525',
                 u'connectivity': u'Down',
                 u'instanceId': u'64702.3786433166',
                 u'scName': u'Storage Center 64702',
                 u'notes': u'',
                 u'scSerialNumber': 64702,
                 u'server':
                     {u'instanceId': u'64702.38',
                      u'instanceName':
                          u'Server_iqn.1993-08.org.debian:01:52332b70525',
                      u'objectType': u'ScPhysicalServer'},
                 u'remoteStorageCenter': False,
                 u'iscsiName': u'',
                 u'portType': u'Iscsi',
                 u'instanceName': u'iqn.1993-08.org.debian:01:52332b70525',
                 u'objectType': u'ScServerHba'}

    FC_HBAS = [{u'portWwnList': [],
                u'iscsiIpAddress': u'0.0.0.0',
                u'pathCount': 2,
                u'name': u'21000024FF30441C',
                u'connectivity': u'Up',
                u'instanceId': u'64702.3282218607',
                u'scName': u'Storage Center 64702',
                u'notes': u'',
                u'scSerialNumber': 64702,
                u'server': {u'instanceId': u'64702.47',
                            u'instanceName': u'Server_21000024ff30441d',
                            u'objectType': u'ScPhysicalServer'},
                u'remoteStorageCenter': False,
                u'iscsiName': u'',
                u'portType': u'FibreChannel',
                u'instanceName': u'21000024FF30441C',
                u'objectType': u'ScServerHba'},
               {u'portWwnList': [],
                u'iscsiIpAddress': u'0.0.0.0',
                u'pathCount': 3,
                u'name': u'21000024FF30441D',
                u'connectivity': u'Partial',
                u'instanceId': u'64702.3282218606',
                u'scName': u'Storage Center 64702',
                u'notes': u'',
                u'scSerialNumber': 64702,
                u'server': {u'instanceId': u'64702.47',
                            u'instanceName': u'Server_21000024ff30441d',
                            u'objectType': u'ScPhysicalServer'},
                u'remoteStorageCenter': False,
                u'iscsiName': u'',
                u'portType': u'FibreChannel',
                u'instanceName': u'21000024FF30441D',
                u'objectType': u'ScServerHba'}]

    FC_HBA = {u'portWwnList': [],
              u'iscsiIpAddress': u'0.0.0.0',
              u'pathCount': 3,
              u'name': u'21000024FF30441D',
              u'connectivity': u'Partial',
              u'instanceId': u'64702.3282218606',
              u'scName': u'Storage Center 64702',
              u'notes': u'',
              u'scSerialNumber': 64702,
              u'server': {u'instanceId': u'64702.47',
                          u'instanceName': u'Server_21000024ff30441d',
                          u'objectType': u'ScPhysicalServer'},
              u'remoteStorageCenter': False,
              u'iscsiName': u'',
              u'portType': u'FibreChannel',
              u'instanceName': u'21000024FF30441D',
              u'objectType': u'ScServerHba'}

    SVR_OS_S = [{u'allowsLunGaps': True,
                 u'product': u'Red Hat Linux',
                 u'supportsActiveMappingDeletion': True,
                 u'version': u'6.x',
                 u'requiresLunZero': False,
                 u'scName': u'Storage Center 64702',
                 u'virtualMachineGuest': True,
                 u'virtualMachineHost': False,
                 u'allowsCrossTransportMapping': False,
                 u'objectType': u'ScServerOperatingSystem',
                 u'instanceId': u'64702.38',
                 u'lunCanVaryAcrossPaths': False,
                 u'scSerialNumber': 64702,
                 u'maximumVolumeSize': u'0.0 Bytes',
                 u'multipath': True,
                 u'instanceName': u'Red Hat Linux 6.x',
                 u'supportsActiveMappingCreation': True,
                 u'name': u'Red Hat Linux 6.x'}]

    ISCSI_FLT_DOMAINS = [{u'headerDigestEnabled': False,
                          u'classOfServicePriority': 0,
                          u'wellKnownIpAddress': u'192.168.0.21',
                          u'scSerialNumber': 64702,
                          u'iscsiName':
                          u'iqn.2002-03.com.compellent:5000d31000fcbe42',
                          u'portNumber': 3260,
                          u'subnetMask': u'255.255.255.0',
                          u'gateway': u'192.168.0.1',
                          u'objectType': u'ScIscsiFaultDomain',
                          u'chapEnabled': False,
                          u'instanceId': u'64702.6.5.3',
                          u'childStatus': u'Up',
                          u'defaultTimeToRetain': u'SECONDS_20',
                          u'dataDigestEnabled': False,
                          u'instanceName': u'iSCSI 10G 2',
                          u'statusMessage': u'',
                          u'status': u'Up',
                          u'transportType': u'Iscsi',
                          u'vlanId': 0,
                          u'windowSize': u'131072.0 Bytes',
                          u'defaultTimeToWait': u'SECONDS_2',
                          u'scsiCommandTimeout': u'MINUTES_1',
                          u'deleteAllowed': False,
                          u'name': u'iSCSI 10G 2',
                          u'immediateDataWriteEnabled': False,
                          u'scName': u'Storage Center 64702',
                          u'notes': u'',
                          u'mtu': u'MTU_1500',
                          u'bidirectionalChapSecret': u'',
                          u'keepAliveTimeout': u'SECONDS_30'}]

    # For testing find_iscsi_properties where multiple portals are found
    ISCSI_FLT_DOMAINS_MULTI_PORTALS = \
        [{u'headerDigestEnabled': False,
          u'classOfServicePriority': 0,
          u'wellKnownIpAddress': u'192.168.0.21',
          u'scSerialNumber': 64702,
          u'iscsiName':
          u'iqn.2002-03.com.compellent:5000d31000fcbe42',
          u'portNumber': 3260,
          u'subnetMask': u'255.255.255.0',
          u'gateway': u'192.168.0.1',
          u'objectType': u'ScIscsiFaultDomain',
          u'chapEnabled': False,
          u'instanceId': u'64702.6.5.3',
          u'childStatus': u'Up',
          u'defaultTimeToRetain': u'SECONDS_20',
          u'dataDigestEnabled': False,
          u'instanceName': u'iSCSI 10G 2',
          u'statusMessage': u'',
          u'status': u'Up',
          u'transportType': u'Iscsi',
          u'vlanId': 0,
          u'windowSize': u'131072.0 Bytes',
          u'defaultTimeToWait': u'SECONDS_2',
          u'scsiCommandTimeout': u'MINUTES_1',
          u'deleteAllowed': False,
          u'name': u'iSCSI 10G 2',
          u'immediateDataWriteEnabled': False,
          u'scName': u'Storage Center 64702',
          u'notes': u'',
          u'mtu': u'MTU_1500',
          u'bidirectionalChapSecret': u'',
          u'keepAliveTimeout': u'SECONDS_30'},
         {u'headerDigestEnabled': False,
          u'classOfServicePriority': 0,
          u'wellKnownIpAddress': u'192.168.0.25',
          u'scSerialNumber': 64702,
          u'iscsiName':
          u'iqn.2002-03.com.compellent:5000d31000fcbe42',
          u'portNumber': 3260,
          u'subnetMask': u'255.255.255.0',
          u'gateway': u'192.168.0.1',
          u'objectType': u'ScIscsiFaultDomain',
          u'chapEnabled': False,
          u'instanceId': u'64702.6.5.3',
          u'childStatus': u'Up',
          u'defaultTimeToRetain': u'SECONDS_20',
          u'dataDigestEnabled': False,
          u'instanceName': u'iSCSI 10G 2',
          u'statusMessage': u'',
          u'status': u'Up',
          u'transportType': u'Iscsi',
          u'vlanId': 0,
          u'windowSize': u'131072.0 Bytes',
          u'defaultTimeToWait': u'SECONDS_2',
          u'scsiCommandTimeout': u'MINUTES_1',
          u'deleteAllowed': False,
          u'name': u'iSCSI 10G 2',
          u'immediateDataWriteEnabled': False,
          u'scName': u'Storage Center 64702',
          u'notes': u'',
          u'mtu': u'MTU_1500',
          u'bidirectionalChapSecret': u'',
          u'keepAliveTimeout': u'SECONDS_30'}]

    ISCSI_FLT_DOMAIN = {u'headerDigestEnabled': False,
                        u'classOfServicePriority': 0,
                        u'wellKnownIpAddress': u'192.168.0.21',
                        u'scSerialNumber': 64702,
                        u'iscsiName':
                            u'iqn.2002-03.com.compellent:5000d31000fcbe42',
                        u'portNumber': 3260,
                        u'subnetMask': u'255.255.255.0',
                        u'gateway': u'192.168.0.1',
                        u'objectType': u'ScIscsiFaultDomain',
                        u'chapEnabled': False,
                        u'instanceId': u'64702.6.5.3',
                        u'childStatus': u'Up',
                        u'defaultTimeToRetain': u'SECONDS_20',
                        u'dataDigestEnabled': False,
                        u'instanceName': u'iSCSI 10G 2',
                        u'statusMessage': u'',
                        u'status': u'Up',
                        u'transportType': u'Iscsi',
                        u'vlanId': 0,
                        u'windowSize': u'131072.0 Bytes',
                        u'defaultTimeToWait': u'SECONDS_2',
                        u'scsiCommandTimeout': u'MINUTES_1',
                        u'deleteAllowed': False,
                        u'name': u'iSCSI 10G 2',
                        u'immediateDataWriteEnabled': False,
                        u'scName': u'Storage Center 64702',
                        u'notes': u'',
                        u'mtu': u'MTU_1500',
                        u'bidirectionalChapSecret': u'',
                        u'keepAliveTimeout': u'SECONDS_30'}

    CTRLR_PORT = {u'status': u'Up',
                  u'iscsiIpAddress': u'0.0.0.0',
                  u'WWN': u'5000D31000FCBE06',
                  u'name': u'5000D31000FCBE06',
                  u'iscsiGateway': u'0.0.0.0',
                  u'instanceId': u'64702.5764839588723736070.51',
                  u'scName': u'Storage Center 64702',
                  u'scSerialNumber': 64702,
                  u'transportType': u'FibreChannel',
                  u'virtual': False,
                  u'controller': {u'instanceId': u'64702.64702',
                                  u'instanceName': u'SN 64702',
                                  u'objectType': u'ScController'},
                  u'iscsiName': u'',
                  u'purpose': u'FrontEnd',
                  u'iscsiSubnetMask': u'0.0.0.0',
                  u'faultDomain':
                      {u'instanceId': u'64702.4.3',
                       u'instanceName': u'Domain 1',
                       u'objectType': u'ScControllerPortFaultDomain'},
                  u'instanceName': u'5000D31000FCBE06',
                  u'statusMessage': u'',
                  u'objectType': u'ScControllerPort'}

    ISCSI_CTRLR_PORT = {u'preferredParent':
                        {u'instanceId': u'64702.5764839588723736074.69',
                         u'instanceName': u'5000D31000FCBE0A',
                         u'objectType': u'ScControllerPort'},
                        u'status': u'Up',
                        u'iscsiIpAddress': u'10.23.8.235',
                        u'WWN': u'5000D31000FCBE43',
                        u'name': u'5000D31000FCBE43',
                        u'parent':
                            {u'instanceId': u'64702.5764839588723736074.69',
                             u'instanceName': u'5000D31000FCBE0A',
                             u'objectType': u'ScControllerPort'},
                        u'iscsiGateway': u'0.0.0.0',
                        u'instanceId': u'64702.5764839588723736131.91',
                        u'scName': u'Storage Center 64702',
                        u'scSerialNumber': 64702,
                        u'transportType': u'Iscsi',
                        u'virtual': True,
                        u'controller': {u'instanceId': u'64702.64702',
                                        u'instanceName': u'SN 64702',
                                        u'objectType': u'ScController'},
                        u'iscsiName':
                            u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                        u'purpose': u'FrontEnd',
                        u'iscsiSubnetMask': u'0.0.0.0',
                        u'faultDomain':
                            {u'instanceId': u'64702.6.5',
                             u'instanceName': u'iSCSI 10G 2',
                             u'objectType': u'ScControllerPortFaultDomain'},
                        u'instanceName': u'5000D31000FCBE43',
                        u'childStatus': u'Up',
                        u'statusMessage': u'',
                        u'objectType': u'ScControllerPort'}

    FC_CTRLR_PORT = {u'preferredParent':
                     {u'instanceId': u'64702.5764839588723736093.57',
                         u'instanceName': u'5000D31000FCBE1D',
                                          u'objectType': u'ScControllerPort'},
                     u'status': u'Up',
                     u'iscsiIpAddress': u'0.0.0.0',
                     u'WWN': u'5000D31000FCBE36',
                     u'name': u'5000D31000FCBE36',
                     u'parent':
                         {u'instanceId': u'64702.5764839588723736093.57',
                             u'instanceName': u'5000D31000FCBE1D',
                          u'objectType': u'ScControllerPort'},
                     u'iscsiGateway': u'0.0.0.0',
                     u'instanceId': u'64702.5764839588723736118.50',
                     u'scName': u'Storage Center 64702',
                     u'scSerialNumber': 64702,
                     u'transportType': u'FibreChannel',
                     u'virtual': True,
                     u'controller': {u'instanceId': u'64702.64703',
                                     u'instanceName': u'SN 64703',
                                     u'objectType': u'ScController'},
                     u'iscsiName': u'',
                     u'purpose': u'FrontEnd',
                     u'iscsiSubnetMask': u'0.0.0.0',
                     u'faultDomain':
                         {u'instanceId': u'64702.1.0',
                          u'instanceName': u'Domain 0',
                          u'objectType': u'ScControllerPortFaultDomain'},
                     u'instanceName': u'5000D31000FCBE36',
                     u'childStatus': u'Up',
                     u'statusMessage': u'',
                     u'objectType': u'ScControllerPort'}

    FC_CTRLR_PORT_WWN_ERROR = \
        {u'preferredParent':
         {u'instanceId': u'64702.5764839588723736093.57',
          u'instanceName': u'5000D31000FCBE1D',
          u'objectType': u'ScControllerPort'},
         u'status': u'Up',
         u'iscsiIpAddress': u'0.0.0.0',
         u'Wwn': u'5000D31000FCBE36',
         u'name': u'5000D31000FCBE36',
         u'parent':
         {u'instanceId': u'64702.5764839588723736093.57',
          u'instanceName': u'5000D31000FCBE1D',
          u'objectType': u'ScControllerPort'},
         u'iscsiGateway': u'0.0.0.0',
         u'instanceId': u'64702.5764839588723736118.50',
         u'scName': u'Storage Center 64702',
         u'scSerialNumber': 64702,
         u'transportType': u'FibreChannel',
         u'virtual': True,
         u'controller': {u'instanceId': u'64702.64703',
                         u'instanceName': u'SN 64703',
                         u'objectType': u'ScController'},
         u'iscsiName': u'',
         u'purpose': u'FrontEnd',
         u'iscsiSubnetMask': u'0.0.0.0',
         u'faultDomain':
         {u'instanceId': u'64702.1.0',
          u'instanceName': u'Domain 0',
          u'objectType': u'ScControllerPortFaultDomain'},
         u'instanceName': u'5000D31000FCBE36',
         u'childStatus': u'Up',
         u'statusMessage': u'',
         u'objectType': u'ScControllerPort'}

    STRG_USAGE = {u'systemSpace': u'7.38197504E8 Bytes',
                  u'freeSpace': u'1.297659461632E13 Bytes',
                  u'oversubscribedSpace': u'0.0 Bytes',
                  u'instanceId': u'64702',
                  u'scName': u'Storage Center 64702',
                  u'savingVsRaidTen': u'1.13737990144E11 Bytes',
                  u'allocatedSpace': u'1.66791217152E12 Bytes',
                  u'usedSpace': u'3.25716017152E11 Bytes',
                  u'configuredSpace': u'9.155796533248E12 Bytes',
                  u'alertThresholdSpace': u'1.197207956992E13 Bytes',
                  u'availableSpace': u'1.3302310633472E13 Bytes',
                  u'badSpace': u'0.0 Bytes',
                  u'time': u'02/02/2015 02:23:39 PM',
                  u'scSerialNumber': 64702,
                  u'instanceName': u'Storage Center 64702',
                  u'storageAlertThreshold': 10,
                  u'objectType': u'StorageCenterStorageUsage'}

    RPLAY_PROFILE = {u'name': u'fc8f2fec-fab2-4e34-9148-c094c913b9a3',
                     u'type': u'Consistent',
                     u'notes': u'Created by Dell Cinder Driver',
                     u'volumeCount': 0,
                     u'expireIncompleteReplaySets': True,
                     u'replayCreationTimeout': 20,
                     u'enforceReplayCreationTimeout': False,
                     u'ruleCount': 0,
                     u'userCreated': True,
                     u'scSerialNumber': 64702,
                     u'scName': u'Storage Center 64702',
                     u'objectType': u'ScReplayProfile',
                     u'instanceId': u'64702.11',
                     u'instanceName': u'fc8f2fec-fab2-4e34-9148-c094c913b9a3'}
    STORAGE_PROFILE_LIST = [
        {u'allowedForFlashOptimized': False,
         u'allowedForNonFlashOptimized': True,
         u'index': 1,
         u'instanceId': u'64158.1',
         u'instanceName': u'Recommended',
         u'name': u'Recommended',
         u'notes': u'',
         u'objectType': u'ScStorageProfile',
         u'raidTypeDescription': u'RAID 10 Active, RAID 5 or RAID 6 Replay',
         u'raidTypeUsed': u'Mixed',
         u'scName': u'Storage Center 64158',
         u'scSerialNumber': 64158,
         u'tiersUsedDescription': u'Tier 1, Tier 2, Tier 3',
         u'useTier1Storage': True,
         u'useTier2Storage': True,
         u'useTier3Storage': True,
         u'userCreated': False,
         u'volumeCount': 125},
        {u'allowedForFlashOptimized': False,
         u'allowedForNonFlashOptimized': True,
         u'index': 2,
         u'instanceId': u'64158.2',
         u'instanceName': u'High Priority',
         u'name': u'High Priority',
         u'notes': u'',
         u'objectType': u'ScStorageProfile',
         u'raidTypeDescription': u'RAID 10 Active, RAID 5 or RAID 6 Replay',
         u'raidTypeUsed': u'Mixed',
         u'scName': u'Storage Center 64158',
         u'scSerialNumber': 64158,
         u'tiersUsedDescription': u'Tier 1',
         u'useTier1Storage': True,
         u'useTier2Storage': False,
         u'useTier3Storage': False,
         u'userCreated': False,
         u'volumeCount': 0},
        {u'allowedForFlashOptimized': False,
         u'allowedForNonFlashOptimized': True,
         u'index': 3,
         u'instanceId': u'64158.3',
         u'instanceName': u'Medium Priority',
         u'name': u'Medium Priority',
         u'notes': u'',
         u'objectType': u'ScStorageProfile',
         u'raidTypeDescription': u'RAID 10 Active, RAID 5 or RAID 6 Replay',
         u'raidTypeUsed': u'Mixed',
         u'scName': u'Storage Center 64158',
         u'scSerialNumber': 64158,
         u'tiersUsedDescription': u'Tier 2',
         u'useTier1Storage': False,
         u'useTier2Storage': True,
         u'useTier3Storage': False,
         u'userCreated': False,
         u'volumeCount': 0},
        {u'allowedForFlashOptimized': True,
         u'allowedForNonFlashOptimized': True,
         u'index': 4,
         u'instanceId': u'64158.4',
         u'instanceName': u'Low Priority',
         u'name': u'Low Priority',
         u'notes': u'',
         u'objectType': u'ScStorageProfile',
         u'raidTypeDescription': u'RAID 10 Active, RAID 5 or RAID 6 Replay',
         u'raidTypeUsed': u'Mixed',
         u'scName': u'Storage Center 64158',
         u'scSerialNumber': 64158,
         u'tiersUsedDescription': u'Tier 3',
         u'useTier1Storage': False,
         u'useTier2Storage': False,
         u'useTier3Storage': True,
         u'userCreated': False,
         u'volumeCount': 0}]

    CGS = [{u'profile':
            {u'instanceId': u'65690.4',
             u'instanceName': u'0869559e-6881-454e-ba18-15c6726d33c1',
             u'objectType': u'ScReplayProfile'},
            u'scSerialNumber': 65690,
            u'globalIndex': u'65690-4-2',
            u'description': u'GUID1-0869559e-6881-454e-ba18-15c6726d33c1',
            u'instanceId': u'65690.65690.4.2',
            u'scName': u'Storage Center 65690',
            u'expires': False,
            u'freezeTime': u'2015-09-28T14:00:59-05:00',
            u'expireTime': u'1969-12-31T18:00:00-06:00',
            u'expectedReplayCount': 2,
            u'writesHeldDuration': 19809,
            u'replayCount': 2,
            u'instanceName': u'Name1',
            u'objectType': u'ScReplayConsistencyGroup'},
           {u'profile':
            {u'instanceId': u'65690.4',
             u'instanceName': u'0869559e-6881-454e-ba18-15c6726d33c1',
             u'objectType': u'ScReplayProfile'},
            u'scSerialNumber': 65690,
            u'globalIndex': u'65690-4-3',
            u'description': u'GUID2-0869559e-6881-454e-ba18-15c6726d33c1',
            u'instanceId': u'65690.65690.4.3',
            u'scName': u'Storage Center 65690',
            u'expires': False,
            u'freezeTime': u'2015-09-28T14:00:59-05:00',
            u'expireTime': u'1969-12-31T18:00:00-06:00',
            u'expectedReplayCount': 2,
            u'writesHeldDuration': 19809,
            u'replayCount': 2,
            u'instanceName': u'Name2',
            u'objectType': u'ScReplayConsistencyGroup'}
           ]

    ISCSI_CONFIG = {
        u'initialReadyToTransfer': True,
        u'scSerialNumber': 64065,
        u'macAddress': u'00c0dd-1da173',
        u'instanceId': u'64065.5764839588723573038.6',
        u'vlanTagging': False,
        u'mapCount': 8,
        u'cardModel': u'Qle4062',
        u'portNumber': 3260,
        u'firstBurstSize': 256,
        u'deviceName': u'PCIDEV09',
        u'subnetMask': u'255.255.255.0',
        u'speed': u'1 Gbps',
        u'maximumVlanCount': 0,
        u'gatewayIpAddress': u'192.168.0.1',
        u'slot': 4,
        u'sfpData': u'',
        u'dataDigest': False,
        u'chapEnabled': False,
        u'firmwareVersion': u'03.00.01.77',
        u'preferredControllerIndex': 64066,
        u'defaultTimeToRetain': 20,
        u'objectType': u'ScControllerPortIscsiConfiguration',
        u'instanceName': u'5000d31000FCBE43',
        u'scName': u'sc64065',
        u'revision': u'0',
        u'controllerPortIndex': 5764839588723573038,
        u'maxBurstSize': 512,
        u'targetCount': 20,
        u'description': u'QLogic QLE4062 iSCSI Adapter Rev 0 Copper',
        u'vlanSupported': True,
        u'chapName': u'iqn.2002-03.com.compellent:5000d31000fcbe43',
        u'windowSize': 128,
        u'vlanId': 0,
        u'defaultTimeToWait': 2,
        u'headerDigest': False,
        u'slotPort': 2,
        u'immediateDataWrite': False,
        u'storageCenterTargetCount': 20,
        u'vlanCount': 0,
        u'scsiCommandTimeout': 60,
        u'slotType': u'PCI4',
        u'ipAddress': u'192.168.0.21',
        u'vlanUserPriority': 0,
        u'bothCount': 0,
        u'initiatorCount': 33,
        u'keepAliveTimeout': 30,
        u'homeControllerIndex': 64066,
        u'chapSecret': u'',
        u'maximumTransmissionUnit': 1500}

    SCQOS = {u'linkSpeed': u'1 Gbps',
             u'numberDevices': 1,
             u'bandwidthLimited': False,
             u'name': u'Cinder QoS',
             u'instanceId': u'64702.2',
             u'scName': u'Storage Center 64702',
             u'scSerialNumber': 64702,
             u'instanceName': u'Cinder QoS',
             u'advancedSettings': {u'globalMaxSectorPerIo': 512,
                                   u'destinationMaxSectorCount': 65536,
                                   u'queuePassMaxSectorCount': 65536,
                                   u'destinationMaxIoCount': 18,
                                   u'globalMaxIoCount': 32,
                                   u'queuePassMaxIoCount': 8},
             u'objectType': u'ScReplicationQosNode'}

    SCREPL = [{u'destinationVolume': {u'instanceId': u'65495.167',
                                      u'instanceName': u'Cinder repl of abcd9'
                                                       u'5b2-1284-4cf0-a397-9'
                                                       u'70fa6c68092',
                                      u'objectType': u'ScVolume'},
               u'instanceId': u'64702.9',
               u'scSerialNumber': 64702,
               u'syncStatus': u'NotApplicable',
               u'objectType': u'ScReplication',
               u'sourceStorageCenter': {u'instanceId': u'64702',
                                        u'instanceName': u'Storage Center '
                                                         '64702',
                                        u'objectType': u'StorageCenter'},
               u'secondaryTransportTypes': [],
               u'dedup': False,
               u'state': u'Up',
               u'replicateActiveReplay': False,
               u'qosNode': {u'instanceId': u'64702.2',
                            u'instanceName': u'Cinder QoS',
                            u'objectType': u'ScReplicationQosNode'},
               u'sourceVolume': {u'instanceId': u'64702.13108',
                                 u'instanceName': u'abcd95b2-1284-4cf0-a397-'
                                                  u'970fa6c68092',
                                 u'objectType': u'ScVolume'},
               u'type': u'Asynchronous',
               u'statusMessage': u'',
               u'status': u'Up',
               u'syncMode': u'None',
               u'stateMessage': u'',
               u'managedByLiveVolume': False,
               u'destinationScSerialNumber': 65495,
               u'pauseAllowed': True,
               u'instanceName': u"Replication of 'abcd95b2-1284-4cf0-"
                                u"a397-970fa6c68092'",
               u'simulation': False,
               u'transportTypes': [u'FibreChannel'],
               u'replicateStorageToLowestTier': True,
               u'scName': u'Storage Center 64702',
               u'destinationStorageCenter': {u'instanceId': u'65495',
                                             u'instanceName': u'Storage Center'
                                                              u' 65495',
                                             u'objectType': u'StorageCenter'}}]

    IQN = 'iqn.2002-03.com.compellent:5000D31000000001'
    WWN = u'21000024FF30441C'

    WWNS = [u'21000024FF30441C',
            u'21000024FF30441D']

    # Used to test finding no match in find_wwns
    WWNS_NO_MATCH = [u'21000024FF30451C',
                     u'21000024FF30451D']

    FLDR_PATH = 'StorageCenter/ScVolumeFolder/'

    # Create a Response object that indicates OK
    response_ok = models.Response()
    response_ok.status_code = 200
    response_ok.reason = u'ok'
    RESPONSE_200 = response_ok

    # Create a Response object that indicates created
    response_created = models.Response()
    response_created.status_code = 201
    response_created.reason = u'created'
    RESPONSE_201 = response_created

    # Create a Response object that can indicate a failure. Although
    # 204 can be a success with no return.  (Know your calls!)
    response_nc = models.Response()
    response_nc.status_code = 204
    response_nc.reason = u'duplicate'
    RESPONSE_204 = response_nc

    # Create a Response object is a pure error.
    response_bad = models.Response()
    response_bad.status_code = 400
    response_bad.reason = u'bad request'
    RESPONSE_400 = response_bad

    def setUp(self):
        super(DellSCSanAPITestCase, self).setUp()

        # Configuration is a mock.  A mock is pretty much a blank
        # slate.  I believe mock's done in setup are not happy time
        # mocks.  So we just do a few things like driver config here.
        self.configuration = mock.Mock()

        self.configuration.san_is_local = False
        self.configuration.san_ip = "192.168.0.1"
        self.configuration.san_login = "admin"
        self.configuration.san_password = "mmm"
        self.configuration.dell_sc_ssn = 12345
        self.configuration.dell_sc_server_folder = 'opnstktst'
        self.configuration.dell_sc_volume_folder = 'opnstktst'
        # Note that we set this to True even though we do not
        # test this functionality.  This is sent directly to
        # the requests calls as the verify parameter and as
        # that is a third party library deeply stubbed out is
        # not directly testable by this code.  Note that in the
        # case that this fails the driver fails to even come
        # up.
        self.configuration.dell_sc_verify_cert = True
        self.configuration.dell_sc_api_port = 3033
        self.configuration.iscsi_ip_address = '192.168.1.1'
        self.configuration.iscsi_port = 3260
        self._context = context.get_admin_context()
        self.apiversion = '2.0'

        # Set up the StorageCenterApi
        self.scapi = dell_storagecenter_api.StorageCenterApi(
            self.configuration.san_ip,
            self.configuration.dell_sc_api_port,
            self.configuration.san_login,
            self.configuration.san_password,
            self.configuration.dell_sc_verify_cert,
            self.apiversion)

        # Set up the scapi configuration vars
        self.scapi.ssn = self.configuration.dell_sc_ssn
        self.scapi.sfname = self.configuration.dell_sc_server_folder
        self.scapi.vfname = self.configuration.dell_sc_volume_folder
        # Note that we set this to True (or not) on the replication tests.
        self.scapi.failed_over = False

        self.volid = str(uuid.uuid4())
        self.volume_name = "volume" + self.volid

    def test_path_to_array(self,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi._path_to_array(u'folder1/folder2/folder3')
        expected = [u'folder1', u'folder2', u'folder3']
        self.assertEqual(expected, res, 'Unexpected folder path')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_result',
                       return_value=SC)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_sc(self,
                     mock_get,
                     mock_get_result,
                     mock_close_connection,
                     mock_open_connection,
                     mock_init):
        res = self.scapi.find_sc()
        mock_get.assert_called_once_with('StorageCenter/StorageCenter')
        self.assertTrue(mock_get_result.called)
        self.assertEqual(u'64702', res, 'Unexpected SSN')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_result',
                       return_value=None)
    def test_find_sc_failure(self,
                             mock_get_result,
                             mock_get,
                             mock_close_connection,
                             mock_open_connection,
                             mock_init):
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_sc)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_folder(self,
                           mock_post,
                           mock_first_result,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi._create_folder(
            'StorageCenter/ScVolumeFolder',
            '',
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.FLDR, res, 'Unexpected Folder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_folder_with_parent(self,
                                       mock_post,
                                       mock_first_result,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Test case where parent folder name is specified
        res = self.scapi._create_folder(
            'StorageCenter/ScVolumeFolder', 'parentFolder',
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.FLDR, res, 'Unexpected Folder')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_create_folder_failure(self,
                                   mock_post,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi._create_folder(
            'StorageCenter/ScVolumeFolder', '',
            self.configuration.dell_sc_volume_folder)
        self.assertIsNone(res, 'Test Create folder - None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_path_to_array',
                       return_value=['Cinder_Test_Folder'])
    def test_create_folder_path(self,
                                mock_path_to_array,
                                mock_find_folder,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        res = self.scapi._create_folder_path(
            'StorageCenter/ScVolumeFolder',
            self.configuration.dell_sc_volume_folder)
        mock_path_to_array.assert_called_once_with(
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_find_folder.called)
        self.assertEqual(self.FLDR, res, 'Unexpected ScFolder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_create_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_path_to_array',
                       return_value=['Cinder_Test_Folder'])
    def test_create_folder_path_create_fldr(self,
                                            mock_path_to_array,
                                            mock_find_folder,
                                            mock_create_folder,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        # Test case where folder is not found and must be created
        res = self.scapi._create_folder_path(
            'StorageCenter/ScVolumeFolder',
            self.configuration.dell_sc_volume_folder)
        mock_path_to_array.assert_called_once_with(
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_find_folder.called)
        self.assertTrue(mock_create_folder.called)
        self.assertEqual(self.FLDR, res, 'Unexpected ScFolder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_create_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_path_to_array',
                       return_value=['Cinder_Test_Folder'])
    def test_create_folder_path_failure(self,
                                        mock_path_to_array,
                                        mock_find_folder,
                                        mock_create_folder,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        # Test case where folder is not found, must be created
        # and creation fails
        res = self.scapi._create_folder_path(
            'StorageCenter/ScVolumeFolder',
            self.configuration.dell_sc_volume_folder)
        mock_path_to_array.assert_called_once_with(
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_find_folder.called)
        self.assertTrue(mock_create_folder.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_result',
                       return_value=u'devstackvol/fcvm/')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_folder(self,
                         mock_post,
                         mock_get_result,
                         mock_close_connection,
                         mock_open_connection,
                         mock_init):
        res = self.scapi._find_folder(
            'StorageCenter/ScVolumeFolder',
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_result.called)
        self.assertEqual(u'devstackvol/fcvm/', res, 'Unexpected folder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_result',
                       return_value=u'devstackvol/fcvm/')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_folder_multi_fldr(self,
                                    mock_post,
                                    mock_get_result,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        # Test case for folder path with multiple folders
        res = self.scapi._find_folder(
            'StorageCenter/ScVolumeFolder',
            u'testParentFolder/opnstktst')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_result.called)
        self.assertEqual(u'devstackvol/fcvm/', res, 'Unexpected folder')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_find_folder_failure(self,
                                 mock_post,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        res = self.scapi._find_folder(
            'StorageCenter/ScVolumeFolder',
            self.configuration.dell_sc_volume_folder)
        self.assertIsNone(res, 'Test find folder - None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=None)
    def test_find_volume_folder_fail(self,
                                     mock_find_folder,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test case where _find_volume_folder returns none
        res = self.scapi._find_volume_folder(
            False)
        mock_find_folder.assert_called_once_with(
            'StorageCenter/ScVolumeFolder/GetList',
            self.configuration.dell_sc_volume_folder)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=FLDR)
    def test_find_volume_folder(self,
                                mock_find_folder,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        res = self.scapi._find_volume_folder(
            False)
        mock_find_folder.assert_called_once_with(
            'StorageCenter/ScVolumeFolder/GetList',
            self.configuration.dell_sc_volume_folder)
        self.assertEqual(self.FLDR, res, 'Unexpected Folder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=STORAGE_PROFILE_LIST)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_storage_profile_fail(self,
                                       mock_json,
                                       mock_find_folder,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Test case where _find_volume_folder returns none
        res = self.scapi._find_storage_profile("Blah")
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=STORAGE_PROFILE_LIST)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_storage_profile_none(self,
                                       mock_json,
                                       mock_find_folder,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Test case where _find_storage_profile returns none
        res = self.scapi._find_storage_profile(None)
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=STORAGE_PROFILE_LIST)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @ddt.data('HighPriority', 'highpriority', 'High Priority')
    def test_find_storage_profile(self,
                                  value,
                                  mock_json,
                                  mock_find_folder,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        res = self.scapi._find_storage_profile(value)
        self.assertIsNotNone(res, 'Expected matching storage profile!')
        self.assertEqual(self.STORAGE_PROFILE_LIST[1]['instanceId'],
                         res.get('instanceId'))

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_create_folder_path',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=None)
    def test_find_volume_folder_create_folder(self,
                                              mock_find_folder,
                                              mock_create_folder_path,
                                              mock_close_connection,
                                              mock_open_connection,
                                              mock_init):
        # Test case where _find_volume_folder returns none and folder must be
        # created
        res = self.scapi._find_volume_folder(
            True)
        mock_find_folder.assert_called_once_with(
            'StorageCenter/ScVolumeFolder/GetList',
            self.configuration.dell_sc_volume_folder)
        self.assertTrue(mock_create_folder_path.called)
        self.assertEqual(self.FLDR, res, 'Unexpected Folder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'unmap_volume',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'map_volume',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SCSERVERS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_init_volume(self,
                         mock_post,
                         mock_get_json,
                         mock_map_volume,
                         mock_unmap_volume,
                         mock_find_volume,
                         mock_close_connection,
                         mock_open_connection,
                         mock_init):
        self.scapi._init_volume(self.VOLUME)
        self.assertTrue(mock_map_volume.called)
        self.assertTrue(mock_unmap_volume.called)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_init_volume_failure(self,
                                 mock_post,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        # Test case where ScServer list fails
        self.scapi._init_volume(self.VOLUME)
        self.assertTrue(mock_post.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'unmap_volume',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'map_volume',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SCSERVERS_DOWN)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_init_volume_servers_down(self,
                                      mock_post,
                                      mock_get_json,
                                      mock_map_volume,
                                      mock_unmap_volume,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case where ScServer Status = Down
        self.scapi._init_volume(self.VOLUME)
        self.assertFalse(mock_map_volume.called)
        self.assertFalse(mock_unmap_volume.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_volume(self,
                           mock_post,
                           mock_find_volume_folder,
                           mock_get_json,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi.create_volume(
            self.volume_name,
            1)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_storage_profile',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    def test_create_volume_storage_profile_missing(self,
                                                   mock_find_volume_folder,
                                                   mock_find_storage_profile,
                                                   mock_close_connection,
                                                   mock_open_connection,
                                                   mock_init):
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.create_volume,
                          self.volume_name,
                          1,
                          'Blah')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_storage_profile',
                       return_value=STORAGE_PROFILE_LIST[0])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_volume_storage_profile(self,
                                           mock_post,
                                           mock_find_volume_folder,
                                           mock_find_storage_profile,
                                           mock_get_json,
                                           mock_close_connection,
                                           mock_open_connection,
                                           mock_init):
        self.scapi.create_volume(
            self.volume_name,
            1,
            'Recommended')
        actual = mock_post.call_args[0][1]['StorageProfile']
        expected = self.STORAGE_PROFILE_LIST[0]['instanceId']
        self.assertEqual(expected, actual)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_volume_retry_find(self,
                                      mock_post,
                                      mock_find_volume_folder,
                                      mock_get_json,
                                      mock_find_volume,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case where find_volume is used to do a retry of finding the
        # created volume
        res = self.scapi.create_volume(
            self.volume_name,
            1)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertTrue(mock_find_volume.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_vol_folder_fail(self,
                                    mock_post,
                                    mock_find_volume_folder,
                                    mock_get_json,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        # Test calling create_volume where volume folder does not exist and
        # fails to be created
        res = self.scapi.create_volume(
            self.volume_name,
            1)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_create_volume_failure(self,
                                   mock_post,
                                   mock_find_volume_folder,
                                   mock_get_json,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi.create_volume(
            self.volume_name,
            1)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME_LIST)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test__get_volume_list_enforce_vol_fldr(self,
                                               mock_post,
                                               mock_get_json,
                                               mock_close_connection,
                                               mock_open_connection,
                                               mock_init):
        # Test case to find volume in the configured volume folder
        res = self.scapi._get_volume_list(self.volume_name, None, True)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.VOLUME_LIST, res, 'Unexpected volume list')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME_LIST)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test__get_volume_list_any_fldr(self,
                                       mock_post,
                                       mock_get_json,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Test case to find volume anywhere in the configured SC
        res = self.scapi._get_volume_list(self.volume_name, None, False)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.VOLUME_LIST, res, 'Unexpected volume list')

    def test_get_volume_list_no_name_no_id(self,
                                           mock_close_connection,
                                           mock_open_connection,
                                           mock_init):
        # Test case specified volume name is None and device id is None.
        res = self.scapi._get_volume_list(None, None, True)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test__get_volume_list_failure(self,
                                      mock_post,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case to find volume in the configured volume folder
        res = self.scapi._get_volume_list(self.volume_name, None, True)
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=VOLUME_LIST)
    def test_find_volume(self,
                         mock_get_vol_list,
                         mock_close_connection,
                         mock_open_connection,
                         mock_init):
        # Test case to find volume by name
        res = self.scapi.find_volume(self.volume_name)
        self.assertTrue(mock_get_vol_list.called)
        self.assertEqual(self.VOLUME, res, 'Unexpected volume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=None)
    def test_find_volume_no_name(self,
                                 mock_get_volume_list,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        # Test calling find_volume with no name or instanceid
        res = self.scapi.find_volume(None)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list')
    def test_find_volume_not_found(self,
                                   mock_get_volume_list,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Test calling find_volume with result of no volume found
        mock_get_volume_list.side_effect = [[], []]
        res = self.scapi.find_volume(self.volume_name)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_import_one',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list')
    def test_find_volume_complete_replication(self,
                                              mock_get_volume_list,
                                              mock_import_one,
                                              mock_close_connection,
                                              mock_open_connection,
                                              mock_init):
        self.scapi.failed_over = True
        mock_get_volume_list.side_effect = [[], [], self.VOLUME_LIST]
        res = self.scapi.find_volume(self.volume_name)
        self.assertEqual(self.VOLUME, res, 'Unexpected volume')
        self.scapi.failed_over = False

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_import_one',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list')
    def test_find_volume_complete_replication_fail(self,
                                                   mock_get_volume_list,
                                                   mock_import_one,
                                                   mock_close_connection,
                                                   mock_open_connection,
                                                   mock_init):
        self.scapi.failed_over = True
        mock_get_volume_list.side_effect = [[], [], self.VOLUME_LIST]
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_volume, self.volume_name)
        self.scapi.failed_over = False

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list')
    def test_find_volume_complete_replication_multi(self,
                                                    mock_get_volume_list,
                                                    mock_close_connection,
                                                    mock_open_connection,
                                                    mock_init):
        # Test case where multiple repl volumes are found.
        mock_get_volume_list.side_effect = [[],
                                            [],
                                            self.VOLUME_LIST_MULTI_VOLS]
        self.scapi.failed_over = True
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_volume, self.volume_name)
        self.scapi.failed_over = False

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=VOLUME_LIST_MULTI_VOLS)
    def test_find_volume_multi_vols_found(self,
                                          mock_get_volume_list,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        # Test case where multiple volumes are found
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_volume, self.volume_name)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=VOLUME)
    def test_delete_volume(self,
                           mock_find_volume,
                           mock_delete,
                           mock_get_json,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi.delete_volume(self.volume_name)
        self.assertTrue(mock_delete.called)
        mock_find_volume.assert_called_once_with(self.volume_name)
        self.assertTrue(mock_get_json.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_400)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=VOLUME)
    def test_delete_volume_failure(self,
                                   mock_find_volume,
                                   mock_delete,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.delete_volume, self.volume_name)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=None)
    def test_delete_volume_no_vol_found(self,
                                        mock_find_volume,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        # Test case where volume to be deleted does not exist
        res = self.scapi.delete_volume(self.volume_name)
        self.assertTrue(res, 'Expected True')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=SVR_FLDR)
    def test_find_server_folder(self,
                                mock_find_folder,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        res = self.scapi._find_server_folder(False)
        mock_find_folder.assert_called_once_with(
            'StorageCenter/ScServerFolder/GetList',
            self.configuration.dell_sc_server_folder)
        self.assertEqual(self.SVR_FLDR, res, 'Unexpected server folder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_create_folder_path',
                       return_value=SVR_FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=None)
    def test_find_server_folder_create_folder(self,
                                              mock_find_folder,
                                              mock_create_folder_path,
                                              mock_close_connection,
                                              mock_open_connection,
                                              mock_init):
        # Test case where specified server folder is not found and must be
        # created
        res = self.scapi._find_server_folder(True)
        mock_find_folder.assert_called_once_with(
            'StorageCenter/ScServerFolder/GetList',
            self.configuration.dell_sc_server_folder)
        self.assertTrue(mock_create_folder_path.called)
        self.assertEqual(self.SVR_FLDR, res, 'Unexpected server folder')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_folder',
                       return_value=None)
    def test_find_server_folder_fail(self,
                                     mock_find_folder,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test case where _find_server_folder returns none
        res = self.scapi._find_server_folder(
            False)
        mock_find_folder.assert_called_once_with(
            'StorageCenter/ScServerFolder/GetList',
            self.configuration.dell_sc_volume_folder)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_add_hba(self,
                     mock_post,
                     mock_close_connection,
                     mock_open_connection,
                     mock_init):
        res = self.scapi._add_hba(self.SCSERVER,
                                  self.IQN,
                                  False)
        self.assertTrue(mock_post.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_add_hba_fc(self,
                        mock_post,
                        mock_close_connection,
                        mock_open_connection,
                        mock_init):
        res = self.scapi._add_hba(self.SCSERVER,
                                  self.WWN,
                                  True)
        self.assertTrue(mock_post.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_add_hba_failure(self,
                             mock_post,
                             mock_close_connection,
                             mock_open_connection,
                             mock_init):
        res = self.scapi._add_hba(self.SCSERVER,
                                  self.IQN,
                                  False)
        self.assertTrue(mock_post.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SVR_OS_S)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_serveros(self,
                           mock_post,
                           mock_get_json,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi._find_serveros('Red Hat Linux 6.x')
        self.assertTrue(mock_get_json.called)
        self.assertTrue(mock_post.called)
        self.assertEqual('64702.38', res, 'Wrong InstanceId')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SVR_OS_S)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_serveros_not_found(self,
                                     mock_post,
                                     mock_get_json,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test requesting a Server OS that will not be found
        res = self.scapi._find_serveros('Non existent OS')
        self.assertTrue(mock_get_json.called)
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_find_serveros_failed(self,
                                  mock_post,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        res = self.scapi._find_serveros('Red Hat Linux 6.x')
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=FC_HBA)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'create_server',
                       return_value=SCSERVER)
    def test_create_server_multiple_hbas(self,
                                         mock_create_server,
                                         mock_add_hba,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        res = self.scapi.create_server_multiple_hbas(
            self.WWNS)
        self.assertTrue(mock_create_server.called)
        self.assertTrue(mock_add_hba.called)
        self.assertEqual(self.SCSERVER, res, 'Unexpected ScServer')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=SCSERVER)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_server_folder',
                       return_value=SVR_FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serveros',
                       return_value='64702.38')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_server(self,
                           mock_post,
                           mock_find_serveros,
                           mock_find_server_folder,
                           mock_first_result,
                           mock_add_hba,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi.create_server(
            self.IQN,
            False)
        self.assertTrue(mock_find_serveros.called)
        self.assertTrue(mock_find_server_folder.called)
        self.assertTrue(mock_first_result.called)
        self.assertTrue(mock_add_hba.called)
        self.assertEqual(self.SCSERVER, res, 'Unexpected ScServer')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=SCSERVER)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_server_folder',
                       return_value=SVR_FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serveros',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_server_os_not_found(self,
                                        mock_post,
                                        mock_find_serveros,
                                        mock_find_server_folder,
                                        mock_first_result,
                                        mock_add_hba,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        res = self.scapi.create_server(
            self.IQN,
            False)
        self.assertTrue(mock_find_serveros.called)
        self.assertEqual(self.SCSERVER, res, 'Unexpected ScServer')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=SCSERVER)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_server_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serveros',
                       return_value='64702.38')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_server_fldr_not_found(self,
                                          mock_post,
                                          mock_find_serveros,
                                          mock_find_server_folder,
                                          mock_first_result,
                                          mock_add_hba,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        res = self.scapi.create_server(
            self.IQN,
            False)
        self.assertTrue(mock_find_server_folder.called)
        self.assertEqual(self.SCSERVER, res, 'Unexpected ScServer')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=SCSERVER)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_server_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serveros',
                       return_value='64702.38')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_create_server_failure(self,
                                   mock_post,
                                   mock_find_serveros,
                                   mock_find_server_folder,
                                   mock_first_result,
                                   mock_add_hba,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi.create_server(
            self.IQN,
            False)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_server_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serveros',
                       return_value='64702.38')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_server_not_found(self,
                                     mock_post,
                                     mock_find_serveros,
                                     mock_find_server_folder,
                                     mock_first_result,
                                     mock_add_hba,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test create server where _first_result is None
        res = self.scapi.create_server(
            self.IQN,
            False)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_delete_server',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_hba',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=SCSERVER)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_server_folder',
                       return_value=SVR_FLDR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serveros',
                       return_value='64702.38')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_server_addhba_fail(self,
                                       mock_post,
                                       mock_find_serveros,
                                       mock_find_server_folder,
                                       mock_first_result,
                                       mock_add_hba,
                                       mock_delete_server,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Tests create server where add hba fails
        res = self.scapi.create_server(
            self.IQN,
            False)
        self.assertTrue(mock_delete_server.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=SCSERVER)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serverhba',
                       return_value=ISCSI_HBA)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_server(self,
                         mock_post,
                         mock_find_serverhba,
                         mock_first_result,
                         mock_close_connection,
                         mock_open_connection,
                         mock_init):
        res = self.scapi.find_server(self.IQN)
        self.assertTrue(mock_find_serverhba.called)
        self.assertTrue(mock_first_result.called)
        self.assertIsNotNone(res, 'Expected ScServer')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serverhba',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_server_no_hba(self,
                                mock_post,
                                mock_find_serverhba,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        # Test case where a ScServer HBA does not exist with the specified IQN
        # or WWN
        res = self.scapi.find_server(self.IQN)
        self.assertTrue(mock_find_serverhba.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_serverhba',
                       return_value=ISCSI_HBA)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_find_server_failure(self,
                                 mock_post,
                                 mock_find_serverhba,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        # Test case where a ScServer does not exist with the specified
        # ScServerHba
        res = self.scapi.find_server(self.IQN)
        self.assertTrue(mock_find_serverhba.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=ISCSI_HBA)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_serverhba(self,
                            mock_post,
                            mock_first_result,
                            mock_close_connection,
                            mock_open_connection,
                            mock_init):
        res = self.scapi.find_server(self.IQN)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertIsNotNone(res, 'Expected ScServerHba')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_find_serverhba_failure(self,
                                    mock_post,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        # Test case where a ScServer does not exist with the specified
        # ScServerHba
        res = self.scapi.find_server(self.IQN)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=ISCSI_FLT_DOMAINS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_domains(self,
                          mock_get,
                          mock_get_json,
                          mock_close_connection,
                          mock_open_connection,
                          mock_init):
        res = self.scapi._find_domains(u'64702.5764839588723736074.69')
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(
            self.ISCSI_FLT_DOMAINS, res, 'Unexpected ScIscsiFaultDomain')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_204)
    def test_find_domains_error(self,
                                mock_get,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        # Test case where get of ScControllerPort FaultDomainList fails
        res = self.scapi._find_domains(u'64702.5764839588723736074.69')
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=FC_HBAS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_fc_initiators(self,
                                mock_get,
                                mock_get_json,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        res = self.scapi._find_fc_initiators(self.SCSERVER)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertIsNotNone(res, 'Expected WWN list')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_find_fc_initiators_error(self,
                                      mock_get,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case where get of ScServer HbaList fails
        res = self.scapi._find_fc_initiators(self.SCSERVER)
        self.assertListEqual([], res, 'Expected empty list')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_get_volume_count(self,
                              mock_get,
                              mock_get_json,
                              mock_close_connection,
                              mock_open_connection,
                              mock_init):
        res = self.scapi.get_volume_count(self.SCSERVER)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(len(self.MAPPINGS), res, 'Mapping count mismatch')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_get_volume_count_failure(self,
                                      mock_get,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case of where get of ScServer MappingList fails
        res = self.scapi.get_volume_count(self.SCSERVER)
        self.assertTrue(mock_get.called)
        self.assertEqual(-1, res, 'Mapping count not -1')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_get_volume_count_no_volumes(self,
                                         mock_get,
                                         mock_get_json,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        res = self.scapi.get_volume_count(self.SCSERVER)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(len([]), res, 'Mapping count mismatch')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_mappings(self,
                           mock_get,
                           mock_get_json,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi._find_mappings(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.MAPPINGS, res, 'Mapping mismatch')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_mappings_inactive_vol(self,
                                        mock_get,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        # Test getting volume mappings on inactive volume
        res = self.scapi._find_mappings(self.INACTIVE_VOLUME)
        self.assertFalse(mock_get.called)
        self.assertEqual([], res, 'No mappings expected')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_find_mappings_failure(self,
                                   mock_get,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Test case of where get of ScVolume MappingList fails
        res = self.scapi._find_mappings(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertEqual([], res, 'Mapping count not empty')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_mappings_no_mappings(self,
                                       mock_get,
                                       mock_get_json,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Test case where ScVolume has no mappings
        res = self.scapi._find_mappings(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual([], res, 'Mapping count mismatch')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=MAP_PROFILES)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_mapping_profiles(self,
                                   mock_get,
                                   mock_get_json,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Test case where ScVolume has no mappings
        res = self.scapi._find_mapping_profiles(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.MAP_PROFILES, res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_find_mapping_profiles_error(self,
                                         mock_get,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        # Test case where ScVolume has no mappings
        res = self.scapi._find_mapping_profiles(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertEqual([], res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_controller_port(self,
                                  mock_get,
                                  mock_first_result,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        res = self.scapi._find_controller_port(u'64702.5764839588723736070.51')
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.CTRLR_PORT, res, 'ScControllerPort mismatch')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_204)
    def test_find_controller_port_failure(self,
                                          mock_get,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        # Test case where get of ScVolume MappingList fails
        res = self.scapi._find_controller_port(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=FC_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=FC_MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_fc_initiators',
                       return_value=WWNS)
    def test_find_wwns(self,
                       mock_find_fc_initiators,
                       mock_find_mappings,
                       mock_find_controller_port,
                       mock_close_connection,
                       mock_open_connection,
                       mock_init):
        lun, wwns, itmap = self.scapi.find_wwns(self.VOLUME,
                                                self.SCSERVER)
        self.assertTrue(mock_find_fc_initiators.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_controller_port.called)

        # The _find_controller_port is Mocked, so all mapping pairs
        # will have the same WWN for the ScControllerPort
        itmapCompare = {u'21000024FF30441C': [u'5000D31000FCBE36'],
                        u'21000024FF30441D':
                        [u'5000D31000FCBE36', u'5000D31000FCBE36']}
        self.assertEqual(1, lun, 'Incorrect LUN')
        self.assertIsNotNone(wwns, 'WWNs is None')
        self.assertEqual(itmapCompare, itmap, 'WWN mapping incorrect')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_fc_initiators',
                       return_value=FC_HBAS)
    def test_find_wwns_no_mappings(self,
                                   mock_find_fc_initiators,
                                   mock_find_mappings,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Test case where there are no ScMapping(s)
        lun, wwns, itmap = self.scapi.find_wwns(self.VOLUME,
                                                self.SCSERVER)
        self.assertTrue(mock_find_fc_initiators.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertIsNone(lun, 'Incorrect LUN')
        self.assertEqual([], wwns, 'WWNs is not empty')
        self.assertEqual({}, itmap, 'WWN mapping not empty')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=FC_MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_fc_initiators',
                       return_value=WWNS)
    def test_find_wwns_no_ctlr_port(self,
                                    mock_find_fc_initiators,
                                    mock_find_mappings,
                                    mock_find_controller_port,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        # Test case where ScControllerPort is none
        lun, wwns, itmap = self.scapi.find_wwns(self.VOLUME,
                                                self.SCSERVER)
        self.assertTrue(mock_find_fc_initiators.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_controller_port.called)
        self.assertIsNone(lun, 'Incorrect LUN')
        self.assertEqual([], wwns, 'WWNs is not empty')
        self.assertEqual({}, itmap, 'WWN mapping not empty')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=FC_CTRLR_PORT_WWN_ERROR)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=FC_MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_fc_initiators',
                       return_value=WWNS)
    def test_find_wwns_wwn_error(self,
                                 mock_find_fc_initiators,
                                 mock_find_mappings,
                                 mock_find_controller_port,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        # Test case where ScControllerPort object has WWn instead of wwn for a
        # property
        lun, wwns, itmap = self.scapi.find_wwns(self.VOLUME,
                                                self.SCSERVER)
        self.assertTrue(mock_find_fc_initiators.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_controller_port.called)

        self.assertIsNone(lun, 'Incorrect LUN')
        self.assertEqual([], wwns, 'WWNs is not empty')
        self.assertEqual({}, itmap, 'WWN mapping not empty')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=FC_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=FC_MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_fc_initiators',
                       return_value=WWNS_NO_MATCH)
    # Test case where HBA name is not found in list of initiators
    def test_find_wwns_hbaname_not_found(self,
                                         mock_find_fc_initiators,
                                         mock_find_mappings,
                                         mock_find_controller_port,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        lun, wwns, itmap = self.scapi.find_wwns(self.VOLUME,
                                                self.SCSERVER)
        self.assertTrue(mock_find_fc_initiators.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_controller_port.called)

        self.assertIsNone(lun, 'Incorrect LUN')
        self.assertEqual([], wwns, 'WWNs is not empty')
        self.assertEqual({}, itmap, 'WWN mapping not empty')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=FC_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=FC_MAPPINGS_LUN_MISMATCH)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_fc_initiators',
                       return_value=WWNS)
    # Test case where FC mappings contain a LUN mismatch
    def test_find_wwns_lun_mismatch(self,
                                    mock_find_fc_initiators,
                                    mock_find_mappings,
                                    mock_find_controller_port,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        lun, wwns, itmap = self.scapi.find_wwns(self.VOLUME,
                                                self.SCSERVER)
        self.assertTrue(mock_find_fc_initiators.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_controller_port.called)
        # The _find_controller_port is Mocked, so all mapping pairs
        # will have the same WWN for the ScControllerPort
        itmapCompare = {u'21000024FF30441C': [u'5000D31000FCBE36'],
                        u'21000024FF30441D':
                        [u'5000D31000FCBE36', u'5000D31000FCBE36']}
        self.assertEqual(1, lun, 'Incorrect LUN')
        self.assertIsNotNone(wwns, 'WWNs is None')
        self.assertEqual(itmapCompare, itmap, 'WWN mapping incorrect')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=VOLUME_CONFIG)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_active_controller(self,
                                    mock_get,
                                    mock_first_result,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        res = self.scapi._find_active_controller(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual('64702.64703', res, 'Unexpected Active Controller')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_find_active_controller_failure(self,
                                            mock_get,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        # Test case of where get of ScVolume MappingList fails
        res = self.scapi._find_active_controller(self.VOLUME)
        self.assertTrue(mock_get.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.5764839588723736131.91')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_domains',
                       return_value=ISCSI_FLT_DOMAINS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_mappings(self,
                                            mock_is_virtualport_mode,
                                            mock_find_mappings,
                                            mock_find_domains,
                                            mock_find_ctrl_port,
                                            mock_find_active_controller,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        res = self.scapi.find_iscsi_properties(self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_domains.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_domains',
                       return_value=ISCSI_FLT_DOMAINS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_by_address(self,
                                              mock_is_virtualport_mode,
                                              mock_find_mappings,
                                              mock_find_domains,
                                              mock_find_ctrl_port,
                                              mock_find_active_controller,
                                              mock_close_connection,
                                              mock_open_connection,
                                              mock_init):
        # Test case to find iSCSI mappings by IP Address & port
        res = self.scapi.find_iscsi_properties(
            self.VOLUME, '192.168.0.21', 3260)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_domains.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_domains',
                       return_value=ISCSI_FLT_DOMAINS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_by_address_not_found(
            self,
            mock_is_virtualport_mode,
            mock_find_mappings,
            mock_find_domains,
            mock_find_ctrl_port,
            mock_find_active_ctrl,
            mock_close_connection,
            mock_open_connection,
            mock_init):
        # Test case to find iSCSI mappings by IP Address & port are not found
        res = self.scapi.find_iscsi_properties(
            self.VOLUME, '192.168.1.21', 3260)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_domains.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_ctrl.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=[])
    def test_find_iscsi_properties_no_mapping(self,
                                              mock_find_mappings,
                                              mock_close_connection,
                                              mock_open_connection,
                                              mock_init):
        # Test case where there are no ScMapping(s)
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_iscsi_properties,
                          self.VOLUME)
        self.assertTrue(mock_find_mappings.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_domains',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_no_domain(self,
                                             mock_is_virtualport_mode,
                                             mock_find_mappings,
                                             mock_find_domains,
                                             mock_find_ctrl_port,
                                             mock_find_active_controller,
                                             mock_close_connection,
                                             mock_open_connection,
                                             mock_init):
        # Test case where there are no ScFaultDomain(s)
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_iscsi_properties,
                          self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_domains.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_no_ctrl_port(self,
                                                mock_is_virtualport_mode,
                                                mock_find_mappings,
                                                mock_find_ctrl_port,
                                                mock_find_active_controller,
                                                mock_close_connection,
                                                mock_open_connection,
                                                mock_init):
        # Test case where there are no ScFaultDomain(s)
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_iscsi_properties,
                          self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_domains',
                       return_value=ISCSI_FLT_DOMAINS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS_READ_ONLY)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_ro(self,
                                      mock_is_virtualport_mode,
                                      mock_find_mappings,
                                      mock_find_domains,
                                      mock_find_ctrl_port,
                                      mock_find_active_controller,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case where Read Only mappings are found
        res = self.scapi.find_iscsi_properties(self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_domains.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_domains',
                       return_value=ISCSI_FLT_DOMAINS_MULTI_PORTALS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS_MULTI_PORTAL)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=True)
    def test_find_iscsi_properties_multi_portals(self,
                                                 mock_is_virtualport_mode,
                                                 mock_find_mappings,
                                                 mock_find_domains,
                                                 mock_find_ctrl_port,
                                                 mock_find_active_controller,
                                                 mock_close_connection,
                                                 mock_open_connection,
                                                 mock_init):
        # Test case where there are multiple portals
        res = self.scapi.find_iscsi_properties(self.VOLUME)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_domains.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        self.assertTrue(mock_is_virtualport_mode.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                         u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                         u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                         u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1, 1, 1, 1],
                    'target_portal': u'192.168.0.25:3260',
                    'target_portals': [u'192.168.0.21:3260',
                                       u'192.168.0.25:3260',
                                       u'192.168.0.21:3260',
                                       u'192.168.0.25:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.5764839588723736131.91')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port_iscsi_config',
                       return_value=ISCSI_CONFIG)
    def test_find_iscsi_properties_mappings_legacy(
            self,
            mock_find_controller_port_iscsi_config,
            mock_is_virtualport_mode,
            mock_find_mappings,
            mock_find_ctrl_port,
            mock_find_active_controller,
            mock_close_connection,
            mock_open_connection,
            mock_init):
        res = self.scapi.find_iscsi_properties(self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_controller_port_iscsi_config.called)
        self.assertTrue(mock_find_active_controller.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.5764839588723736131.91')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port_iscsi_config',
                       return_value=None)
    def test_find_iscsi_properties_mappings_legacy_no_iscsi_config(
            self,
            mock_find_controller_port_iscsi_config,
            mock_is_virtualport_mode,
            mock_find_mappings,
            mock_find_ctrl_port,
            mock_find_active_controller,
            mock_close_connection,
            mock_open_connection,
            mock_init):
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_iscsi_properties,
                          self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_controller_port_iscsi_config.called)
        self.assertTrue(mock_find_active_controller.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port_iscsi_config',
                       return_value=ISCSI_CONFIG)
    def test_find_iscsi_properties_by_address_legacy(
            self,
            mock_find_controller_port_iscsi_config,
            mock_is_virtualport_mode,
            mock_find_mappings,
            mock_find_ctrl_port,
            mock_find_active_controller,
            mock_close_connection,
            mock_open_connection,
            mock_init):
        # Test case to find iSCSI mappings by IP Address & port
        res = self.scapi.find_iscsi_properties(
            self.VOLUME, '192.168.0.21', 3260)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        self.assertTrue(mock_find_controller_port_iscsi_config.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port_iscsi_config',
                       return_value=ISCSI_CONFIG)
    def test_find_iscsi_properties_by_address_not_found_legacy(
            self,
            mock_find_controller_port_iscsi_config,
            mock_is_virtualport_mode,
            mock_find_mappings,
            mock_find_ctrl_port,
            mock_find_active_ctrl,
            mock_close_connection,
            mock_open_connection,
            mock_init):
        # Test case to find iSCSI mappings by IP Address & port are not found
        res = self.scapi.find_iscsi_properties(
            self.VOLUME, '192.168.1.21', 3260)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_ctrl.called)
        self.assertTrue(mock_find_controller_port_iscsi_config.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS_READ_ONLY)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port_iscsi_config',
                       return_value=ISCSI_CONFIG)
    def test_find_iscsi_properties_ro_legacy(self,
                                             mock_find_iscsi_config,
                                             mock_is_virtualport_mode,
                                             mock_find_mappings,
                                             mock_find_ctrl_port,
                                             mock_find_active_controller,
                                             mock_close_connection,
                                             mock_open_connection,
                                             mock_init):
        # Test case where Read Only mappings are found
        res = self.scapi.find_iscsi_properties(self.VOLUME)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        self.assertTrue(mock_find_iscsi_config.called)
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_active_controller',
                       return_value='64702.64702')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port',
                       return_value=ISCSI_CTRLR_PORT)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=MAPPINGS_MULTI_PORTAL)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_is_virtualport_mode',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_controller_port_iscsi_config',
                       return_value=ISCSI_CONFIG)
    def test_find_iscsi_properties_multi_portals_legacy(
            self,
            mock_find_controller_port_iscsi_config,
            mock_is_virtualport_mode,
            mock_find_mappings,
            mock_find_ctrl_port,
            mock_find_active_controller,
            mock_close_connection,
            mock_open_connection,
            mock_init):
        # Test case where there are multiple portals
        res = self.scapi.find_iscsi_properties(self.VOLUME)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_find_ctrl_port.called)
        self.assertTrue(mock_find_active_controller.called)
        self.assertTrue(mock_is_virtualport_mode.called)
        self.assertTrue(mock_find_controller_port_iscsi_config.called)
        # Since we're feeding the same info back multiple times the information
        # will be duped.
        expected = {'target_discovered': False,
                    'target_iqn':
                        u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                    'target_iqns':
                        [u'iqn.2002-03.com.compellent:5000d31000fcbe43',
                         u'iqn.2002-03.com.compellent:5000d31000fcbe43'],
                    'target_lun': 1,
                    'target_luns': [1, 1],
                    'target_portal': u'192.168.0.21:3260',
                    'target_portals': [u'192.168.0.21:3260',
                                       u'192.168.0.21:3260']}
        self.assertEqual(expected, res, 'Wrong Target Info')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=MAP_PROFILE)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=[])
    def test_map_volume(self,
                        mock_find_mapping_profiles,
                        mock_post,
                        mock_first_result,
                        mock_close_connection,
                        mock_open_connection,
                        mock_init):
        res = self.scapi.map_volume(self.VOLUME,
                                    self.SCSERVER)
        self.assertTrue(mock_find_mapping_profiles.called)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.MAP_PROFILE, res, 'Incorrect ScMappingProfile')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=MAP_PROFILE)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=MAP_PROFILES)
    def test_map_volume_existing_mapping(self,
                                         mock_find_mappings,
                                         mock_post,
                                         mock_first_result,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        res = self.scapi.map_volume(self.VOLUME,
                                    self.SCSERVER)
        self.assertTrue(mock_find_mappings.called)
        self.assertFalse(mock_post.called)
        self.assertFalse(mock_first_result.called)
        self.assertEqual(self.MAP_PROFILE, res, 'Incorrect ScMappingProfile')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=MAP_PROFILE)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=[])
    def test_map_volume_existing_mapping_not_us(self,
                                                mock_find_mappings,
                                                mock_post,
                                                mock_first_result,
                                                mock_close_connection,
                                                mock_open_connection,
                                                mock_init):
        server = {'instanceId': 64702.48}
        res = self.scapi.map_volume(self.VOLUME,
                                    server)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.MAP_PROFILE, res, 'Incorrect ScMappingProfile')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post')
    def test_map_volume_no_vol_id(self,
                                  mock_post,
                                  mock_first_result,
                                  mock_get_id,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        # Test case where ScVolume instanceId is None
        mock_get_id.side_effect = [None, '64702.47']
        res = self.scapi.map_volume(self.VOLUME,
                                    self.SCSERVER)
        self.assertFalse(mock_post.called)
        self.assertFalse(mock_first_result.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post')
    def test_map_volume_no_server_id(self,
                                     mock_post,
                                     mock_first_result,
                                     mock_get_id,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test case where ScVolume instanceId is None
        mock_get_id.side_effect = ['64702.3494', None]
        res = self.scapi.map_volume(self.VOLUME,
                                    self.SCSERVER)
        self.assertFalse(mock_post.called)
        self.assertFalse(mock_first_result.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=[])
    def test_map_volume_failure(self,
                                mock_find_mapping_profiles,
                                mock_post,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        # Test case where mapping volume to server fails
        res = self.scapi.map_volume(self.VOLUME,
                                    self.SCSERVER)
        self.assertTrue(mock_find_mapping_profiles.called)
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=MAP_PROFILES)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value={'result': True})
    def test_unmap_volume(self,
                          mock_get_json,
                          mock_find_mapping_profiles,
                          mock_delete,
                          mock_close_connection,
                          mock_open_connection,
                          mock_init):
        res = self.scapi.unmap_volume(self.VOLUME,
                                      self.SCSERVER)
        self.assertTrue(mock_find_mapping_profiles.called)
        self.assertTrue(mock_delete.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=MAP_PROFILES)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_204)
    def test_unmap_volume_failure(self,
                                  mock_delete,
                                  mock_find_mapping_profiles,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        res = self.scapi.unmap_volume(self.VOLUME,
                                      self.SCSERVER)
        self.assertTrue(mock_find_mapping_profiles.called)
        self.assertTrue(mock_delete.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=[])
    def test_unmap_volume_no_map_profile(self,
                                         mock_find_mapping_profiles,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        res = self.scapi.unmap_volume(self.VOLUME,
                                      self.SCSERVER)
        self.assertTrue(mock_find_mapping_profiles.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_204)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=MAP_PROFILES)
    def test_unmap_volume_del_fail(self,
                                   mock_find_mapping_profiles,
                                   mock_delete,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi.unmap_volume(self.VOLUME,
                                      self.SCSERVER)
        self.assertTrue(mock_find_mapping_profiles.called)
        self.assertTrue(mock_delete.called)
        self.assertFalse(res, False)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=MAP_PROFILES)
    def test_unmap_volume_no_vol_id(self,
                                    mock_find_mapping_profiles,
                                    mock_delete,
                                    mock_get_id,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        # Test case where ScVolume instanceId = None
        mock_get_id.side_effect = [None, '64702.47']
        res = self.scapi.unmap_volume(self.VOLUME,
                                      self.SCSERVER)
        self.assertFalse(mock_find_mapping_profiles.called)
        self.assertFalse(mock_delete.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mapping_profiles',
                       return_value=MAP_PROFILES)
    def test_unmap_volume_no_server_id(self,
                                       mock_find_mapping_profiles,
                                       mock_delete,
                                       mock_get_id,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        # Test case where ScVolume instanceId = None
        mock_get_id.side_effect = ['64702.3494', None]
        res = self.scapi.unmap_volume(self.VOLUME,
                                      self.SCSERVER)
        self.assertFalse(mock_find_mapping_profiles.called)
        self.assertFalse(mock_delete.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[{'a': 1}, {'a': 2}])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_controller_port_iscsi_config(self,
                                               mock_get,
                                               mock_get_json,
                                               mock_close_connection,
                                               mock_open_connection,
                                               mock_init):
        # Not much to test here.  Just make sure we call our stuff and
        # that we return the first item returned to us.
        res = self.scapi._find_controller_port_iscsi_config('guid')
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual({'a': 1}, res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_find_controller_port_iscsi_config_err(self,
                                                   mock_get,
                                                   mock_close_connection,
                                                   mock_open_connection,
                                                   mock_init):
        res = self.scapi._find_controller_port_iscsi_config('guid')
        self.assertTrue(mock_get.called)
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=STRG_USAGE)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_get_storage_usage(self,
                               mock_get,
                               mock_get_json,
                               mock_close_connection,
                               mock_open_connection,
                               mock_init):
        res = self.scapi.get_storage_usage()
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.STRG_USAGE, res, 'Unexpected ScStorageUsage')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_204)
    def test_get_storage_usage_no_ssn(self,
                                      mock_get,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        # Test case where SSN is none
        self.scapi.ssn = None
        res = self.scapi.get_storage_usage()
        self.scapi.ssn = 12345
        self.assertFalse(mock_get.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_204)
    # Test case where get of Storage Usage fails
    def test_get_storage_usage_failure(self,
                                       mock_get,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        res = self.scapi.get_storage_usage()
        self.assertTrue(mock_get.called)
        self.assertIsNone(res, 'None expected')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=RPLAY)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_replay(self,
                           mock_post,
                           mock_first_result,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi.create_replay(self.VOLUME,
                                       'Test Replay',
                                       60)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.RPLAY, res, 'Unexpected ScReplay')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=RPLAY)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_init_volume')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_replay_inact_vol(self,
                                     mock_post,
                                     mock_init_volume,
                                     mock_first_result,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test case where the specified volume is inactive
        res = self.scapi.create_replay(self.INACTIVE_VOLUME,
                                       'Test Replay',
                                       60)
        self.assertTrue(mock_post.called)
        mock_init_volume.assert_called_once_with(self.INACTIVE_VOLUME)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.RPLAY, res, 'Unexpected ScReplay')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=RPLAY)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_replay_no_expire(self,
                                     mock_post,
                                     mock_first_result,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        res = self.scapi.create_replay(self.VOLUME,
                                       'Test Replay',
                                       0)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.RPLAY, res, 'Unexpected ScReplay')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_replay_no_volume(self,
                                     mock_post,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test case where no ScVolume is specified
        res = self.scapi.create_replay(None,
                                       'Test Replay',
                                       60)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_create_replay_failure(self,
                                   mock_post,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Test case where create ScReplay fails
        res = self.scapi.create_replay(self.VOLUME,
                                       'Test Replay',
                                       60)
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=RPLAYS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_replay(self,
                         mock_post,
                         mock_get_json,
                         mock_close_connection,
                         mock_open_connection,
                         mock_init):
        res = self.scapi.find_replay(self.VOLUME,
                                     u'Cinder Test Replay012345678910')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.TST_RPLAY, res, 'Unexpected ScReplay')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_replay_no_replays(self,
                                    mock_post,
                                    mock_get_json,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        # Test case where no replays are found
        res = self.scapi.find_replay(self.VOLUME,
                                     u'Cinder Test Replay012345678910')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_204)
    def test_find_replay_failure(self,
                                 mock_post,
                                 mock_get_json,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        # Test case where None is returned for replays
        res = self.scapi.find_replay(self.VOLUME,
                                     u'Cinder Test Replay012345678910')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_replay',
                       return_value=RPLAYS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_delete_replay(self,
                           mock_post,
                           mock_find_replay,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        replayId = u'Cinder Test Replay012345678910'
        res = self.scapi.delete_replay(self.VOLUME,
                                       replayId)
        self.assertTrue(mock_post.called)
        mock_find_replay.assert_called_once_with(self.VOLUME, replayId)
        self.assertTrue(res, 'Expected True')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_replay',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_delete_replay_no_replay(self,
                                     mock_post,
                                     mock_find_replay,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        # Test case where specified ScReplay does not exist
        replayId = u'Cinder Test Replay012345678910'
        res = self.scapi.delete_replay(self.VOLUME,
                                       replayId)
        self.assertFalse(mock_post.called)
        mock_find_replay.assert_called_once_with(self.VOLUME, replayId)
        self.assertTrue(res, 'Expected True')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_replay',
                       return_value=TST_RPLAY)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_delete_replay_failure(self,
                                   mock_post,
                                   mock_find_replay,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Test case where delete ScReplay results in an error
        replayId = u'Cinder Test Replay012345678910'
        res = self.scapi.delete_replay(self.VOLUME,
                                       replayId)
        self.assertTrue(mock_post.called)
        mock_find_replay.assert_called_once_with(self.VOLUME, replayId)
        self.assertFalse(res, 'Expected False')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_view_volume(self,
                                mock_post,
                                mock_find_volume_folder,
                                mock_first_result,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        vol_name = u'Test_create_vol'
        res = self.scapi.create_view_volume(
            vol_name,
            self.TST_RPLAY,
            None)
        self.assertTrue(mock_post.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_view_volume_create_fldr(self,
                                            mock_post,
                                            mock_find_volume_folder,
                                            mock_first_result,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        # Test case where volume folder does not exist and must be created
        vol_name = u'Test_create_vol'
        res = self.scapi.create_view_volume(
            vol_name,
            self.TST_RPLAY,
            None)
        self.assertTrue(mock_post.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_create_view_volume_no_vol_fldr(self,
                                            mock_post,
                                            mock_find_volume_folder,
                                            mock_first_result,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        # Test case where volume folder does not exist and cannot be created
        vol_name = u'Test_create_vol'
        res = self.scapi.create_view_volume(
            vol_name,
            self.TST_RPLAY,
            None)
        self.assertTrue(mock_post.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder',
                       return_value=FLDR)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_create_view_volume_failure(self,
                                        mock_post,
                                        mock_find_volume_folder,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        # Test case where view volume create fails
        vol_name = u'Test_create_vol'
        res = self.scapi.create_view_volume(
            vol_name,
            self.TST_RPLAY,
            None)
        self.assertTrue(mock_post.called)
        mock_find_volume_folder.assert_called_once_with(True)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'create_view_volume',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'create_replay',
                       return_value=RPLAY)
    def test_create_cloned_volume(self,
                                  mock_create_replay,
                                  mock_create_view_volume,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        vol_name = u'Test_create_clone_vol'
        res = self.scapi.create_cloned_volume(
            vol_name,
            self.VOLUME,
            ['Daily'])
        mock_create_replay.assert_called_once_with(self.VOLUME,
                                                   'Cinder Clone Replay',
                                                   60)
        mock_create_view_volume.assert_called_once_with(
            vol_name,
            self.RPLAY,
            ['Daily'])
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'create_view_volume',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'create_replay')
    def test_create_cloned_volume_failure(self,
                                          mock_create_replay,
                                          mock_create_view_volume,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        # Test case where create cloned volumes fails because create_replay
        # fails
        vol_name = u'Test_create_clone_vol'
        mock_create_replay.return_value = None
        res = self.scapi.create_cloned_volume(
            vol_name,
            self.VOLUME,
            ['Daily'])
        mock_create_replay.assert_called_once_with(self.VOLUME,
                                                   'Cinder Clone Replay',
                                                   60)
        self.assertFalse(mock_create_view_volume.called)
        self.assertIsNone(res, 'Expected None')
        # Again buy let create_view_volume fail.
        mock_create_replay.return_value = self.RPLAY
        res = self.scapi.create_cloned_volume(
            vol_name,
            self.VOLUME,
            ['Daily'])
        mock_create_view_volume.assert_called_once_with(
            vol_name,
            self.RPLAY,
            ['Daily'])
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_expand_volume(self,
                           mock_post,
                           mock_get_json,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi.expand_volume(self.VOLUME, 550)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.VOLUME, res, 'Unexpected ScVolume')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_expand_volume_failure(self,
                                   mock_post,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi.expand_volume(self.VOLUME, 550)
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_rename_volume(self,
                           mock_post,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi.rename_volume(self.VOLUME, 'newname')
        self.assertTrue(mock_post.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_rename_volume_failure(self,
                                   mock_post,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi.rename_volume(self.VOLUME, 'newname')
        self.assertTrue(mock_post.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    def test_delete_server(self,
                           mock_delete,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        res = self.scapi._delete_server(self.SCSERVER)
        self.assertTrue(mock_delete.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    def test_delete_server_del_not_allowed(self,
                                           mock_delete,
                                           mock_close_connection,
                                           mock_open_connection,
                                           mock_init):
        # Test case where delete of ScServer not allowed
        res = self.scapi._delete_server(self.SCSERVER_NO_DEL)
        self.assertFalse(mock_delete.called)
        self.assertIsNone(res, 'Expected None')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value={'test': 'test'})
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_get_user_preferences(self,
                                  mock_get,
                                  mock_get_json,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        # Not really testing anything other than the ability to mock, but
        # including for completeness.
        res = self.scapi._get_user_preferences()
        self.assertEqual({'test': 'test'}, res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_get_user_preferences_failure(self,
                                          mock_get,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        res = self.scapi._get_user_preferences()
        self.assertEqual({}, res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_user_preferences',
                       return_value=None)
    def test_update_storage_profile_noprefs(self,
                                            mock_prefs,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        res = self.scapi.update_storage_profile(None, None)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_user_preferences',
                       return_value={'allowStorageProfileSelection': False})
    def test_update_storage_profile_not_allowed(self,
                                                mock_prefs,
                                                mock_close_connection,
                                                mock_open_connection,
                                                mock_init):
        LOG = self.mock_object(dell_storagecenter_api, "LOG")
        res = self.scapi.update_storage_profile(None, None)
        self.assertFalse(res)
        self.assertEqual(1, LOG.error.call_count)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_storage_profile',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_user_preferences',
                       return_value={'allowStorageProfileSelection': True})
    def test_update_storage_profile_prefs_not_found(self,
                                                    mock_profile,
                                                    mock_prefs,
                                                    mock_close_connection,
                                                    mock_open_connection,
                                                    mock_init):
        LOG = self.mock_object(dell_storagecenter_api, "LOG")
        res = self.scapi.update_storage_profile(None, 'Fake')
        self.assertFalse(res)
        self.assertEqual(1, LOG.error.call_count)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_user_preferences',
                       return_value={'allowStorageProfileSelection': True,
                                     'storageProfile': None})
    def test_update_storage_profile_default_not_found(self,
                                                      mock_prefs,
                                                      mock_close_connection,
                                                      mock_open_connection,
                                                      mock_init):
        LOG = self.mock_object(dell_storagecenter_api, "LOG")
        res = self.scapi.update_storage_profile(None, None)
        self.assertFalse(res)
        self.assertEqual(1, LOG.error.call_count)

    @mock.patch.object(
        dell_storagecenter_api.StorageCenterApi,
        '_get_user_preferences',
        return_value={'allowStorageProfileSelection': True,
                      'storageProfile': {'name': 'Fake',
                                         'instanceId': 'fakeId'}})
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_update_storage_profile(self,
                                    mock_post,
                                    mock_prefs,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        LOG = self.mock_object(dell_storagecenter_api, "LOG")
        fake_scvolume = {'name': 'name', 'instanceId': 'id'}
        res = self.scapi.update_storage_profile(fake_scvolume, None)
        self.assertTrue(res)
        self.assertTrue('fakeId' in repr(mock_post.call_args_list[0]))
        self.assertEqual(1, LOG.info.call_count)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[RPLAY_PROFILE])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_replay_profile(self,
                                 mock_post,
                                 mock_get_json,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        res = self.scapi.find_replay_profile('guid')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertEqual(self.RPLAY_PROFILE, res, 'Unexpected Profile')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[RPLAY_PROFILE, RPLAY_PROFILE])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_replay_profile_more_than_one(self,
                                               mock_post,
                                               mock_get_json,
                                               mock_close_connection,
                                               mock_open_connection,
                                               mock_init):
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.find_replay_profile,
                          'guid')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_find_replay_profile_empty_list(self,
                                            mock_post,
                                            mock_get_json,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):
        res = self.scapi.find_replay_profile('guid')
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_get_json.called)
        self.assertIsNone(res, 'Unexpected return')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_find_replay_profile_error(self,
                                       mock_post,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        res = self.scapi.find_replay_profile('guid')
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'Unexpected return')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_replay_profile',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=RPLAY_PROFILE)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_201)
    def test_create_replay_profile(self,
                                   mock_post,
                                   mock_first_result,
                                   mock_find_replay_profile,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        res = self.scapi.create_replay_profile('guid')
        self.assertTrue(mock_find_replay_profile.called)
        self.assertTrue(mock_post.called)
        self.assertTrue(mock_first_result.called)
        self.assertEqual(self.RPLAY_PROFILE, res, 'Unexpected Profile')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_replay_profile',
                       return_value=RPLAY_PROFILE)
    def test_create_replay_profile_exists(self,
                                          mock_find_replay_profile,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        res = self.scapi.create_replay_profile('guid')
        self.assertTrue(mock_find_replay_profile.called)
        self.assertEqual(self.RPLAY_PROFILE, res, 'Unexpected Profile')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_replay_profile',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_create_replay_profile_fail(self,
                                        mock_post,
                                        mock_find_replay_profile,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        res = self.scapi.create_replay_profile('guid')
        self.assertTrue(mock_find_replay_profile.called)
        self.assertTrue(mock_post.called)
        self.assertIsNone(res, 'Unexpected return')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    def test_delete_replay_profile(self,
                                   mock_get_id,
                                   mock_delete,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        profile = {'name': 'guid'}
        self.scapi.delete_replay_profile(profile)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_delete.called)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_400)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    def test_delete_replay_profile_fail(self,
                                        mock_get_id,
                                        mock_delete,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        profile = {'name': 'guid'}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.delete_replay_profile,
                          profile)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_delete.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_first_result',
                       return_value=VOLUME_CONFIG)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    def test_get_volume_configuration(self,
                                      mock_get_id,
                                      mock_get,
                                      mock_first_result,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        res = self.scapi._get_volume_configuration({})
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_get.called)
        self.assertEqual(self.VOLUME_CONFIG, res, 'Unexpected config')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    def test_get_volume_configuration_bad_response(self,
                                                   mock_get_id,
                                                   mock_get,
                                                   mock_close_connection,
                                                   mock_open_connection,
                                                   mock_init):
        res = self.scapi._get_volume_configuration({})
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_get.called)
        self.assertIsNone(res, 'Unexpected result')

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_configuration',
                       return_value=VOLUME_CONFIG)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    def test_update_volume_profiles(self,
                                    mock_get_id,
                                    mock_put,
                                    mock_get_volume_configuration,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        scvolume = {'instanceId': '1'}
        existingid = self.VOLUME_CONFIG[u'replayProfileList'][0][u'instanceId']
        vcid = self.VOLUME_CONFIG[u'instanceId']
        # First get_id is for our existing replay profile id and the second
        # is for the volume config and the last is for the volume id.  And
        # then we do this again for the second call below.
        mock_get_id.side_effect = [existingid,
                                   vcid,
                                   scvolume['instanceId'],
                                   existingid,
                                   vcid,
                                   scvolume['instanceId']]
        newid = '64702.1'
        expected_payload = {'ReplayProfileList': [newid, existingid]}
        expected_url = 'StorageCenter/ScVolumeConfiguration/' + vcid
        res = self.scapi._update_volume_profiles(scvolume, newid, None)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_get_volume_configuration.called)
        mock_put.assert_called_once_with(expected_url,
                                         expected_payload)
        self.assertTrue(res)

        # Now do a remove.  (Restarting with the original config so this will
        # end up as an empty list.)
        expected_payload['ReplayProfileList'] = []
        res = self.scapi._update_volume_profiles(scvolume, None, existingid)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_get_volume_configuration.called)
        mock_put.assert_called_with(expected_url,
                                    expected_payload)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_configuration',
                       return_value=VOLUME_CONFIG)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put',
                       return_value=RESPONSE_400)
    # We set this to 1 so we can check our payload
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id')
    def test_update_volume_profiles_bad_response(self,
                                                 mock_get_id,
                                                 mock_put,
                                                 mock_get_volume_configuration,
                                                 mock_close_connection,
                                                 mock_open_connection,
                                                 mock_init):
        scvolume = {'instanceId': '1'}
        existingid = self.VOLUME_CONFIG[u'replayProfileList'][0][u'instanceId']
        vcid = self.VOLUME_CONFIG[u'instanceId']
        # First get_id is for our existing replay profile id and the second
        # is for the volume config and the last is for the volume id.  And
        # then we do this again for the second call below.
        mock_get_id.side_effect = [existingid,
                                   vcid,
                                   scvolume['instanceId'],
                                   existingid,
                                   vcid,
                                   scvolume['instanceId']]
        newid = '64702.1'
        expected_payload = {'ReplayProfileList': [newid, existingid]}
        expected_url = 'StorageCenter/ScVolumeConfiguration/' + vcid
        res = self.scapi._update_volume_profiles(scvolume, newid, None)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_get_volume_configuration.called)
        mock_put.assert_called_once_with(expected_url,
                                         expected_payload)
        self.assertFalse(res)

        # Now do a remove.  (Restarting with the original config so this will
        # end up as an empty list.)
        expected_payload['ReplayProfileList'] = []
        res = self.scapi._update_volume_profiles(scvolume, None, existingid)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_get_volume_configuration.called)
        mock_put.assert_called_with(expected_url,
                                    expected_payload)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_configuration',
                       return_value=None)
    def test_update_volume_profiles_no_config(self,
                                              mock_get_volume_configuration,
                                              mock_close_connection,
                                              mock_open_connection,
                                              mock_init):
        scvolume = {'instanceId': '1'}
        res = self.scapi._update_volume_profiles(scvolume, '64702.2', None)
        self.assertTrue(mock_get_volume_configuration.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=999)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_update_volume_profiles',
                       return_value=True)
    def test_add_cg_volumes(self,
                            mock_update_volume_profiles,
                            mock_find_volume,
                            mock_close_connection,
                            mock_open_connection,
                            mock_init):
        profileid = '100'
        add_volumes = [{'id': '1'}]
        res = self.scapi._add_cg_volumes(profileid, add_volumes)
        self.assertTrue(mock_find_volume.called)
        mock_update_volume_profiles.assert_called_once_with(999,
                                                            addid=profileid,
                                                            removeid=None)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=999)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_update_volume_profiles',
                       return_value=False)
    def test_add_cg_volumes_fail(self,
                                 mock_update_volume_profiles,
                                 mock_find_volume,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        profileid = '100'
        add_volumes = [{'id': '1'}]
        res = self.scapi._add_cg_volumes(profileid, add_volumes)
        self.assertTrue(mock_find_volume.called)
        mock_update_volume_profiles.assert_called_once_with(999,
                                                            addid=profileid,
                                                            removeid=None)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=999)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_update_volume_profiles',
                       return_value=True)
    def test_remove_cg_volumes(self,
                               mock_update_volume_profiles,
                               mock_find_volume,
                               mock_close_connection,
                               mock_open_connection,
                               mock_init):
        profileid = '100'
        remove_volumes = [{'id': '1'}]
        res = self.scapi._remove_cg_volumes(profileid, remove_volumes)
        self.assertTrue(mock_find_volume.called)
        mock_update_volume_profiles.assert_called_once_with(999,
                                                            addid=None,
                                                            removeid=profileid)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume',
                       return_value=999)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_update_volume_profiles',
                       return_value=False)
    def test_remove_cg_volumes_false(self,
                                     mock_update_volume_profiles,
                                     mock_find_volume,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        profileid = '100'
        remove_volumes = [{'id': '1'}]
        res = self.scapi._remove_cg_volumes(profileid, remove_volumes)
        self.assertTrue(mock_find_volume.called)
        mock_update_volume_profiles.assert_called_once_with(999,
                                                            addid=None,
                                                            removeid=profileid)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_remove_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_update_cg_volumes(self,
                               mock_get_id,
                               mock_add_cg_volumes,
                               mock_remove_cg_volumes,
                               mock_close_connection,
                               mock_open_connection,
                               mock_init):
        profile = {'name': 'guid'}
        add_volumes = [{'id': '1'}]
        remove_volumes = [{'id': '2'}]
        res = self.scapi.update_cg_volumes(profile,
                                           add_volumes,
                                           remove_volumes)
        self.assertTrue(mock_get_id.called)
        mock_add_cg_volumes.assert_called_once_with('100', add_volumes)
        mock_remove_cg_volumes.assert_called_once_with('100',
                                                       remove_volumes)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_remove_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_update_cg_volumes_no_remove(self,
                                         mock_get_id,
                                         mock_add_cg_volumes,
                                         mock_remove_cg_volumes,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        profile = {'name': 'guid'}
        add_volumes = [{'id': '1'}]
        remove_volumes = []
        res = self.scapi.update_cg_volumes(profile,
                                           add_volumes,
                                           remove_volumes)
        self.assertTrue(mock_get_id.called)
        mock_add_cg_volumes.assert_called_once_with('100', add_volumes)
        self.assertFalse(mock_remove_cg_volumes.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_remove_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_update_cg_volumes_no_add(self,
                                      mock_get_id,
                                      mock_add_cg_volumes,
                                      mock_remove_cg_volumes,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        profile = {'name': 'guid'}
        add_volumes = []
        remove_volumes = [{'id': '1'}]
        res = self.scapi.update_cg_volumes(profile,
                                           add_volumes,
                                           remove_volumes)
        self.assertTrue(mock_get_id.called)
        mock_remove_cg_volumes.assert_called_once_with('100', remove_volumes)
        self.assertFalse(mock_add_cg_volumes.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_remove_cg_volumes')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_cg_volumes',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_update_cg_volumes_add_fail(self,
                                        mock_get_id,
                                        mock_add_cg_volumes,
                                        mock_remove_cg_volumes,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        profile = {'name': 'guid'}
        add_volumes = [{'id': '1'}]
        remove_volumes = [{'id': '2'}]
        res = self.scapi.update_cg_volumes(profile,
                                           add_volumes,
                                           remove_volumes)
        self.assertTrue(mock_get_id.called)
        mock_add_cg_volumes.assert_called_once_with('100', add_volumes)
        self.assertTrue(not mock_remove_cg_volumes.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_remove_cg_volumes',
                       return_value=False)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_add_cg_volumes',
                       return_value=True)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_update_cg_volumes_remove_fail(self,
                                           mock_get_id,
                                           mock_add_cg_volumes,
                                           mock_remove_cg_volumes,
                                           mock_close_connection,
                                           mock_open_connection,
                                           mock_init):
        profile = {'name': 'guid'}
        add_volumes = [{'id': '1'}]
        remove_volumes = [{'id': '2'}]
        res = self.scapi.update_cg_volumes(profile,
                                           add_volumes,
                                           remove_volumes)
        self.assertTrue(mock_get_id.called)
        mock_add_cg_volumes.assert_called_once_with('100', add_volumes)
        mock_remove_cg_volumes.assert_called_once_with('100',
                                                       remove_volumes)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[INACTIVE_VOLUME])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_init_volume')
    def test_init_cg_volumes_inactive(self,
                                      mock_init_volume,
                                      mock_get_json,
                                      mock_get,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        profileid = 100
        self.scapi._init_cg_volumes(profileid)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        mock_init_volume.assert_called_once_with(self.INACTIVE_VOLUME)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[VOLUME])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_init_volume')
    def test_init_cg_volumes_active(self,
                                    mock_init_volume,
                                    mock_get_json,
                                    mock_get,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        profileid = 100
        self.scapi._init_cg_volumes(profileid)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_get_json.called)
        self.assertFalse(mock_init_volume.called)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_init_cg_volumes')
    def test_snap_cg_replay(self,
                            mock_init_cg_volumes,
                            mock_get_id,
                            mock_post,
                            mock_close_connection,
                            mock_open_connection,
                            mock_init):
        replayid = 'guid'
        expire = 0
        profile = {'instanceId': '100'}
        # See the 100 from get_id above?
        expected_url = 'StorageCenter/ScReplayProfile/100/CreateReplay'
        expected_payload = {'description': replayid, 'expireTime': expire}
        res = self.scapi.snap_cg_replay(profile, replayid, expire)
        mock_post.assert_called_once_with(expected_url, expected_payload)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_init_cg_volumes.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_init_cg_volumes')
    def test_snap_cg_replay_bad_return(self,
                                       mock_init_cg_volumes,
                                       mock_get_id,
                                       mock_post,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        replayid = 'guid'
        expire = 0
        profile = {'instanceId': '100'}
        # See the 100 from get_id above?
        expected_url = 'StorageCenter/ScReplayProfile/100/CreateReplay'
        expected_payload = {'description': replayid, 'expireTime': expire}
        res = self.scapi.snap_cg_replay(profile, replayid, expire)
        mock_post.assert_called_once_with(expected_url, expected_payload)
        self.assertTrue(mock_get_id.called)
        self.assertTrue(mock_init_cg_volumes.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=CGS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_sc_cg(self,
                        mock_get,
                        mock_get_json,
                        mock_close_connection,
                        mock_open_connection,
                        mock_init):
        res = self.scapi._find_sc_cg(
            {},
            'GUID1-0869559e-6881-454e-ba18-15c6726d33c1')
        self.assertEqual(self.CGS[0], res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=CGS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    def test_find_sc_cg_not_found(self,
                                  mock_get,
                                  mock_get_json,
                                  mock_close_connection,
                                  mock_open_connection,
                                  mock_init):
        res = self.scapi._find_sc_cg(
            {},
            'GUID3-0869559e-6881-454e-ba18-15c6726d33c1')
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_find_sc_cg_fail(self,
                             mock_get,
                             mock_close_connection,
                             mock_open_connection,
                             mock_init):
        res = self.scapi._find_sc_cg(
            {},
            'GUID1-0869559e-6881-454e-ba18-15c6726d33c1')
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_sc_cg',
                       return_value={'instanceId': 101})
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=RPLAYS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get')
    def test_find_cg_replays(self,
                             mock_get,
                             mock_get_json,
                             mock_find_sc_cg,
                             mock_close_connection,
                             mock_open_connection,
                             mock_init):
        profile = {'instanceId': '100'}
        replayid = 'Cinder Test Replay012345678910'
        res = self.scapi._find_cg_replays(profile, replayid)
        expected_url = 'StorageCenter/ScReplayConsistencyGroup/101/ReplayList'
        mock_get.assert_called_once_with(expected_url)
        self.assertTrue(mock_find_sc_cg.called)
        self.assertTrue(mock_get_json.called)
        # We should fine RPLAYS
        self.assertEqual(self.RPLAYS, res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_sc_cg',
                       return_value=None)
    def test_find_cg_replays_no_cg(self,
                                   mock_find_sc_cg,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        profile = {'instanceId': '100'}
        replayid = 'Cinder Test Replay012345678910'
        res = self.scapi._find_cg_replays(profile, replayid)
        self.assertTrue(mock_find_sc_cg.called)
        # We should return an empty list.
        self.assertEqual([], res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_sc_cg',
                       return_value={'instanceId': 101})
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=None)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get')
    def test_find_cg_replays_bad_json(self,
                                      mock_get,
                                      mock_get_json,
                                      mock_find_sc_cg,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        profile = {'instanceId': '100'}
        replayid = 'Cinder Test Replay012345678910'
        res = self.scapi._find_cg_replays(profile, replayid)
        expected_url = 'StorageCenter/ScReplayConsistencyGroup/101/ReplayList'
        mock_get.assert_called_once_with(expected_url)
        self.assertTrue(mock_find_sc_cg.called)
        self.assertTrue(mock_get_json.called)
        self.assertIsNone(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_cg_replays',
                       return_value=RPLAYS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_delete_cg_replay(self,
                              mock_post,
                              mock_find_cg_replays,
                              mock_close_connection,
                              mock_open_connection,
                              mock_init):
        res = self.scapi.delete_cg_replay({}, '')
        expected_url = ('StorageCenter/ScReplay/' +
                        self.RPLAYS[0]['instanceId'] +
                        '/Expire')
        mock_post.assert_any_call(expected_url, {})
        expected_url = ('StorageCenter/ScReplay/' +
                        self.RPLAYS[1]['instanceId'] +
                        '/Expire')
        mock_post.assert_any_call(expected_url, {})
        self.assertTrue(mock_find_cg_replays.called)
        self.assertTrue(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_cg_replays',
                       return_value=RPLAYS)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_delete_cg_replay_error(self,
                                    mock_post,
                                    mock_find_cg_replays,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        expected_url = ('StorageCenter/ScReplay/' +
                        self.RPLAYS[0]['instanceId'] +
                        '/Expire')
        res = self.scapi.delete_cg_replay({}, '')
        mock_post.assert_called_once_with(expected_url, {})
        self.assertTrue(mock_find_cg_replays.called)
        self.assertFalse(res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_cg_replays',
                       return_value=[])
    def test_delete_cg_replay_cant_find(self,
                                        mock_find_cg_replays,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        res = self.scapi.delete_cg_replay({}, '')
        self.assertTrue(mock_find_cg_replays.called)
        self.assertTrue(res)

    def test_size_to_gb(self,
                        mock_close_connection,
                        mock_open_connection,
                        mock_init):
        gb, rem = self.scapi.size_to_gb('1.073741824E9 Byte')
        self.assertEqual(1, gb)
        self.assertEqual(0, rem)
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.size_to_gb,
                          'banana')
        gb, rem = self.scapi.size_to_gb('1.073741924E9 Byte')
        self.assertEqual(1, gb)
        self.assertEqual(100, rem)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_volume_folder')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=VOLUME)
    def test_import_one(self,
                        mock_get_json,
                        mock_put,
                        mock_find_volume_folder,
                        mock_close_connection,
                        mock_open_connection,
                        mock_init):
        newname = 'guid'
        # First test is folder found.  Second ist is not found.
        mock_find_volume_folder.side_effect = [{'instanceId': '1'}, None]
        expected_url = 'StorageCenter/ScVolume/100'
        expected_payload = {'Name': newname,
                            'VolumeFolder': '1'}
        self.scapi._import_one({'instanceId': '100'}, newname)
        mock_put.assert_called_once_with(expected_url, expected_payload)
        self.assertTrue(mock_find_volume_folder.called)
        expected_payload = {'Name': newname}
        self.scapi._import_one({'instanceId': '100'}, newname)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{'configuredSize':
                                      '1.073741824E9 Bytes'}])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'size_to_gb',
                       return_value=(1, 0))
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_import_one',
                       return_value=VOLUME)
    def test_manage_existing(self,
                             mock_import_one,
                             mock_find_mappings,
                             mock_size_to_gb,
                             mock_get_volume_list,
                             mock_close_connection,
                             mock_open_connection,
                             mock_init):
        newname = 'guid'
        existing = {'source-name': 'scvolname'}
        self.scapi.manage_existing(newname, existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'), None, False)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_size_to_gb.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[])
    def test_manage_existing_vol_not_found(self,
                                           mock_get_volume_list,
                                           mock_close_connection,
                                           mock_open_connection,
                                           mock_init):

        # Same as above only we don't have a volume folder.
        newname = 'guid'
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.ManageExistingInvalidReference,
                          self.scapi.manage_existing,
                          newname,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{}, {}, {}])
    def test_manage_existing_vol_multiple_found(self,
                                                mock_get_volume_list,
                                                mock_close_connection,
                                                mock_open_connection,
                                                mock_init):

        # Same as above only we don't have a volume folder.
        newname = 'guid'
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.ManageExistingInvalidReference,
                          self.scapi.manage_existing,
                          newname,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{'configuredSize':
                                      '1.073741924E9 Bytes'}])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'size_to_gb',
                       return_value=(1, 100))
    def test_manage_existing_bad_size(self,
                                      mock_size_to_gb,
                                      mock_get_volume_list,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):

        # Same as above only we don't have a volume folder.
        newname = 'guid'
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.manage_existing,
                          newname,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)
        self.assertTrue(mock_size_to_gb.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{'configuredSize':
                                      '1.073741824E9 Bytes'}])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'size_to_gb',
                       return_value=(1, 0))
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=[{}, {}])
    def test_manage_existing_already_mapped(self,
                                            mock_find_mappings,
                                            mock_size_to_gb,
                                            mock_get_volume_list,
                                            mock_close_connection,
                                            mock_open_connection,
                                            mock_init):

        newname = 'guid'
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.manage_existing,
                          newname,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_size_to_gb.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{'configuredSize':
                                      '1.073741824E9 Bytes'}])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'size_to_gb',
                       return_value=(1, 0))
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_mappings',
                       return_value=[])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_import_one',
                       return_value=None)
    def test_manage_existing_import_fail(self,
                                         mock_import_one,
                                         mock_find_mappings,
                                         mock_size_to_gb,
                                         mock_get_volume_list,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        # We fail on the _find_volume_folder to make this easier.
        newname = 'guid'
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.manage_existing,
                          newname,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)
        self.assertTrue(mock_find_mappings.called)
        self.assertTrue(mock_size_to_gb.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{'configuredSize':
                                      '1.073741824E9 Bytes'}])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'size_to_gb',
                       return_value=(1, 0))
    def test_get_unmanaged_volume_size(self,
                                       mock_size_to_gb,
                                       mock_get_volume_list,
                                       mock_close_connection,
                                       mock_open_connection,
                                       mock_init):
        existing = {'source-name': 'scvolname'}
        res = self.scapi.get_unmanaged_volume_size(existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)
        self.assertTrue(mock_size_to_gb.called)
        self.assertEqual(1, res)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[])
    def test_get_unmanaged_volume_size_not_found(self,
                                                 mock_get_volume_list,
                                                 mock_close_connection,
                                                 mock_open_connection,
                                                 mock_init):
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.ManageExistingInvalidReference,
                          self.scapi.get_unmanaged_volume_size,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{}, {}, {}])
    def test_get_unmanaged_volume_size_many_found(self,
                                                  mock_get_volume_list,
                                                  mock_close_connection,
                                                  mock_open_connection,
                                                  mock_init):
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.ManageExistingInvalidReference,
                          self.scapi.get_unmanaged_volume_size,
                          existing)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_volume_list',
                       return_value=[{'configuredSize':
                                      '1.073741924E9 Bytes'}])
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'size_to_gb',
                       return_value=(1, 100))
    def test_get_unmanaged_volume_size_bad_size(self,
                                                mock_size_to_gb,
                                                mock_get_volume_list,
                                                mock_close_connection,
                                                mock_open_connection,
                                                mock_init):
        existing = {'source-name': 'scvolname'}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.get_unmanaged_volume_size,
                          existing)
        self.assertTrue(mock_size_to_gb.called)
        mock_get_volume_list.assert_called_once_with(
            existing.get('source-name'),
            existing.get('source-id'),
            False)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_unmanage(self,
                      mock_get_id,
                      mock_put,
                      mock_close_connection,
                      mock_open_connection,
                      mock_init):
        # Same as above only we don't have a volume folder.
        scvolume = {'name': 'guid'}
        expected_url = 'StorageCenter/ScVolume/100'
        newname = 'Unmanaged_' + scvolume['name']
        expected_payload = {'Name': newname}
        self.scapi.unmanage(scvolume)
        self.assertTrue(mock_get_id.called)
        mock_put.assert_called_once_with(expected_url, expected_payload)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put',
                       return_value=RESPONSE_400)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_id',
                       return_value='100')
    def test_unmanage_fail(self,
                           mock_get_id,
                           mock_put,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        # Same as above only we don't have a volume folder.
        scvolume = {'name': 'guid'}
        expected_url = 'StorageCenter/ScVolume/100'
        newname = 'Unmanaged_' + scvolume['name']
        expected_payload = {'Name': newname}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.unmanage,
                          scvolume)
        self.assertTrue(mock_get_id.called)
        mock_put.assert_called_once_with(expected_url, expected_payload)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[SCQOS])
    # def _find_qos(self, qosnode):
    def test__find_qos(self,
                       mock_get_json,
                       mock_post,
                       mock_close_connection,
                       mock_open_connection,
                       mock_init):
        ret = self.scapi._find_qos('Cinder QoS')
        self.assertDictEqual(self.SCQOS, ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json')
    # def _find_qos(self, qosnode):
    def test__find_qos_not_found(self,
                                 mock_get_json,
                                 mock_post,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        # set side effect for posts.
        # first empty second returns qosnode
        mock_get_json.side_effect = [[], self.SCQOS]
        ret = self.scapi._find_qos('Cinder QoS')
        self.assertDictEqual(self.SCQOS, ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    # def _find_qos(self, qosnode):
    def test__find_qos_find_fail(self,
                                 mock_post,
                                 mock_close_connection,
                                 mock_open_connection,
                                 mock_init):
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi._find_qos,
                          'Cinder QoS')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    # def _find_qos(self, qosnode):
    def test__find_qos_create_fail(self,
                                   mock_get_json,
                                   mock_post,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        mock_post.side_effect = [self.RESPONSE_200, self.RESPONSE_400]
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi._find_qos,
                          'Cinder QoS')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SCREPL)
    def test_get_screplication(self,
                               mock_get_json,
                               mock_get,
                               mock_close_connection,
                               mock_open_connection,
                               mock_init):
        ret = self.scapi.get_screplication({'instanceId': '1'}, 65495)
        self.assertDictEqual(self.SCREPL[0], ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    def test_get_screplication_not_found(self,
                                         mock_get_json,
                                         mock_get,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        ret = self.scapi.get_screplication({'instanceId': '1'}, 65496)
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'get',
                       return_value=RESPONSE_400)
    def test_get_screplication_error(self,
                                     mock_get,
                                     mock_close_connection,
                                     mock_open_connection,
                                     mock_init):
        ret = self.scapi.get_screplication({'instanceId': '1'}, 65495)
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'get_screplication',
                       return_value=SCREPL[0])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_200)
    def test_delete_replication(self,
                                mock_delete,
                                mock_get_screplication,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        destssn = 65495
        expected = 'StorageCenter/ScReplication/%s' % (
            self.SCREPL[0]['instanceId'])
        ret = self.scapi.delete_replication(self.VOLUME, destssn)
        mock_delete.assert_any_call(expected)
        self.assertTrue(ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'get_screplication',
                       return_value=None)
    def test_delete_replication_not_found(self,
                                          mock_get_screplication,
                                          mock_close_connection,
                                          mock_open_connection,
                                          mock_init):
        destssn = 65495
        ret = self.scapi.delete_replication(self.VOLUME, destssn)
        self.assertFalse(ret)
        ret = self.scapi.delete_replication(self.VOLUME, destssn)
        self.assertFalse(ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'get_screplication',
                       return_value=SCREPL[0])
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'delete',
                       return_value=RESPONSE_400)
    def test_delete_replication_error(self,
                                      mock_delete,
                                      mock_get_screplication,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        destssn = 65495
        expected = 'StorageCenter/ScReplication/%s' % (
            self.SCREPL[0]['instanceId'])
        ret = self.scapi.delete_replication(self.VOLUME, destssn)
        mock_delete.assert_any_call(expected)
        self.assertFalse(ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_qos',
                       return_value=SCQOS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_sc')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SCREPL[0])
    def test_create_replication(self,
                                mock_get_json,
                                mock_post,
                                mock_find_sc,
                                mock_find_qos,
                                mock_close_connection,
                                mock_open_connection,
                                mock_init):
        # We don't test diskfolder. If one is found we include it. If not
        # then we leave it out. Checking for disk folder is tested elsewhere.
        ssn = 64702
        destssn = 65495
        qosnode = 'Cinder QoS'
        notes = 'Created by Dell Cinder Driver'
        repl_prefix = 'Cinder repl of '

        mock_find_sc.side_effect = [destssn, ssn, destssn, ssn, destssn, ssn]
        payload = {'DestinationStorageCenter': destssn,
                   'QosNode': self.SCQOS['instanceId'],
                   'SourceVolume': self.VOLUME['instanceId'],
                   'StorageCenter': ssn,
                   'ReplicateActiveReplay': False,
                   'Type': 'Asynchronous',
                   'DestinationVolumeAttributes':
                       {'CreateSourceVolumeFolderPath': True,
                        'Notes': notes,
                        'Name': repl_prefix + self.VOLUME['name']}
                   }
        ret = self.scapi.create_replication(self.VOLUME,
                                            str(destssn),
                                            qosnode,
                                            False,
                                            None,
                                            False)
        mock_post.assert_any_call('StorageCenter/ScReplication', payload)
        self.assertDictEqual(self.SCREPL[0], ret)
        payload['Type'] = 'Synchronous'
        payload['ReplicateActiveReplay'] = True
        payload['SyncMode'] = 'HighAvailability'
        ret = self.scapi.create_replication(self.VOLUME,
                                            str(destssn),
                                            qosnode,
                                            True,
                                            None,
                                            False)
        mock_post.assert_any_call('StorageCenter/ScReplication', payload)
        self.assertDictEqual(self.SCREPL[0], ret)
        ret = self.scapi.create_replication(self.VOLUME,
                                            str(destssn),
                                            qosnode,
                                            True,
                                            None,
                                            True)
        mock_post.assert_any_call('StorageCenter/ScReplication', payload)
        self.assertDictEqual(self.SCREPL[0], ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_qos',
                       return_value=SCQOS)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_sc')
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SCREPL[0])
    def test_create_replication_error(self,
                                      mock_get_json,
                                      mock_post,
                                      mock_find_sc,
                                      mock_find_qos,
                                      mock_close_connection,
                                      mock_open_connection,
                                      mock_init):
        ssn = 64702
        destssn = 65495
        qosnode = 'Cinder QoS'
        notes = 'Created by Dell Cinder Driver'
        repl_prefix = 'Cinder repl of '

        mock_find_sc.side_effect = [destssn, ssn, destssn, ssn]
        mock_post.side_effect = [self.RESPONSE_400, self.RESPONSE_400,
                                 self.RESPONSE_400, self.RESPONSE_400]
        payload = {'DestinationStorageCenter': destssn,
                   'QosNode': self.SCQOS['instanceId'],
                   'SourceVolume': self.VOLUME['instanceId'],
                   'StorageCenter': ssn,
                   'ReplicateActiveReplay': False,
                   'Type': 'Asynchronous',
                   'DestinationVolumeAttributes':
                       {'CreateSourceVolumeFolderPath': True,
                        'Notes': notes,
                        'Name': repl_prefix + self.VOLUME['name']}
                   }
        ret = self.scapi.create_replication(self.VOLUME,
                                            str(destssn),
                                            qosnode,
                                            False,
                                            None,
                                            False)
        mock_post.assert_any_call('StorageCenter/ScReplication', payload)
        self.assertIsNone(ret)

        payload['Type'] = 'Synchronous'
        payload['ReplicateActiveReplay'] = True
        payload['SyncMode'] = 'HighAvailability'
        ret = self.scapi.create_replication(self.VOLUME,
                                            str(destssn),
                                            qosnode,
                                            True,
                                            None,
                                            True)
        mock_post.assert_any_call('StorageCenter/ScReplication', payload)
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=SCREPL)
    def test_find_repl_volume(self,
                              mock_get_json,
                              mock_post,
                              mock_close_connection,
                              mock_open_connection,
                              mock_init):
        ret = self.scapi.find_repl_volume('guid', 65495)
        self.assertDictEqual(self.SCREPL[0], ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[])
    def test_find_repl_volume_empty_list(self,
                                         mock_get_json,
                                         mock_post,
                                         mock_close_connection,
                                         mock_open_connection,
                                         mock_init):
        ret = self.scapi.find_repl_volume('guid', 65495)
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=[{'instanceId': '1'}, {'instanceId': '2'}])
    def test_find_repl_volume_multiple_results(self,
                                               mock_get_json,
                                               mock_post,
                                               mock_close_connection,
                                               mock_open_connection,
                                               mock_init):
        ret = self.scapi.find_repl_volume('guid', 65495)
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_find_repl_volume_error(self,
                                    mock_post,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        ret = self.scapi.find_repl_volume('guid', 65495)
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'get_screplication')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_repl_volume')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'find_volume')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       'remove_mappings')
    def test_break_replication(self,
                               mock_remove_mappings,
                               mock_find_volume,
                               mock_find_repl_volume,
                               mock_get_screplication,
                               mock_close_connection,
                               mock_open_connection,
                               mock_init):
        # Find_volume doesn't actually matter.  We do not gate on this.
        # Switch it up just to prove that.
        mock_find_volume.side_effect = [self.VOLUME,    # 1
                                        self.VOLUME,    # 2
                                        None,           # 3
                                        None]           # 4
        # Much like find volume we do not gate on this.
        mock_get_screplication.side_effect = [self.SCREPL[0],  # 1
                                              None,            # 2
                                              None,            # 3
                                              None]            # 4
        # This
        mock_find_repl_volume.side_effect = [self.VOLUME,   # 1
                                             self.VOLUME,   # 2
                                             self.VOLUME,   # 3
                                             self.VOLUME]   # 4
        mock_remove_mappings.side_effect = [True,   # 1
                                            True,
                                            True,   # 2
                                            False,
                                            True,   # 3
                                            True,
                                            False]  # 4

        # Good path.
        ret = self.scapi.break_replication('name', 65495)
        self.assertTrue(ret)
        # Source found, screpl not found.
        ret = self.scapi.break_replication('name', 65495)
        self.assertTrue(ret)
        # No source vol good path.
        ret = self.scapi.break_replication('name', 65495)
        self.assertTrue(ret)
        # fail remove mappings
        ret = self.scapi.break_replication('name', 65495)
        self.assertFalse(ret)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_user_preferences')
    def test__find_user_replay_profiles(self,
                                        mock_get_user_preferences,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        mock_get_user_preferences.return_value = {}
        ret = self.scapi._find_user_replay_profiles()
        self.assertEqual([], ret)
        mock_get_user_preferences.return_value = {'test': 'test',
                                                  'replayProfileList': []}
        ret = self.scapi._find_user_replay_profiles()
        self.assertEqual([], ret)
        mock_get_user_preferences.return_value = {
            'test': 'test', 'replayProfileList': [{'instanceId': 'a'},
                                                  {'instanceId': 'b'}]}
        ret = self.scapi._find_user_replay_profiles()
        self.assertEqual(['a', 'b'], ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json')
    def test__find_daily_replay_profile(self,
                                        mock_get_json,
                                        mock_post,
                                        mock_close_connection,
                                        mock_open_connection,
                                        mock_init):
        mock_post.return_value = self.RESPONSE_200
        mock_get_json.return_value = [{'instanceId': 'a'}]
        ret = self.scapi._find_daily_replay_profile()
        self.assertEqual('a', ret)
        mock_get_json.return_value = []
        ret = self.scapi._find_daily_replay_profile()
        self.assertIsNone(ret)
        mock_get_json.return_value = None
        ret = self.scapi._find_daily_replay_profile()
        self.assertIsNone(ret)
        mock_post.return_value = self.RESPONSE_400
        ret = self.scapi._find_daily_replay_profile()
        self.assertIsNone(ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json')
    def test__find_replay_profiles(self,
                                   mock_get_json,
                                   mock_post,
                                   mock_close_connection,
                                   mock_open_connection,
                                   mock_init):
        # Good run.
        rps = 'a,b'
        mock_post.return_value = self.RESPONSE_200
        mock_get_json.return_value = [{'name': 'a', 'instanceId': 'a'},
                                      {'name': 'b', 'instanceId': 'b'},
                                      {'name': 'c', 'instanceId': 'c'}]
        reta, retb = self.scapi._find_replay_profiles(rps)
        self.assertEqual(['a', 'b'], reta)
        self.assertEqual(['c'], retb)
        # Looking for profile that doesn't exist.
        rps = 'a,b,d'
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi._find_replay_profiles,
                          rps)
        # Looking for nothing.
        rps = ''
        reta, retb = self.scapi._find_replay_profiles(rps)
        self.assertEqual([], reta)
        self.assertEqual([], retb)
        # Still Looking for nothing.
        rps = None
        reta, retb = self.scapi._find_replay_profiles(rps)
        self.assertEqual([], reta)
        self.assertEqual([], retb)
        # Bad call.
        rps = 'a,b'
        mock_post.return_value = self.RESPONSE_400
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi._find_replay_profiles,
                          rps)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_replay_profiles')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_user_replay_profiles')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_find_daily_replay_profile')
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_update_volume_profiles')
    def test_update_replay_profiles(self,
                                    mock_update_volume_profiles,
                                    mock_find_daily_replay_profile,
                                    mock_find_user_replay_profiles,
                                    mock_find_replay_profiles,
                                    mock_close_connection,
                                    mock_open_connection,
                                    mock_init):
        scvol = {}
        mock_find_replay_profiles.return_value = (['a', 'b'], ['c'])
        mock_update_volume_profiles.side_effect = [
            True, True, True,
            False,
            True, True, False,
            True, True, True, True, True,
            True, True, True, True,
            False]
        ret = self.scapi.update_replay_profiles(scvol, 'a,b')
        # Two adds and one remove
        self.assertEqual(3, mock_update_volume_profiles.call_count)
        self.assertTrue(ret)
        # Now update fails.
        ret = self.scapi.update_replay_profiles(scvol, 'a,b')
        # 1 failed update plus 3 from before.
        self.assertEqual(4, mock_update_volume_profiles.call_count)
        self.assertFalse(ret)
        # Fail adding Ids..
        ret = self.scapi.update_replay_profiles(scvol, 'a,b')
        # 3 more 4 from before.
        self.assertEqual(7, mock_update_volume_profiles.call_count)
        self.assertFalse(ret)
        # User clearing profiles.
        mock_find_replay_profiles.return_value = ([], ['a', 'b', 'c'])
        mock_find_user_replay_profiles.return_value = ['d', 'u']
        ret = self.scapi.update_replay_profiles(scvol, '')
        # 3 removes and 2 adds plus 7 from before
        self.assertEqual(12, mock_update_volume_profiles.call_count)
        self.assertTrue(ret)
        # User clearing profiles and no defaults. (Probably not possible.)
        mock_find_user_replay_profiles.return_value = []
        mock_find_daily_replay_profile.return_value = 'd'
        ret = self.scapi.update_replay_profiles(scvol, '')
        # 3 removes and 1 add plus 12 from before.
        self.assertEqual(16, mock_update_volume_profiles.call_count)
        self.assertTrue(ret)
        # _find_replay_profiles blows up so we do too.
        mock_find_replay_profiles.side_effect = (
            exception.VolumeBackendAPIException('aaa'))
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.update_replay_profiles,
                          scvol,
                          'a,b')

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put')
    def test_manage_replay(self,
                           mock_put,
                           mock_close_connection,
                           mock_open_connection,
                           mock_init):
        screplay = {'description': 'notguid',
                    'instanceId': 1}
        payload = {'description': 'guid',
                   'expireTime': 0}
        mock_put.return_value = self.RESPONSE_200
        ret = self.scapi.manage_replay(screplay, 'guid')
        self.assertTrue(ret)
        mock_put.assert_called_once_with('StorageCenter/ScReplay/1', payload)
        mock_put.return_value = self.RESPONSE_400
        ret = self.scapi.manage_replay(screplay, 'guid')
        self.assertFalse(ret)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'put')
    def test_unmanage_replay(self,
                             mock_put,
                             mock_close_connection,
                             mock_open_connection,
                             mock_init):
        screplay = {'description': 'guid',
                    'instanceId': 1}
        payload = {'expireTime': 1440}
        mock_put.return_value = self.RESPONSE_200
        ret = self.scapi.unmanage_replay(screplay)
        self.assertTrue(ret)
        mock_put.assert_called_once_with('StorageCenter/ScReplay/1', payload)
        mock_put.return_value = self.RESPONSE_400
        ret = self.scapi.unmanage_replay(screplay)
        self.assertFalse(ret)


class DellSCSanAPIConnectionTestCase(test.TestCase):

    """DellSCSanAPIConnectionTestCase

    Class to test the Storage Center API connection using Mock.
    """

    # Create a Response object that indicates OK
    response_ok = models.Response()
    response_ok.status_code = 200
    response_ok.reason = u'ok'
    RESPONSE_200 = response_ok

    # Create a Response object with no content
    response_nc = models.Response()
    response_nc.status_code = 204
    response_nc.reason = u'duplicate'
    RESPONSE_204 = response_nc

    # Create a Response object is a pure error.
    response_bad = models.Response()
    response_bad.status_code = 400
    response_bad.reason = u'bad request'
    RESPONSE_400 = response_bad

    APIDICT = {u'instanceId': u'0',
               u'hostName': u'192.168.0.200',
               u'userId': 434226,
               u'connectionKey': u'',
               u'minApiVersion': u'0.1',
               u'webServicesPort': 3033,
               u'locale': u'en_US',
               u'objectType': u'ApiConnection',
               u'secureString': u'',
               u'applicationVersion': u'2.0.1',
               u'source': u'REST',
               u'commandLine': False,
               u'application': u'Cinder REST Driver',
               u'sessionKey': 1436460614863,
               u'provider': u'EnterpriseManager',
               u'instanceName': u'ApiConnection',
               u'connected': True,
               u'userName': u'Admin',
               u'useHttps': False,
               u'providerVersion': u'15.3.1.186',
               u'apiVersion': u'2.2',
               u'apiBuild': 199}

    def setUp(self):
        super(DellSCSanAPIConnectionTestCase, self).setUp()

        # Configuration is a mock.  A mock is pretty much a blank
        # slate.  I believe mock's done in setup are not happy time
        # mocks.  So we just do a few things like driver config here.
        self.configuration = mock.Mock()

        self.configuration.san_is_local = False
        self.configuration.san_ip = "192.168.0.1"
        self.configuration.san_login = "admin"
        self.configuration.san_password = "mmm"
        self.configuration.dell_sc_ssn = 12345
        self.configuration.dell_sc_server_folder = 'openstack'
        self.configuration.dell_sc_volume_folder = 'openstack'
        # Note that we set this to True even though we do not
        # test this functionality.  This is sent directly to
        # the requests calls as the verify parameter and as
        # that is a third party library deeply stubbed out is
        # not directly testable by this code.  Note that in the
        # case that this fails the driver fails to even come
        # up.
        self.configuration.dell_sc_verify_cert = True
        self.configuration.dell_sc_api_port = 3033
        self.configuration.iscsi_ip_address = '192.168.1.1'
        self.configuration.iscsi_port = 3260
        self._context = context.get_admin_context()
        self.apiversion = '2.0'

        # Set up the StorageCenterApi
        self.scapi = dell_storagecenter_api.StorageCenterApi(
            self.configuration.san_ip,
            self.configuration.dell_sc_api_port,
            self.configuration.san_login,
            self.configuration.san_password,
            self.configuration.dell_sc_verify_cert,
            self.apiversion)

        # Set up the scapi configuration vars
        self.scapi.ssn = self.configuration.dell_sc_ssn
        self.scapi.sfname = self.configuration.dell_sc_server_folder
        self.scapi.vfname = self.configuration.dell_sc_volume_folder

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=APIDICT)
    def test_open_connection(self,
                             mock_get_json,
                             mock_post):
        self.scapi.open_connection()
        self.assertTrue(mock_post.called)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_check_version_fail',
                       return_value=RESPONSE_400)
    def test_open_connection_failure(self,
                                     mock_check_version_fail,
                                     mock_post):

        self.assertRaises(exception.VolumeBackendAPIException,
                          self.scapi.open_connection)
        self.assertTrue(mock_check_version_fail.called)

    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_check_version_fail',
                       return_value=RESPONSE_200)
    @mock.patch.object(dell_storagecenter_api.StorageCenterApi,
                       '_get_json',
                       return_value=APIDICT)
    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_400)
    def test_open_connection_sc(self,
                                mock_post,
                                mock_get_json,
                                mock_check_version_fail):
        self.scapi.open_connection()
        self.assertTrue(mock_check_version_fail.called)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_204)
    def test_close_connection(self,
                              mock_post):
        self.scapi.close_connection()
        self.assertTrue(mock_post.called)

    @mock.patch.object(dell_storagecenter_api.HttpClient,
                       'post',
                       return_value=RESPONSE_200)
    def test_close_connection_failure(self,
                                      mock_post):
        self.scapi.close_connection()
        self.assertTrue(mock_post.called)