#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
from enum import IntEnum
import logging

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode, USBRequestType, USBRequestRecipient
from ultimarc.devices._structures import UltimarcStruct

_logger = logging.getLogger('ultimarc')


USTIK_DATA_SIZE = 96
USTIK_CONFIG_BASE = 0x51

# UltraStik pre 2015 defines
USTIK_PRE_INTERFACE = 0
USTIK_PRE_REQUEST_TYPE_1 = 0x43
USTIK_PRE_REQUEST_TYPE_2  = 0xC3
USTIK_PRE_REQUEST_1 = 0xE9
USTIK_PRE_REQUEST_2 = 0xEB
USTIK_PRE_REQUEST_3 = 0xEA
USTIK_PRE_MESG_LENGTH = 32

# UltraStik 2015 and newer defines
USTIK_INTERFACE = 2
USTIK_MESG_LENGTH = 4


DIRECTION_MAP = {
    '-': 0x0,
    'C': 0x1,
    'N': 0x2,
    'NE': 0x3,
    'E': 0x4,
    'SE': 0x5,
    'S': 0x6,
    'SW': 0x7,
    'W': 0x8,
    'NW': 0x9,
    '*': 0xA
}


class UltraStikPre2015Device(USBDeviceHandle):
    """
    Manage an UltraStik 360 Joystick (Pre-2015)
    """
    class_id = 'ultrastik'  # Used to match/filter devices.
    class_descr = _('UltraStik 360 Joystick')
    interface = USTIK_PRE_INTERFACE

    def set_controller_id(self, new_controller_id: int) -> bool:
        """
        Set the UltraStik controller ID
        :param new_controller_id: New control ID to set, must be an integer between 1 and 4.
        :return: True if successful, otherwise false.
        """
        # Calculate new device ID.
        new_id = USTIK_CONFIG_BASE + (new_controller_id - 1)
        # Setup data array.
        data = (ct.c_uint8 * USTIK_PRE_MESG_LENGTH)(0)
        data[0] = new_id

        resp_1 = self.write_raw(USBRequestCode.ULTRASTIK_E9, 0x1, USTIK_PRE_INTERFACE, ct.c_void_p(), 0x0,
                               request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                               recipient=USBRequestRecipient.RECIPIENT_OTHER)
        # We need to write 32 bytes here.
        resp_2 = self.write(USBRequestCode.ULTRASTIK_EB, 0x0, USTIK_PRE_INTERFACE, data, USTIK_PRE_MESG_LENGTH,
                            request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                            recipient=USBRequestRecipient.RECIPIENT_OTHER)
        resp_3 = self.read(USBRequestCode.ULTRASTIK_EA, 0x0, USTIK_PRE_INTERFACE, ct.c_void_p(), 0x0,
                          request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                          recipient=USBRequestRecipient.RECIPIENT_OTHER)
        resp_4 = self.write(USBRequestCode.ULTRASTIK_E9, 0x0, USTIK_PRE_INTERFACE, ct.c_void_p(), 0x0,
                           request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                           recipient=USBRequestRecipient.RECIPIENT_OTHER)

        return not False in [resp_1, resp_2, resp_3, resp_4]

    def set_config(self):
        ...


class UltraStikDevice(USBDeviceHandle):
    """
    Manage an UltraStik 360 Joystick (2015 or newer)
    """
    class_id = 'ultrastik'  # Used to match/filter devices.
    class_descr = _('UltraStik 360 Joystick')
    interface = USTIK_INTERFACE

    def set_controller_id(self, new_controller_id: int) -> bool:
        """
        Set the Ultrastik controller ID
        :param new_controller_id: New control ID to set, must be an integer between 1 and 4.
        :return: True if successful, otherwise false.
        """
        # Calculate new device ID.
        new_id = USTIK_CONFIG_BASE + (new_controller_id - 1)
        # Setup data array.
        data = (ct.c_uint8 * USTIK_MESG_LENGTH)(0)
        data[0] = new_id

        resp = self.write(USBRequestCode.SET_CONFIGURATION, 0x0, USTIK_INTERFACE, data, USTIK_MESG_LENGTH,
                          request_type=USBRequestType.REQUEST_TYPE_CLASS,
                          recipient=USBRequestRecipient.RECIPIENT_INTERFACE)

        return resp
