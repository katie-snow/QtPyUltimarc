#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode
from ultimarc.devices._structures import UltimarcStruct


_logger = logging.getLogger('ultimarc')


USBButtonReportID = ct.c_uint16(0x0)
USBButtonWIndex = ct.c_uint16(0x0)


class USBButtonColorStruct(ct.Structure):
    """ Defines RGB color values for USB button device """
    _fields_ = [
        ('target', ct.c_uint8),  # Must always be 0x01.
        ('red', ct.c_uint8),
        ('green', ct.c_uint8),
        ('blue', ct.c_uint8)
    ]


class USBButtonDevice(USBDeviceHandle):
    """
    Manage a USB Button device
    """
    class_id = 'usb-button'  # Used to match/filter devices.
    class_descr = _('USB Button')
    interface = 0  # Interface to write and read from.

    def set_color(self, red, green, blue):
        """
        Set USB button color.
        :param red: integer between 0 and 255
        :param green: integer between 0 and 255
        :param blue: integer between 0 and 255
        :return: True if successful otherwise False.
        """
        for color in [red, green, blue]:
            if not isinstance(color, int) or not 0 <= color <= 255:
                raise ValueError(_('Color argument value is invalid'))

        data = USBButtonColorStruct(0x01, red, green, blue)
        return self.write(USBRequestCode.SET_CONFIGURATION, 0x0, USBButtonWIndex, data, ct.sizeof(data))

    def get_color(self):
        """
        Return the current USB button RGB color values.
        :return: (Integer, Integer, Integer) or None
        """
        data = USBButtonColorStruct(0x01, 0x0, 0x0, 0x0)
        for x in range(20):
            ret = self.read(USBRequestCode.CLEAR_FEATURE, 0x0, USBButtonWIndex, data, ct.sizeof(data))
            if ret:
                return data.red, data.green, data.blue
            _logger.error(_('Failed to read color data from usb button.'))
        return None, None, None

    def set_config(self, config_file):
        """
        Write the configuration file to the device.
        :param config_file: Absolute path to configuration json file.
        :return: True if successful otherwise False.
        """
        # List of possible 'resourceType' values in the config file for a USB button.
        resource_types = ['usb-button-color']

        # Validate against the base schema.
        config = self.validate_config_base(config_file, resource_types)
        if not config:
            return False

        if config['deviceClass'] != 'usb-button':
            _logger.error(_('Configuration device class is not "usb-button".'))
            return False

        # Determine which config resource type we have.
        if config['resourceType'] == 'usb-button-color':
            if not self.validate_config(config, 'usb-button-color.schema'):
                return False
            c = config['colorRGB']
            data = USBButtonColorStruct(0x01, c['red'], c['green'], c['blue'])
            return self.write(USBRequestCode.SET_CONFIGURATION, USBButtonReportID, USBButtonWIndex, data, ct.sizeof(data))

        return False
