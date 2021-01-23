#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging
from enum import IntEnum

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode
from ultimarc.devices._mappings import IPACSeriesMapping
from ultimarc.devices._structures import UltimarcStruct
from ultimarc.system_utils import JSONObject


_logger = logging.getLogger('ultimarc')


USBButtonReportID = 0x0200
USBButtonWIndex = 0x0
PACKETSIZE = 64


class ConfigApplication(IntEnum):
    permanent = 0x50
    temporary = 0x51


ButtonModeMapping = {
    'alternate': 0x00,
    'extended': 0x01,
    'both': 0x02
}


class RGBValueStruct(ct.Structure):
    _fields_ = [
        ('red', ct.c_uint8),
        ('green', ct.c_uint8),
        ('blue', ct.c_uint8)
    ]


class USBButtonColorStruct(UltimarcStruct):
    """ Defines RGB color values for USB button device """
    _fields_ = [
        ('reportId', ct.c_uint8),  # Must always be 0x01.
        ('red', ct.c_uint8),
        ('green', ct.c_uint8),
        ('blue', ct.c_uint8)
    ]


ROWARRAY = ct.c_uint8 * 6


class USBButtonConfigStruct(UltimarcStruct):
    """ Defines a configuration for a USB button device. """
    _fields_ = [
        # ('reportId', ct.c_uint8),  # Can be 0x00 or 0x01, not sure exactly which one is right.
        ('configApplication', ct.c_uint8),  # Can be 0x50 for permanent or 0x51 for temporary. See: ConfigApplication.
        ('opDetail', ct.c_uint8),  # Must always be 0xdd.
        ('mode', ct.c_uint8),  # See ButtonModeMapping.
        ('reserved', ct.c_uint8),  # Must be 0x00.
        ('releasedRGB', RGBValueStruct),
        ('pressedRGB', RGBValueStruct),
        ('row1', ROWARRAY),
        ('row2', ROWARRAY),
        ('row3', ROWARRAY),
        ('row4', ROWARRAY),
        ('row5', ROWARRAY),
        ('row6', ROWARRAY),
        ('row7', ROWARRAY),
        ('row8', ROWARRAY)
    ]


class USBButtonDevice(USBDeviceHandle):
    """
    Manage a USB Button device
    """
    class_id = 'usb-button'  # Used to match/filter devices.
    class_descr = _('USB Button')
    interface = 0  # USB interface to write and read from.

    def set_color(self, red, green, blue):
        """
        Set USB button color, overrides the current device configuration released color.
        :param red: integer between 0 and 255
        :param green: integer between 0 and 255
        :param blue: integer between 0 and 255
        :return: True if successful otherwise False.
        """
        for color in [red, green, blue]:
            if not isinstance(color, int) or not 0 <= color <= 255:
                raise ValueError(_('Color argument value is invalid'))

        data = USBButtonColorStruct(0x01, red, green, blue)
        return self.write(USBRequestCode.SET_CONFIGURATION, USBButtonReportID, USBButtonWIndex, data, ct.sizeof(data))

    def get_color(self):
        """
        Return override USB button RGB color.  Will return (0, 0, 0) if the device has not yet been written
        to using the set_color() method.
        :return: (Integer, Integer, Integer) or None
        """
        data = USBButtonColorStruct(0x01, 0x0, 0x0, 0x0)
        ret = self.read(USBRequestCode.CLEAR_FEATURE, USBButtonReportID, USBButtonWIndex, data, ct.sizeof(data))
        if ret:
            return data.red, data.green, data.blue
        _logger.error(_('Failed to read color data from usb button.'))
        return None, None, None

    def set_config(self, config_file, application=ConfigApplication.permanent):
        """
        Write the configuration file to the device.
        :param config_file: Absolute path to configuration json file.
        :param application: Permanent or temporary application of configuration to device.
        :return: True if successful otherwise False.
        """
        # List of possible 'resourceType' values in the config file for a USB button.
        resource_types = ['usb-button-color', 'usb-button-config']

        # Validate against the base schema.
        config = JSONObject(self.validate_config_base(config_file, resource_types))
        if not config:
            return False

        if config.deviceClass != 'usb-button':
            _logger.error(_('Configuration device class is not "usb-button".'))
            return False

        # Determine which config resource type we have.
        if config.resourceType == 'usb-button-color':
            if not self.validate_config(config.to_dict(), 'usb-button-color.schema'):
                return False
            _logger.debug(_('Device JSON configuration passed schema validation.'))
            data = USBButtonColorStruct(0x01, config.colorRGB.red, config.colorRGB.green, config.colorRGB.blue)
            return self.write(USBRequestCode.SET_CONFIGURATION, USBButtonReportID, USBButtonWIndex, data,
                              ct.sizeof(data))

        # Process usb-button-config data
        if not self.validate_config(config.to_dict(), 'usb-button-config.schema'):
            return False
        _logger.debug(_('Device JSON configuration passed schema validation.'))

        action = ButtonModeMapping[config.action]

        released_rgb = RGBValueStruct(config.releasedColor.red, config.releasedColor.green, config.releasedColor.blue)
        pressed_rgb = RGBValueStruct(config.pressedColor.red, config.pressedColor.green, config.pressedColor.blue)
        debug_data = list()

        def row_to_struct(row):
            """ Convert array of chars to array of ct.c_uint8 values. """
            data = ROWARRAY(0)
            debug_row = list()
            for x in range(6):
                char = row[x].upper()
                if char in IPACSeriesMapping:
                    data[x] = IPACSeriesMapping[char]
                debug_row.append(f'{hex(data[x])}({char})')
            debug_data.append(debug_row)
            return data

        row1 = row_to_struct(config.keys[0].row1)
        row2 = row_to_struct(config.keys[0].row2)
        row3 = row_to_struct(config.keys[0].row3)
        row4 = row_to_struct(config.keys[0].row4)
        row5 = row_to_struct(config.keys[1].row5)
        row6 = row_to_struct(config.keys[1].row6)
        row7 = row_to_struct(config.keys[1].row7)
        row8 = row_to_struct(config.keys[1].row8)

        # TODO: Why do we have to write twice in a row for the config to be applied to the device?
        data = USBButtonConfigStruct(application, 0xdd, action, 0x00,
                    pressed_rgb, released_rgb,
                    row1, row2, row3, row4, row5, row6, row7, row8)

        _logger.debug(_(' application') + f': {application.name}')
        _logger.debug(_(' action') + f': {config.action}')
        _logger.debug(_(' released color') + f': R({released_rgb.red}), G({released_rgb.green}), B({released_rgb.blue})')
        _logger.debug(_(' pressed color') + f': R({pressed_rgb.red}), G({pressed_rgb.green}), B({pressed_rgb.blue})')
        for row in debug_data:
            _logger.debug(_(' row') + f': {", ".join(row)}')

        return self.write_alt(USBRequestCode.SET_CONFIGURATION, 0x00, USBButtonWIndex, data,
                          ct.sizeof(data))
