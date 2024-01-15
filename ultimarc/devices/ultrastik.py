#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging

from python_easy_json import JSONObject

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode, USBRequestType, USBRequestRecipient
from ultimarc.devices._structures import UltraStikStruct

_logger = logging.getLogger('ultimarc')

USTIK_RESOURCE_TYPES = ['ultrastik-controller-id', 'ultrastik-config']

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
        # Setup an array with zero for all byte values.
        data = (ct.c_ubyte * USTIK_PRE_MESG_LENGTH)(0)
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

    def set_config(self, config_file: str) -> bool:
        """ Set the joystick configuration """

        config = JSONObject(self.validate_config_base(config_file, USTIK_RESOURCE_TYPES))

        data = UltraStikStruct()
        data.keepAnalog = 0x11 if config.keepAnalog else 0x11
        data.mapSize = config.mapSize
        data.restrictor = 0x09 if config.restrictor else 0x10
        data.borders = (ct.c_uint8 * 8)(*config.borders)
        data.map = (ct.c_uint8 * 81)(*[DIRECTION_MAP[v] for v in config.map])
        data.flash = 0x00 if config.flash else 0xFF
        data.reserved = (ct.c_uint8 * 3)(*[0, 0, 0])

        resp_2 = resp_3 = resp_4 = False
        payload = (ct.c_uint8 * USTIK_PRE_MESG_LENGTH)(0)

        resp_1 = self.write_raw(USBRequestCode.ULTRASTIK_E9, 0x1, USTIK_PRE_INTERFACE, ct.c_void_p(), 0x0,
                                request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                                recipient=USBRequestRecipient.RECIPIENT_OTHER)
        # We need to write 32 bytes here.
        for x in range(3):
            ct.memmove(ct.addressof(payload), ct.byref(data, USTIK_PRE_MESG_LENGTH * x), USTIK_PRE_MESG_LENGTH)
            _logger.debug(f"  config data block {x+1}: {' '.join('%02X' % b for b in payload)}")

            resp_2 = self.write(USBRequestCode.ULTRASTIK_EB, 0x0, USTIK_PRE_INTERFACE,
                                payload, USTIK_PRE_MESG_LENGTH,
                                request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                                recipient=USBRequestRecipient.RECIPIENT_OTHER)
            resp_3 = self.read(USBRequestCode.ULTRASTIK_EA, 0x0, USTIK_PRE_INTERFACE, ct.c_void_p(), 0x0,
                                request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                                recipient=USBRequestRecipient.RECIPIENT_OTHER)
            if not resp_2 or not resp_3:
                break

        if resp_2 and resp_3:
            resp_4 = self.write(USBRequestCode.ULTRASTIK_E9, 0x0, USTIK_PRE_INTERFACE, ct.c_void_p(), 0x0,
                            request_type=USBRequestType.REQUEST_TYPE_VENDOR,
                            recipient=USBRequestRecipient.RECIPIENT_OTHER)

        return not False in [resp_1, resp_2, resp_3, resp_4]


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
        # Setup an array with zero for all byte values.
        data = (ct.c_ubyte * USTIK_MESG_LENGTH)(0)
        data[0] = new_id

        resp = self.write(USBRequestCode.SET_CONFIGURATION, 0x0, USTIK_INTERFACE, data, USTIK_MESG_LENGTH,
                          request_type=USBRequestType.REQUEST_TYPE_CLASS,
                          recipient=USBRequestRecipient.RECIPIENT_INTERFACE)

        return resp

    def set_config(self, config_file: str) -> bool:
        """ Set the joystick configuration """

        config = JSONObject(self.validate_config_base(config_file, USTIK_RESOURCE_TYPES))

        data = UltraStikStruct()
        data.keepAnalog = 0x11 if config.keepAnalog else 0x11
        data.mapSize = config.mapSize
        data.restrictor = 0x09 if config.restrictor else 0x10
        data.borders = (ct.c_uint8 * 8)(*config.borders)
        data.map = (ct.c_uint8 * 81)(*[DIRECTION_MAP[v] for v in config.map])
        data.flash = 0x00
        data.reserved = (ct.c_uint8 * 3)(*[0, 0, 0])

        payload = (ct.c_uint8 * USTIK_MESG_LENGTH)(0)
        ct.memmove(ct.addressof(payload), ct.byref(data, USTIK_MESG_LENGTH), USTIK_MESG_LENGTH)
        _logger.debug(f"  config data : {' '.join('%02X' % b for b in payload)}")

        resp = self.write_raw(USBRequestCode.SET_CONFIGURATION, 0x1, USTIK_INTERFACE, payload, USTIK_MESG_LENGTH,
                                request_type=USBRequestType.REQUEST_TYPE_CLASS,
                                recipient=USBRequestRecipient.RECIPIENT_INTERFACE)

        return resp
