# Copyright (c) 2013 Intel, Inc.
# Copyright (c) 2013 OpenStack Foundation
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

from oslo_serialization import jsonutils

import jacket.compute.conf
from jacket.compute import exception
from jacket.i18n import _
from jacket.compute.pci import devspec

CONF = jacket.compute.conf.CONF


class Whitelist(object):

    """White list class to decide assignable pci devices.

    Not all devices on compute node can be assigned to guest, the
    cloud administrator decides the devices that can be assigned
    based on vendor_id or product_id etc. If no white list specified,
    no device will be assignable.
    """

    def _parse_white_list_from_config(self, whitelists):
        """Parse and validate the pci whitelist from the compute config."""
        specs = []
        for jsonspec in whitelists:
            try:
                dev_spec = jsonutils.loads(jsonspec)
            except ValueError:
                raise exception.PciConfigInvalidWhitelist(
                          reason=_("Invalid entry: '%s'") % jsonspec)
            if isinstance(dev_spec, dict):
                dev_spec = [dev_spec]
            elif not isinstance(dev_spec, list):
                raise exception.PciConfigInvalidWhitelist(
                          reason=_("Invalid entry: '%s'; "
                                   "Expecting list or dict") % jsonspec)

            for ds in dev_spec:
                if not isinstance(ds, dict):
                    raise exception.PciConfigInvalidWhitelist(
                              reason=_("Invalid entry: '%s'; "
                                       "Expecting dict") % ds)

                spec = devspec.PciDeviceSpec(ds)
                specs.append(spec)

        return specs

    def __init__(self, whitelist_spec=None):
        """White list constructor

        For example, followed json string specifies that devices whose
        vendor_id is '8086' and product_id is '1520' can be assigned
        to guest.
        '[{"product_id":"1520", "vendor_id":"8086"}]'

        :param whitelist_spec: A json string for a list of dictionaries,
                               each dictionary specifies the pci device
                               properties requirement.
        """
        super(Whitelist, self).__init__()
        if whitelist_spec:
            self.specs = self._parse_white_list_from_config(whitelist_spec)
        else:
            self.specs = []

    def device_assignable(self, dev):
        """Check if a device can be assigned to a guest.

        :param dev: A dictionary describing the device properties
        """
        for spec in self.specs:
            if spec.match(dev):
                return True
        return False

    def get_devspec(self, pci_dev):
        for spec in self.specs:
            if spec.match_pci_obj(pci_dev):
                return spec


def get_pci_device_devspec(pci_dev):
    dev_filter = Whitelist(CONF.pci_passthrough_whitelist)
    return dev_filter.get_devspec(pci_dev)