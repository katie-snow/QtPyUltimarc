#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import json
import logging
from enum import IntEnum

from python_easy_json import JSONObject
from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode
from ultimarc.devices._mappings import IPACSeriesMapping, get_ipac_series_mapping_key
from ultimarc.devices._structures import UltimarcStruct

_logger = logging.getLogger('ultimarc')

USBButtonReportID = 0x0200
USBButtonWIndex = 0x0
PACKETSIZE = 64
ROWARRAY = ct.c_uint8 * 6


class ConfigApplication(IntEnum):
    permanent = 0x50
    temporary = 0x51


ButtonModeMapping = {
    'alternate': 0x00,  # Send primary sequence then secondary on alternate presses.
    'extended': 0x01,  # Send both sequences on every press.
    'both': 0x02  # Send primary sequence on short press, secondary on long press.
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
        ('rgb', RGBValueStruct)
    ]


class USBButtonConfigStruct(UltimarcStruct):
    """ Defines a configuration for a USB button device. """
    _fields_ = [
        # ('reportId', ct.c_uint8),  # Can be 0x00 or 0x01, not sure exactly which one is right.
        ('configApplication', ct.c_uint8),  # Can be 0x50 for permanent or 0x51 for temporary. See: ConfigApplication.
        ('opDetail', ct.c_uint8),  # Must always be 0xdd.
        ('action', ct.c_uint8),  # See ButtonModeMapping.
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
        ('row8', ROWARRAY),
        ('padding', ROWARRAY)
    ]

class USBButtonRequestStruct(UltimarcStruct):
    """ Defines a request message for the USB button device. """
    _fields_ = [
        ('configApplication', ct.c_uint8),  # Must be 0x59 for request
        ('opDetail', ct.c_uint8),  # Must always be 0xdd.
        ('action', ct.c_uint8),  # Must be 0x00
        ('reserved', ct.c_uint8),  # Must be 0x00.
    ]


class USBButtonDevice(USBDeviceHandle):
    """
    Manage a USB Button device
    """
    class_id = 'usb-button'  # Used to match/filter devices.
    class_descr = _('USB Button')
    interface = 0  # USB interface to write and read from.

    def get_state(self):
        """
        Return the USB button click state.
        :return: 1 if clicked otherwise 0, None if error.
        """
        # TODO: Can't seem to make this work to return the button click state.  See USBButtonGetState() in PacDrive.cpp.
        data = USBButtonColorStruct(0x02, RGBValueStruct(0x0, 0x0, 0x0))
        ret = self.read(USBRequestCode.CLEAR_FEATURE, USBButtonReportID, USBButtonWIndex, data, ct.sizeof(data))
        if ret:
            return data.red
        _logger.error(_('Failed to read usb button state.'))
        return None

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

        data = USBButtonColorStruct(0x01, RGBValueStruct(red, green, blue))
        return self.write(USBRequestCode.SET_CONFIGURATION, USBButtonReportID, USBButtonWIndex, data, ct.sizeof(data))

    def get_color(self):
        """
        Return override USB button RGB color.  Will return (0, 0, 0) if the device has not yet been written
        to using the set_color() method.
        :return: (Integer, Integer, Integer) or None
        """
        data = USBButtonColorStruct(0x01, RGBValueStruct(0x0, 0x0, 0x0))
        ret = self.read(USBRequestCode.CLEAR_FEATURE, USBButtonReportID, USBButtonWIndex, data, ct.sizeof(data))
        if ret:
            return data.rgb.red, data.rgb.green, data.rgb.blue
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
            data = USBButtonColorStruct(0x01,
                                        RGBValueStruct(config.colorRGB.red, config.colorRGB.green,
                                                       config.colorRGB.blue))
            return self.write(USBRequestCode.SET_CONFIGURATION, USBButtonReportID, USBButtonWIndex, data,
                              ct.sizeof(data))

        # Process usb-button-config data
        if not self.validate_config(config.to_dict(), 'usb-button-config.schema'):
            return False
        _logger.debug(_('Device JSON configuration passed schema validation.'))

        data = self.create_message(config, application)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, 0x00, USBButtonWIndex, data,
                              ct.sizeof(data))

    def create_message(self, config: JSONObject, application=ConfigApplication.permanent):
        """
        Create message to send to the device.
        :param config: JSON object with configuration.
        :param application: Permanent or temporary application of configuration to device.
        :return: data structure to be sent.

        """
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

        row_keys = list()
        # Make sure we always put the primary set before the secondary set.
        for key in sorted(config.keys, key=lambda k: k.sequence):
            row_keys.append(row_to_struct(key.row1))
            row_keys.append(row_to_struct(key.row2))
            row_keys.append(row_to_struct(key.row3))
            row_keys.append(row_to_struct(key.row4))
        row_keys.append(ROWARRAY(0))  # Add padding data, this is probably used by the bluetooth usb button.

        data = USBButtonConfigStruct(application, 0xdd, action, 0x00, released_rgb, pressed_rgb, *row_keys)

        _logger.debug(_(' application') + f': {application.name}')
        _logger.debug(_(' action') + f': {config.action}')
        _logger.debug(
            _(' released color') + f': R({released_rgb.red}), G({released_rgb.green}), B({released_rgb.blue})')
        _logger.debug(_(' pressed color') + f': R({pressed_rgb.red}), G({pressed_rgb.green}), B({pressed_rgb.blue})')
        for row in debug_data:
            _logger.debug(_(' row') + f': {", ".join(row)}')

        return data

    def set_config_ui(self, config: JSONObject):
        """ Write the configuration from UI to the device """
        data = self.create_message(config)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, 0x00, USBButtonWIndex, data,
                              ct.sizeof(data))

    def get_device_config (self, indent=None, file=None):
        """ Return a json string of the device configuration """
        config = self.read_device()
        json_obj = self.create_json(config)
        if file:
            if self.write_to_file(json_obj, file, indent):
                return _('Wrote USB-Button configuration to ' + file)
            else:
                return _('Failed to write USB-Button configuration to file.')
        else:
            return json.dumps(json_obj, indent=indent) if config else None

    def create_json (self, data):
        """ Create a string for the USB-Button configuration"""
        config = {'schemaVersion': 2.0, 'resourceType': 'usb-button-config', 'deviceClass': 'usb-button'}

        # action
        action = hex(data.action)
        for key, value in ButtonModeMapping.items():
            if hex(value) == action:
                config['action'] = key
                break

        # releasedColor
        color = {'red': data.releasedRGB.red,
                 'green': data.releasedRGB.green,
                 'blue': data.releasedRGB.blue}
        config['releasedColor'] = color

        # pressedColor
        color = {'red': data.pressedRGB.red,
                 'green': data.pressedRGB.green,
                 'blue': data.pressedRGB.blue}
        config['pressedColor'] = color

        # Keys Primary rows 1-4
        config['keys'] = []
        keys = {'sequence': 'primary', 'row1':[], 'row2': [], 'row3': [], 'row4': []}
        for x in range(6):
            key = get_ipac_series_mapping_key(data.row1[x])
            keys['row1'].append(key)

            key = get_ipac_series_mapping_key(data.row2[x])
            keys['row2'].append(key)

            key = get_ipac_series_mapping_key(data.row3[x])
            keys['row3'].append(key)

            key = get_ipac_series_mapping_key(data.row4[x])
            keys['row4'].append(key)

        config['keys'].append(keys)

        # Keys Secondary rows 5 - 8
        keys = {'sequence': 'secondary', 'row1': [], 'row2': [], 'row3': [], 'row4': []}
        for x in range(6):
            key = get_ipac_series_mapping_key(data.row5[x])
            keys['row1'].append(key)

            key = get_ipac_series_mapping_key(data.row6[x])
            keys['row2'].append(key)

            key = get_ipac_series_mapping_key(data.row7[x])
            keys['row3'].append(key)

            key = get_ipac_series_mapping_key(data.row8[x])
            keys['row4'].append(key)

        config['keys'].append(keys)

        return config if self.validate_config(config, 'usb-button-config.schema') else None

    def read_device(self):
        """ Return the configuration of the connected USBButton """
        request = USBButtonRequestStruct(0x59, 0xdd, 0x00, 0x00)
        ret = self.write_raw(USBRequestCode.SET_CONFIGURATION, 0x200, 0x00,
                         request, ct.sizeof(request))
        return self.read_interrupt(0x81, USBButtonConfigStruct(), False) if ret else None

    @classmethod
    def write_to_file(cls, data: dict, file_path, indent=None):
        try:
            with open(file_path, 'w') as h:
                json.dump(data, h, indent=indent)
                return True
        except FileNotFoundError as err:
            _logger.debug(err)
            return False