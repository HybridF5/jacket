# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright (c) 2010 Citrix Systems, Inc.
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

"""
Handling of VM disk images.
"""

import os

from oslo_concurrency import processutils
from oslo_log import log as logging
from oslo_utils import fileutils
from oslo_utils import imageutils
from oslo_utils import units

import jacket.compute.conf
from jacket.compute import exception
from jacket.i18n import _, _LE
from jacket.compute import image
from jacket.compute import utils

LOG = logging.getLogger(__name__)

CONF = jacket.compute.conf.CONF
IMAGE_API = image.API()

QEMU_IMG_LIMITS = processutils.ProcessLimits(
    #cpu_time=2,
    address_space=1 * units.Gi)


def qemu_img_info(path, format=None):
    """Return an object containing the parsed output from qemu-img info."""
    # TODO(mikal): this code should not be referring to a libvirt specific
    # flag.
    # NOTE(sirp): The config option import must go here to avoid an import
    # cycle
    CONF.import_opt('images_type', 'jacket.compute.virt.libvirt.imagebackend',
                    group='libvirt')
    if not os.path.exists(path) and CONF.libvirt.images_type != 'rbd':
        raise exception.DiskNotFound(location=path)

    try:
        cmd = ('env', 'LC_ALL=C', 'LANG=C', 'qemu-img', 'info', path)
        if format is not None:
            cmd = cmd + ('-f', format)
        out, err = utils.execute(*cmd, prlimit=QEMU_IMG_LIMITS)
    except processutils.ProcessExecutionError as exp:
        msg = (_("qemu-img failed to execute on %(path)s : %(exp)s") %
                {'path': path, 'exp': exp})
        raise exception.InvalidDiskInfo(reason=msg)

    if not out:
        msg = (_("Failed to run qemu-img info on %(path)s : %(error)s") %
               {'path': path, 'error': err})
        raise exception.InvalidDiskInfo(reason=msg)

    return imageutils.QemuImgInfo(out)


def convert_image(source, dest, in_format, out_format, run_as_root=False):
    """Convert image to other format."""
    if in_format is None:
        raise RuntimeError("convert_image without input format is a security"
                           "risk")
    _convert_image(source, dest, in_format, out_format, run_as_root)


def convert_image_unsafe(source, dest, out_format, run_as_root=False):
    """Convert image to other format, doing unsafe automatic input format
    detection. Do not call this function.
    """

    # NOTE: there is only 1 caller of this function:
    # imagebackend.Lvm.create_image. It is not easy to fix that without a
    # larger refactor, so for the moment it has been manually audited and
    # allowed to continue. Remove this function when Lvm.create_image has
    # been fixed.
    _convert_image(source, dest, None, out_format, run_as_root)


def _convert_image(source, dest, in_format, out_format, run_as_root):
    cmd = ('qemu-img', 'convert', '-O', out_format, source, dest)
    if in_format is not None:
        cmd = cmd + ('-f', in_format)
    try:
        utils.execute(*cmd, run_as_root=run_as_root)
    except processutils.ProcessExecutionError as exp:
        msg = (_("Unable to convert image to %(format)s: %(exp)s") %
               {'format': out_format, 'exp': exp})
        raise exception.ImageUnacceptable(image_id=source, reason=msg)


def fetch(context, image_href, path, _user_id, _project_id, max_size=0):
    with fileutils.remove_path_on_error(path):
        IMAGE_API.download(context, image_href, dest_path=path)


def get_info(context, image_href):
    return IMAGE_API.get(context, image_href)


def fetch_to_raw(context, image_href, path, user_id, project_id, max_size=0):
    path_tmp = "%s.part" % path
    fetch(context, image_href, path_tmp, user_id, project_id,
          max_size=max_size)

    with fileutils.remove_path_on_error(path_tmp):
        data = qemu_img_info(path_tmp)

        fmt = data.file_format
        if fmt is None:
            raise exception.ImageUnacceptable(
                reason=_("'qemu-img info' parsing failed."),
                image_id=image_href)

        backing_file = data.backing_file
        if backing_file is not None:
            raise exception.ImageUnacceptable(image_id=image_href,
                reason=(_("fmt=%(fmt)s backed by: %(backing_file)s") %
                        {'fmt': fmt, 'backing_file': backing_file}))

        # We can't generally shrink incoming images, so disallow
        # images > size of the flavor we're booting.  Checking here avoids
        # an immediate DoS where we convert large qcow images to raw
        # (which may compress well but not be sparse).
        # TODO(p-draigbrady): loop through all flavor sizes, so that
        # we might continue here and not discard the download.
        # If we did that we'd have to do the higher level size checks
        # irrespective of whether the base image was prepared or not.
        disk_size = data.virtual_size
        if max_size and max_size < disk_size:
            LOG.error(_LE('%(base)s virtual size %(disk_size)s '
                          'larger than flavor root disk size %(size)s'),
                      {'base': path,
                       'disk_size': disk_size,
                       'size': max_size})
            raise exception.FlavorDiskSmallerThanImage(
                flavor_size=max_size, image_size=disk_size)

        if fmt != "raw" and CONF.force_raw_images:
            staged = "%s.converted" % path
            LOG.debug("%s was %s, converting to raw", image_href, fmt)
            with fileutils.remove_path_on_error(staged):
                try:
                    convert_image(path_tmp, staged, fmt, 'raw')
                except exception.ImageUnacceptable as exp:
                    # re-raise to include image_href
                    raise exception.ImageUnacceptable(image_id=image_href,
                        reason=_("Unable to convert image to raw: %(exp)s")
                        % {'exp': exp})

                os.unlink(path_tmp)

                data = qemu_img_info(staged)
                if data.file_format != "raw":
                    raise exception.ImageUnacceptable(image_id=image_href,
                        reason=_("Converted to raw, but format is now %s") %
                        data.file_format)

                os.rename(staged, path)
        else:
            os.rename(path_tmp, path)
