#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import json
import logging

from python_easy_json import JSONObject
from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode
from ultimarc.devices._mappings import get_ipac_series_macro_mapping_index, get_ipac_series_mapping_key, \
    get_ipac_series_debounce_key, IPACSeriesMapping, IPACSeriesDebounce
from ultimarc.devices._structures import PacHeaderStruct, PacStruct, PacConfigUnion

_logger = logging.getLogger('ultimarc')

ULTIMATE_IO_RESOURCE_TYPES = ['ultimateIO_pin', 'ultimateIO_led']

# Pin mapping for ultimateIO device
# code_index: Normal action
# alternate_code_index: Alternate action
# alternate_index: Which pin is the shift code
# pin name: (action_index, alternate_action_index, shift_key)
PinMapping = {
    '1up': (4, 54, 104),
    '1down': (6, 56, 106),
    '1right': (0, 50, 100),
    '1left': (2, 52, 102),
    '1a': (12, 62, 112),
    '1b': (14, 64, 114),
    '2up': (27, 77, 127),
    '2down': (25, 75, 125),
    '2right': (31, 81, 131),
    '2left': (29, 79, 129),
    '2a': (40, 90, 140),
    '2b': (42, 92, 142),
    '3up': (16, 66, 116),
    '3down': (18, 68, 118),
    '3right': (22, 72, 122),
    '3left': (20, 70, 120),
    '4up': (30, 80, 130),
    '4down': (28, 78, 128),
    '4right': (9, 59, 109),
    '4left': (8, 58, 108),
    '1sw1': (7, 57, 107),
    '1sw2': (5, 55, 105),
    '1sw3': (3, 53, 153),
    '1sw4': (1, 51, 101),
    '1sw5': (23, 73, 123),
    '1sw6': (21, 71, 121),
    '1sw7': (19, 69, 119),
    '1sw8': (17, 67, 117),
    '2sw1': (47, 97, 147),
    '2sw2': (45, 95, 145),
    '2sw3': (43, 93, 143),
    '2sw4': (41, 91, 141),
    '2sw5': (11, 61, 111),
    '2sw6': (49, 99, 149),
    '2sw7': (48, 98, 148),
    '2sw8': (10, 60, 110),
    '3sw1': (36, 86, 136),
    '3sw2': (38, 88, 138),
    '3sw3': (32, 82, 132),
    '3sw4': (34, 84, 134),
    '4sw1': (26, 76, 126),
    '4sw2': (24, 74, 124),
    '4sw3': (46, 96, 146),
    '4sw4': (44, 94, 144),
    '1start': (39, 89, 139),
    '1coin': (35, 85, 135),
    '2start': (37, 87, 137),
    '2coin': (33, 83, 133)
}


class UltimateIODevice(USBDeviceHandle):
    """ Manage an ultimateIO device """
    class_id = 'ultimateIO'
    class_descr = _('ULTIMATE IO')
    interface = 2
    ULTIMATEIO_INDEX = ct.c_uint16(0x02)

    # Each macro starts with control character e0 - fe.  Total of 30 macros possible
    # overall total macro characters is 56
    MACRO_MAX_COUNT = 30

    # These two values need to add up to 252
    MACRO_MAX_SIZE = 88
    MACRO_START_INDEX = 164

    def get_device_config(self, indent=None, file=None):
        """ Return a json string of the device configuration """
        config = self.read_device()
        json_obj = self.to_json_str(config)
        if file:
            if self.write_to_file(json_obj, file, indent):
                return _('Wrote ultimateIO configuration to ' + file)
            else:
                return _('Failed to write ultimateIO configuration to file.')
        else:
            return json.dumps(json_obj, indent=indent) if config else None

    def read_device(self):
        """ Return the configuration of the connected ultimateIO """
        request = PacHeaderStruct(0x59, 0xdd, 0x0f, 0)
        ret = self.write(USBRequestCode.SET_CONFIGURATION, int(0x03), self.ULTIMATEIO_INDEX,
                         request, ct.sizeof(request))
        return self.read_interrupt(0x84, PacStruct()) if ret else None

    def to_json_str(self, ultimate_struct):
        """ Converts a PacStruct to a json object """
        json_obj = {'schemaVersion': 2.0, 'resourceType': 'ultimateIO-pin', 'deviceClass': self.class_id}

        # header configuration
        header = PacConfigUnion()
        header.asByte = ultimate_struct.header.byte_4
        json_obj['debounce'] = get_ipac_series_debounce_key(header.config.debounce)

        # X Threshold
        json_obj['xThreshold'] = int(ultimate_struct.bytes[156], 16)

        # Y Threshold
        json_obj['yThreshold'] = int(ultimate_struct.bytes[163], 16)

        # macros
        macros = self._create_macro_array_(ultimate_struct)
        if len(macros):
            json_obj['macros'] = macros

        # pins
        pins = []
        for key in PinMapping:
            action_index, alternate_action_index, shift_index = PinMapping[key]
            pin = {}
            if ultimate_struct.bytes[action_index]:
                pin['name'] = key
                pin['action'] = get_ipac_series_mapping_key(ultimate_struct.bytes[action_index])
                if pin['action'] is None:
                    mi = get_ipac_series_macro_mapping_index(ultimate_struct.bytes[action_index])
                    if mi is not None:
                        pin['action'] = macros[mi]['name']
                    else:
                        _logger.debug(_(f'{key} action ({hex(ultimate_struct.bytes[action_index])})is not a valid value'))
                if ultimate_struct.bytes[alternate_action_index]:
                    alt_action = get_ipac_series_mapping_key(ultimate_struct.bytes[alternate_action_index])
                    if alt_action is None:
                        mi = get_ipac_series_macro_mapping_index(ultimate_struct.bytes[alternate_action_index])
                        if mi is not None:
                            pin['alternate_action'] = macros[mi]['name']
                    else:
                        pin['alternate_action'] = alt_action
                if ultimate_struct.bytes[shift_index] == 0x41:
                    pin['shift'] = True
                pins.append(pin)
        json_obj['pins'] = pins

        return json_obj if self.validate_config(json_obj, 'ultimateio-pin.schema') else None

    @classmethod
    def _create_macro_array_(cls, pac_struct):
        # macros
        macros = []
        macro_start = 0xe0
        macro_index = 1

        y = 0
        for x in range(cls.MACRO_START_INDEX, len(pac_struct.bytes)):
            if x >= y:
                macro = {}
                if pac_struct.bytes[x]:
                    if pac_struct.bytes[x] == macro_start:
                        macro['name'] = f'#{macro_index}'
                        macro_start += 1
                        macro_index += 1

                        action = []
                        for y in range(x + 1, len(pac_struct.bytes)):
                            # check that the value isn't zero and not the start of the next macro
                            if pac_struct.bytes[y] and pac_struct.bytes[y] != macro_start:
                                action.append(get_ipac_series_mapping_key(pac_struct.bytes[y]))
                            else:
                                macro['action'] = action
                                macros.append(macro)
                                break
                else:
                    # No more macros defined, end the loop
                    break
        return macros

    @classmethod
    def write_to_file(cls, data: dict, file_path, indent=None):
        try:
            with open(file_path, 'w') as h:
                json.dump(data, h, indent=indent)
                return True
        except FileNotFoundError as err:
            _logger.debug(err)
            return False

    def set_config(self, config_file, use_current):
        """ Write a new configuration to the current UltimateIO device """

        # Get the current configuration from the device
        cur_config = self.read_device() if use_current else None

        # Insert the new configuration into the PacStruct data object
        res, data = self._create_device_message_(config_file, cur_config)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.ULTIMATEIO_INDEX, data, ct.sizeof(data)) \
            if res else False

    def set_pin(self, pin_config):
        """ Write a pin to the current ipac4 device """
        pin = pin_config[0]
        # Get the current configuration from the device
        cur_config = self.read_device()
        macros = self._create_macro_array_(cur_config)

        action_index, alternate_action_index, shift_index = PinMapping[pin]
        action = pin_config[1].upper()
        cur_config.bytes[action_index] = 0
        if action in IPACSeriesMapping:
            cur_config.bytes[action_index] = IPACSeriesMapping[action]
        else:
            macro_val = 0xe0
            for x in macros:
                if x['name'].upper() == action:
                    cur_config.bytes[action_index] = macro_val
                else:
                    macro_val += 1
        if cur_config.bytes[action_index] == 0:
            _logger.info(_(f'{pin} action "{action}" is not a valid value'))

        # Pin alternate action
        alternate_action = pin_config[2].upper()
        # Empty string means no value
        if len(alternate_action) > 0:
            cur_config.bytes[alternate_action_index] = 0
            if alternate_action in IPACSeriesMapping:
                cur_config.bytes[alternate_action_index] = IPACSeriesMapping[alternate_action]
            else:
                macro_val = 0xe0
                for x in macros:
                    if x['name'].upper() == alternate_action:
                        cur_config.bytes[alternate_action_index] = macro_val
                    else:
                        macro_val += 1
            if cur_config.bytes[alternate_action_index] == 0:
                _logger.info(_(f'{pin} alternate action "{alternate_action}" is not a valid value'))
        else:
            # No Alternate Value
            cur_config.bytes[alternate_action_index] = 0

        # Pin designated as shift
        cur_config.bytes[shift_index] = 0x41 if pin_config[3].lower() in ['true', '1', 't', 'y'] else 0x01

        # Header - Setup to send back to device
        cur_config.header.type = 0x50
        cur_config.header.byte_2 = 0xdd
        cur_config.header.byte_3 = 0x0f

        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.ULTIMATEIO_INDEX,
                              cur_config, ct.sizeof(cur_config))

    def set_debounce(self, debounce):
        """ Set debounce value to the current ipac4 device """
        val = debounce.lower()
        if val in IPACSeriesDebounce:
            # Get the current configuration from the device
            cur_config = self.read_device()

            header = PacConfigUnion()
            header.asByte = cur_config.header.byte_4
            header.config.debounce = IPACSeriesDebounce[val]

            cur_config.header.byte_4 = header.asByte
        else:
            _logger.info(_(f'"{debounce}" is not a valid debounce value.'))
            _logger.info(_(f'Valid values are: {list(IPACSeriesDebounce.keys())}'))
            return None

        # Header - Setup to send back to device
        cur_config.header.type = 0x50
        cur_config.header.byte_2 = 0xdd
        cur_config.header.byte_3 = 0x0f

        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.ULTIMATEIO_INDEX,
                              cur_config, ct.sizeof(cur_config))

    def set_config_ui(self, config_dict: dict):
        """ Write a new configuration from UI to the current ipac4 device """

        # Insert the new configuration into the PacStruct data object
        res, data = self._create_device_struct_(config_dict)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.ULTIMATEIO_INDEX, data, ct.sizeof(data)) \
            if res else False

    def _create_device_message_(self, config_file: str, cur_device_config=None):
        """ Create the message to be sent to the device """

        # List of possible 'resourceType' values in the config file for an ultimateIO device.
        resource_types = ['ultimateIO-pin', 'ultimateIO-led']

        # Validate against the base schema.
        valid_config = self.validate_config_base(config_file, resource_types)
        if not valid_config:
            return False, None

        return self._create_device_struct_(valid_config, cur_device_config)

    def _create_device_struct_(self, json_config: dict, cur_device_config=None):
        data = cur_device_config if cur_device_config else PacStruct()
        config = JSONObject(json_config)

        if config.deviceClass != 'ultimateIO':
            _logger.error(_('Configuration device class is not "ultimateIO".'))
            return False, None

        # Determine which config resource type we have.
        if config.resourceType == 'ultimateIO-pin':
            if not self.validate_config(config, 'ultimateio-pin.schema'):
                return False, None

            # Prep the data structure
            data.bytes[13] = 0xff
            data.bytes[15] = 0xff
            data.bytes[63] = 0xff
            data.bytes[65] = 0xff

            for x in range(100, 149):
                data.bytes[x] = 0x01

            # set these back to 0
            data.bytes[108] = 0
            data.bytes[109] = 0
            data.bytes[113] = 0
            data.bytes[115] = 0
            data.bytes[116] = 0
            data.bytes[118] = 0
            data.bytes[120] = 0
            data.bytes[122] = 0
            data.bytes[139] = 0
            data.bytes[157] = 0x7f

            # Header
            data.header.type = 0x50
            data.header.byte_2 = 0xdd
            data.header.byte_3 = 0x0f

            # Header configuration options
            header = PacConfigUnion()
            val = config.debounce.lower()
            if val in IPACSeriesDebounce:
                header.config.debounce = IPACSeriesDebounce[val]
            else:
                _logger.info(_(f'"{config.debounce}" is not a valid debounce value'))
                return False, None

            # X Threshold
            data.bytes[156] = config.xThreshold

            # Y Threshold
            data.bytes[163] = config.yThreshold

            # bug: Current limitation, macros are not kept between configurations.  To prevent lingering macro
            #   values in pac structure
            # Clear current macro structure
            if cur_device_config is not None:
                for x in range(self.MACRO_START_INDEX, self.MACRO_MAX_COUNT):
                    data.bytes[x] = 0

            # key: Macro name value: macro value (e0 - fe)
            macro_dict = {}
            try:
                # Macros
                # Each macro starts with control character e0 - fe.  Total of 30 macros possible
                # overall total macro characters is 56
                cur_size_count = 0
                cur_macro = 0xe0
                cur_position = self.MACRO_START_INDEX

                if len(config.macros) > self.MACRO_MAX_COUNT:
                    _logger.debug(_(f'There are more than {self.MACRO_MAX_COUNT} '
                                    f'macros defined for the ultimateIO device'))
                    return False, None

                for macro in config.macros:
                    if len(macro.action) > 0:
                        # Set the start point of the new macro
                        data.bytes[cur_position] = cur_macro
                        macro_dict[macro.name.upper()] = cur_macro

                        cur_position += 1
                        cur_macro += 1
                        cur_size_count += 1

                        for action in macro.action:
                            if action.upper() in IPACSeriesMapping:
                                data.bytes[cur_position] = IPACSeriesMapping[action.upper()]
                                cur_position += 1
                                cur_size_count += 1

                            if cur_size_count > self.MACRO_MAX_SIZE:
                                _logger.debug(_(f'There are more than {self.MACRO_MAX_SIZE} '
                                                f'macro values defined for the ipac4 device'))
                                return False, None
            except AttributeError:
                pass

            # Pins
            # Places the action value, alternate action value and if assigned as shift key
            # 0x40 in the shift position for all pins designated as shift pins in json config
            for pin in config.pins:
                try:
                    action_index, alternate_action_index, shift_index = PinMapping[pin.name]
                    action = pin.action.upper()
                    if action in IPACSeriesMapping:
                        data.bytes[action_index] = IPACSeriesMapping[action]
                    elif action in macro_dict:
                        data.bytes[action_index] = macro_dict[action]
                    else:
                        _logger.info(_(f'{pin.name} action "{action}" is not a valid value'))

                    try:
                        alternate_action = pin.alternate_action.upper()
                        if alternate_action in IPACSeriesMapping:
                            data.bytes[alternate_action_index] = IPACSeriesMapping[alternate_action]
                        elif alternate_action in macro_dict:
                            data.bytes[alternate_action_index] = macro_dict[alternate_action]
                        elif alternate_action:
                            _logger.info(_(f'{pin.name} alternate action "{alternate_action}" is not a valid value'))
                    except AttributeError:
                        pass

                    # Pin designated as shift
                    try:
                        if pin.shift:
                            data.bytes[shift_index] = 0x40
                    except AttributeError:
                        pass

                except KeyError:
                    _logger.debug(_(f'Pin {pin.name} does not exists in ipac4 device'))

            return True, data

        return False, None
