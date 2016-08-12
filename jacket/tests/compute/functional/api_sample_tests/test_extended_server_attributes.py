# Copyright 2012 Nebula, Inc.
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

from oslo_config import cfg

from jacket.tests.compute.functional.api_sample_tests import test_servers

CONF = cfg.CONF
CONF.import_opt('osapi_compute_extension',
                'compute.api.openstack.compute.legacy_v2.extensions')


class ExtendedServerAttributesJsonTest(test_servers.ServersSampleBase):
    extension_name = "os-extended-server-attributes"

    def _get_flags(self):
        f = super(ExtendedServerAttributesJsonTest, self)._get_flags()
        f['osapi_compute_extension'] = CONF.osapi_compute_extension[:]
        f['osapi_compute_extension'].append(
            'compute.api.openstack.compute.contrib.keypairs.Keypairs')
        f['osapi_compute_extension'].append(
            'compute.api.openstack.compute.contrib.extended_ips.Extended_ips')
        f['osapi_compute_extension'].append(
            'compute.api.openstack.compute.contrib.extended_ips_mac.'
            'Extended_ips_mac')
        f['osapi_compute_extension'].append(
            'compute.api.openstack.compute.contrib.extended_server_attributes.'
            'Extended_server_attributes')
        return f

    def test_show(self):
        uuid = self._post_server()

        response = self._do_get('servers/%s' % uuid)
        subs = {}
        subs['hostid'] = '[a-f0-9]+'
        subs['id'] = uuid
        subs['instance_name'] = 'instance-\d{8}'
        subs['hypervisor_hostname'] = r'[\w\.\-]+'
        subs['access_ip_v4'] = '1.2.3.4'
        subs['access_ip_v6'] = '80fe::'
        self._verify_response('server-get-resp', subs, response, 200)

    def test_detail(self):
        uuid = self._post_server()

        response = self._do_get('servers/detail')
        subs = {}
        subs['hostid'] = '[a-f0-9]+'
        subs['id'] = uuid
        subs['instance_name'] = 'instance-\d{8}'
        subs['hypervisor_hostname'] = r'[\w\.\-]+'
        subs['access_ip_v4'] = '1.2.3.4'
        subs['access_ip_v6'] = '80fe::'
        self._verify_response('servers-detail-resp', subs, response, 200)


class ExtendedServerAttributesJsonTestV216(ExtendedServerAttributesJsonTest):
    microversion = '2.16'
    scenarios = [('v2_16', {'api_major_version': 'v2.1'})]

    def test_show(self):
        uuid = self._post_server()

        response = self._do_get('servers/%s' % uuid)
        subs = {}
        subs['hostid'] = '[a-f0-9]+'
        subs['id'] = uuid
        subs['instance_name'] = 'instance-\d{8}'
        subs['hypervisor_hostname'] = r'[\w\.\-]+'
        subs['access_ip_v4'] = '1.2.3.4'
        subs['access_ip_v6'] = '80fe::'
        self._verify_response('server-get-resp', subs, response, 200)

    def test_detail(self):
        uuid = self._post_server()

        response = self._do_get('servers/detail')
        subs = {}
        subs['hostid'] = '[a-f0-9]+'
        subs['id'] = uuid
        subs['instance_name'] = 'instance-\d{8}'
        subs['hypervisor_hostname'] = r'[\w\.\-]+'
        subs['access_ip_v4'] = '1.2.3.4'
        subs['access_ip_v6'] = '80fe::'
        self._verify_response('servers-detail-resp', subs, response, 200)
