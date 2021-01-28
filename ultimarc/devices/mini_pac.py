#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode
from ultimarc.devices._mappings import IPACSeriesMapping
from ultimarc.devices._structures import PacHeaderStruct, PacStruct
from ultimarc.system_utils import JSONObject

_logger = logging.getLogger('ultimarc')

MINI_PAC_INDEX = ct.c_uint16(0x02)

# Pin mapping for Mini-pac device
# code_index: Normal action
# alternate_code_index: Alternate action
# alternate_index: Which pin is the shift code
# pin name: (action_index, alternate_action_index, shift_key)
PinMapping = {
    '1up': (10, 80, 110),
    '1down': (8, 58, 108),
    '1right': (14, 64, 114),
    '1left': (12, 62, 112),
    '2up': (37, 87, 137),
    '2down': (39, 89, 139),
    '2right': (33, 83, 133),
    '2left': (35, 85, 135),
    '1sw1': (9, 59, 109),
    '1sw2': (11, 61, 111),
    '1sw3': (13, 63, 113),
    '1sw4': (15, 65, 115),
    '1sw5': (41, 91, 141),
    '1sw6': (43, 93, 143),
    '1sw7': (45, 95, 145),
    '1sw8': (47, 97, 147),
    '2sw1': (17, 67, 117),
    '2sw2': (19, 69, 119),
    '2sw3': (21, 71, 121),
    '2sw4': (23, 73, 123),
    '2sw5': (1, 51, 101),
    '2sw6': (3, 53, 103),
    '2sw7': (5, 55, 105),
    '2sw8': (7, 57, 107),
    '1start': (25, 75, 125),
    '1coin': (29, 79, 129),
    '1a': (6, 56, 106),
    '1b': (4, 54, 104),
    '2start': (27, 77, 127),
    '2coin': (31, 81, 131),
    '2a': (2, 52, 102),
    '2b': (0, 50, 100)
}


class MiniPacDevice(USBDeviceHandle):
    """ Manage a MINI-pac device """
    class_id = 'mini-pac'  # Used to match/filter devices
    class_descr = _('Mini-PAC')
    interface = 2

    def get_current_configuration(self):
        """ Return the current Mini-PAC pins configuration """
        request = PacHeaderStruct(0x59, 0xdd, 0x0f, 0)
        ret = self.write(USBRequestCode.SET_CONFIGURATION, int(0x03), MINI_PAC_INDEX,
                         request, ct.sizeof(request))

        if ret:
            return self.read_interrupt(0x84, PacStruct())

    def set_config(self, config_file):
        """ Write a new configuration to the current Mini-PAC device """
        # Get the current configuration from the device
        cur_config = self.get_current_configuration()

        # Insert the new configuration into the PacStruct data object
        res, data = self._create_message_(config_file)
        return self.write_alt(USBRequestCode.SET_CONFIGURATION, int(0x03), MINI_PAC_INDEX, data, ct.sizeof(data)) \
            if res else False

    def _create_message_(self, config_file, cur_device_config=None):
        """ Create the message to be sent to the device """
        data = PacStruct()

        # List of possible 'resourceType' values in the config file for a Mini-pac device.
        resource_types = ['mini-pac-pins']

        # Validate against the base schema.
        config = JSONObject(self.validate_config_base(config_file, resource_types))
        if not config:
            return False, None

        if config.deviceClass != 'mini-pac':
            _logger.error(_('Configuration device class is not "mini-pac".'))
            return False, None

        # Determine which config resource type we have.
        if config.resourceType == 'mini-pac-pins':
            if not self.validate_config(config, 'mini-pac.schema'):
                return False, None

            # Pins
            # Places the action value, alternate action value and if assigned as shift key
            # 0x41 in the shift_key position for all pins in json config
            shift_key = config.shift_key

            for pin in config.pins:
                try:
                    action_index, alternate_action_index, shift_key_index = PinMapping[pin.name]
                    action = pin.action.upper()
                    if action:
                        data.bytes[action_index] = IPACSeriesMapping[action]

                    alternate_action = pin.alternate_action.upper()
                    if alternate_action:
                        data.bytes[alternate_action_index] = IPACSeriesMapping[alternate_action]

                    if shift_key.upper() == pin.name.upper():
                        data.bytes[shift_key_index] = 0x41
                except KeyError:
                    _logger.debug(_(f'Pin {pin.name} does not exists in Mini-pac device'))

            # Macros
            # Each macro starts with control character e0 - fe.  Total of 30 macros possible
            # overall total macro characters is 85
            max_size = 85
            max_macro = 30
            cur_size_count = 0
            cur_macro_count = 0
            cur_macro = 0xe0
            cur_position = 167

            for macro in config.macros:
                if len(macro.action) > 0:
                    data.bytes[cur_position] = cur_macro
                    cur_position += 1
                    cur_macro += 1

                    if cur_macro_count > max_macro:
                        _logger.debug(_(f'There are more than {max_macro} macros defined for the Mini-pac device'))
                        return False, None

                    for action in macro.action:
                        data.bytes[cur_position] = IPACSeriesMapping[action.upper()]
                        cur_position += 1

                        if cur_size_count > max_size:
                            _logger.debug\
                                (_(f'There are more than {max_size} macro values defined for the Mini-pac device'))
                            return False, None

            return True, data

        return False, None
