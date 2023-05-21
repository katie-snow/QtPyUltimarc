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

# Pin mapping for jpac device
# code_index: Normal action
# alternate_code_index: Alternate action
# alternate_index: Which pin is the shift code
# pin name: (action_index, alternate_action_index, shift_key)
PinMapping = {
    '1up': (24, 74, 124),
    '1down': (28, 78, 128),
    '1right': (36, 86, 136),
    '1left': (32, 82, 132),
    '2up': (26, 76, 126),
    '2down': (30, 80, 130),
    '2right': (38, 88, 138),
    '2left': (34, 84, 134),
    '1sw1': (16, 66, 116),
    '1sw2': (20, 70, 120),
    '1sw3': (0, 50, 100),
    '1sw4': (4, 54, 104),
    '1sw5': (19, 69, 119),
    '1sw6': (17, 67, 117),
    '1sw7': (39, 89, 139),
    '1sw8': (37, 87, 137),
    '2sw1': (18, 68, 118),
    '2sw2': (22, 72, 122),
    '2sw3': (2, 52, 102),
    '2sw4': (6, 56, 106),
    '2sw5': (31, 81, 131),
    '2sw6': (29, 79, 129),
    '2sw7': (33, 83, 133),
    '2sw8': (35, 85, 135),
    '1start': (44, 94, 144),
    '1coin': (40, 90, 140),
    '2start': (46, 96, 146),
    '2coin': (42, 92, 142),
    'test': (12, 62, 112),
    'tilt': (14, 64, 114),
    'service': (10, 60, 110)
}


class JpacDevice(USBDeviceHandle):
    """ Manage an jpac device """
    class_id = 'jpac'
    class_descr = _('JPAC')
    interface = 2
    JPAC_INDEX = ct.c_uint16(0x02)

    # Each macro starts with control character e0 - fe.  Total of 30 macros possible
    # overall total macro characters is 85
    MACRO_MAX_COUNT = 30
    MACRO_MAX_SIZE = 85
    MACRO_START_INDEX = 166

    # Disabled value
    DISABLED = 0xff

    def get_device_config(self, indent=None, file=None):
        """ Return a json string of the device configuration """
        config = self.read_device()
        print(config)
        json_obj = self.to_json_str(config)
        if file:
            if self.write_to_file(json_obj, file, indent):
                return _('Wrote jpac configuration to ' + file)
            else:
                return _('Failed to write jpac configuration to file.')
        else:
            return json.dumps(json_obj, indent=indent) if config else None

    def read_device(self):
        """ Return the configuration of the connected jpac """
        request = PacHeaderStruct(0x59, 0xdd, 0x0f, 0)
        ret = self.write(USBRequestCode.SET_CONFIGURATION, int(0x03), self.JPAC_INDEX,
                         request, ct.sizeof(request))
        return self.read_interrupt(0x84, PacStruct()) if ret else None

    def to_json_str(self, pac_struct):
        """ Converts a PacStruct to a json object """
        json_obj = {'schemaVersion': 2.0, 'resourceType': 'jpac-pins', 'deviceClass': self.class_id}

        # header configuration
        header = PacConfigUnion()
        header.asByte = pac_struct.header.byte_4
        json_obj['debounce'] = get_ipac_series_debounce_key(header.config.debounce)
        json_obj['paclink'] = True if header.config.paclink == 0x01 else False

        # macros
        macros = self._create_macro_array_(pac_struct)
        if len(macros):
            json_obj['macros'] = macros

        # pins
        pins = []
        for key in PinMapping:
            action_index, alternate_action_index, shift_index = PinMapping[key]
            pin = {'name': key}

            # Disabled pins have an action_index of 0xff for j-pac
            if pac_struct.bytes[action_index] is not self.DISABLED:
                pin['action'] = get_ipac_series_mapping_key(pac_struct.bytes[action_index])
                if pin['action'] is None:
                    mi = get_ipac_series_macro_mapping_index(pac_struct.bytes[action_index])
                    if mi is not None:
                        pin['action'] = macros[mi]['name']
                    else:
                        _logger.error(_(f'{key} action is not a valid value'))
                if pac_struct.bytes[alternate_action_index]:
                    alt_action = get_ipac_series_mapping_key(pac_struct.bytes[alternate_action_index])
                    if alt_action is None:
                        mi = get_ipac_series_macro_mapping_index(pac_struct.bytes[alternate_action_index])
                        if mi is not None:
                            pin['alternate_action'] = macros[mi]['name']
                    else:
                        pin['alternate_action'] = alt_action
                if pac_struct.bytes[shift_index] == 0x41 or \
                        pac_struct.bytes[shift_index] == 0x40:
                    pin['shift'] = True
            else:
                pin['disabled'] = True
                pin['action'] = ''
            pins.append(pin)
        json_obj['pins'] = pins

        return json_obj if self.validate_config(json_obj, 'jpac.schema') else None

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
    def write_to_file(cls, data: JSONObject, file_path, indent=None):
        try:
            with open(file_path, 'w') as h:
                h.write(data.to_json(indent))
                return True
        except FileNotFoundError as err:
            _logger.debug(err)
            return False

    def set_config(self, config_file, use_current):
        """ Write a new configuration to the current JPAC device """

        # Get the current configuration from the device
        cur_config = self.read_device() if use_current else None

        # Insert the new configuration into the PacStruct data object
        res, data = self._create_device_message_(config_file, cur_config)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.JPAC_INDEX, data, ct.sizeof(data)) \
            if res else False

    def set_pin(self, pin_config):
        """ Write a pin to the current jpac device """
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

        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.JPAC_INDEX,
                              cur_config, ct.sizeof(cur_config))

    def set_debounce(self, debounce):
        """ Set debounce value to the current jpac device """
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

        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.JPAC_INDEX,
                              cur_config, ct.sizeof(cur_config))

    def set_paclink(self, paclink):
        """ Set paclink value to the current jpac device """

        # Get the current configuration from the device
        cur_config = self.read_device()

        header = PacConfigUnion()
        header.asByte = cur_config.header.byte_4
        header.config.paclink = 0x01 if paclink is True else 0

        cur_config.header.byte_4 = header.asByte

        # Header - Setup to send back to device
        cur_config.header.type = 0x50
        cur_config.header.byte_2 = 0xdd
        cur_config.header.byte_3 = 0x0f

        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.JPAC_INDEX,
                              cur_config, ct.sizeof(cur_config))

    def set_config_ui(self, config_dict: dict):
        """ Write a new configuration from UI to the current jpac device """

        # Insert the new configuration into the PacStruct data object
        res, data = self._create_device_struct_(config_dict)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), self.JPAC_INDEX, data, ct.sizeof(data)) \
            if res else False

    def _create_device_message_(self, config_file: str, cur_device_config=None):
        """ Create the message to be sent to the device """

        # List of possible 'resourceType' values in the config file for a jpac device.
        resource_types = ['jpac-pins']

        # Validate against the base schema.
        valid_config = self.validate_config_base(config_file, resource_types)
        if not valid_config:
            return False, None

        return self._create_device_struct_(valid_config, cur_device_config)

    def _create_device_struct_(self, json_config: dict, cur_device_config=None):
        data = cur_device_config if cur_device_config else PacStruct()
        config = JSONObject(json_config)

        if config.deviceClass != 'jpac':
            _logger.error(_('Configuration device class is not "jpac".'))
            return False, None

        # Determine which config resource type we have.
        if config.resourceType == 'jpac-pins':
            if not self.validate_config(config, 'jpac.schema'):
                return False, None

            # Prep the data structure
            for x in range(1, 50):
                data.bytes[x] = 0xff

            for x in range(100, 107):
                data.bytes[x] = 0x01

            data.bytes[112] = 0x01
            data.bytes[114] = 0x01
            for x in range(116, 121):
                data.bytes[x] = 0x01

            data.bytes[124] = 0x01
            data.bytes[126] = 0x01
            for x in range(128, 141):
                data.bytes[x] = 0x01

            data.bytes[142] = 0x01
            data.bytes[144] = 0x01
            data.bytes[146] = 0x01

            for x in range(152, 158):
                data.bytes[x] = 0x80

            data.bytes[158] = 0x0a
            for x in range(159, 166):
                data.bytes[x] = 0x10
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

            header.config.paclink = 0x1 if config.paclink is True else 0
            data.header.byte_4 = header.asByte

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
                # overall total macro characters is 85
                cur_size_count = 0
                cur_macro = 0xe0
                cur_position = self.MACRO_START_INDEX

                if len(config.macros) > self.MACRO_MAX_COUNT:
                    _logger.debug(_(f'There are more than {self.MACRO_MAX_COUNT} '
                                    f'macros defined for the jpac device'))
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
                                                f'macro values defined for the jpac device'))
                                return False, None
            except AttributeError:
                pass

            # Pins
            # Places the action value, alternate action value and if assigned as shift key
            # 0x40 in the shift position for all pins designated as shift pins in json config
            for pin in config.pins:
                try:
                    action_index, alternate_action_index, shift_index = PinMapping[pin.name]
                    action = 0
                    try:
                        # The pin is disabled if disabled is present.  Schema only allows true
                        if pin.disabled:
                            action = self.DISABLED
                    except AttributeError:
                        action = pin.action.upper()

                    if action is not self.DISABLED:
                        if action in IPACSeriesMapping:
                            data.bytes[action_index] = IPACSeriesMapping[action]
                        elif action in macro_dict:
                            data.bytes[action_index] = macro_dict[action]
                        else:
                            _logger.info(_(f'{pin.name} action "{action}" is not a valid value'))
                    else:
                        # the pin is disabled don't update any other bytes for this pin
                        data.bytes[action_index] = self.DISABLED
                        continue

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
                            data.bytes[shift_index] = 0x41
                    except AttributeError:
                        pass

                except KeyError:
                    _logger.debug(_(f'Pin {pin.name} does not exists in jpac device'))

            return True, data

        return False, None
