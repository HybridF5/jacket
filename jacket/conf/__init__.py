# This package got introduced during the Mitaka cycle in 2015 to
# have a central place where the config options of Nova can be maintained.
# For more background see the blueprint "centralize-config-options"

from jacket.compute import conf
from jacket.conf import api
from jacket.conf import fs_conf
from jacket.conf import netconf
from jacket.conf import quota


CONF = conf.CONF

api.register_opts(CONF)
fs_conf.register_opts(CONF)
quota.register_opts(CONF)
netconf.register_opts(CONF)