# Copyright (c) 2010 OpenStack Foundation
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

"""Handles ConsoleProxy API requests."""

from oslo_config import cfg

from jacket.compute.cloud import rpcapi as compute_rpcapi
from jacket.compute.console import rpcapi as console_rpcapi
from jacket.db import base
from jacket.objects import compute as objects

CONF = cfg.CONF
CONF.import_opt('console_topic', 'jacket.compute.console.rpcapi')


class API(base.Base):
    """API for spinning up or down console proxy connections."""

    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)

    def get_consoles(self, context, instance_uuid):
        return self.db.console_get_all_by_instance(context, instance_uuid,
                                                   columns_to_join=['pool'])

    def get_console(self, context, instance_uuid, console_uuid):
        return self.db.console_get(context, console_uuid, instance_uuid)

    def delete_console(self, context, instance_uuid, console_uuid):
        console = self.db.console_get(context, console_uuid, instance_uuid)
        rpcapi = console_rpcapi.ConsoleAPI(topic=CONF.console_topic,
                                           server=console['pool']['host'])
        rpcapi.remove_console(context, console['id'])

    def create_console(self, context, instance_uuid):
        # NOTE(mdragon): If we wanted to return this the console info
        #                here, as we would need to do a call.
        #                They can just do an index later to fetch
        #                console info. I am not sure which is better
        #                here.
        instance = objects.Instance.get_by_uuid(context, instance_uuid)
        topic = self._get_console_topic(context, instance.host)
        server = None
        if '.' in topic:
            topic, server = topic.split('.', 1)
        rpcapi = console_rpcapi.ConsoleAPI(topic=topic, server=server)
        rpcapi.add_console(context, instance.id)

    def _get_console_topic(self, context, instance_host):
        rpcapi = compute_rpcapi.ComputeAPI()
        return rpcapi.get_console_topic(context, instance_host)
