#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import atexit
import logging
import sys

import libusb as usb

from ._base import _USB_PRODUCT_CLASSES, USB_PRODUCT_DESCRIPTIONS, USBDevices, DeviceClassID
from ._device import usb_error

from ultimarc import translate_gettext as _
from ultimarc.exceptions import USBDeviceClaimInterfaceError, USBDeviceNotFoundError, \
    USBDeviceInterfaceNotClaimedError

_logger = logging.getLogger('default')

# Initialize libusb library.
_ret = usb.init(None)
if _ret < 0:
    _str = f'{_("LibUSB.init() failed with error")} {usb.error_name(_ret).decode("utf-8")} ({_ret}).'
    raise IOError(_str)
# Enable additional logging from LibUSB.
usb.set_option(None, usb.LIBUSB_OPTION_LOG_LEVEL, 1 if '--debug' in sys.argv else 0)


def _exit():
    """ Clean up libusb on exit """
    usb.exit(None)
    _logger.debug(_('LibUSB.exit() function called successfully.'))


# Register the _exit() function to be called when program quits.
atexit.register(_exit)

__all__ = [
    _USB_PRODUCT_CLASSES,
    USB_PRODUCT_DESCRIPTIONS,
    USBDevices,
    usb_error,
    USBDeviceClaimInterfaceError,
    USBDeviceInterfaceNotClaimedError,
    USBDeviceNotFoundError,
    DeviceClassID
]
