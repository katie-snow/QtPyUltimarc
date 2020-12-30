#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle


class AimTrakDevice(USBDeviceHandle):
    """
    Manage an AimTrak light gun device
    """
    class_id = 'aimtrak'  # Used to match/filter devices.
    class_descr = _('Aimtrak Light Gun')
    pass
