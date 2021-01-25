#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle, USBRequestCode
from ultimarc.devices._structures import PacHeaderStruct, PacStruct

_logger = logging.getLogger('ultimarc')

MINI_PAC_INDEX = ct.c_uint16(0x02)

PINMAP = {
    """ Pin map for device
    code_index: Normal key press action
    shifted_code_index: Shifted key press action
    shift_key_index: Which key is the shift key 
    pin name: (code_index, shifted_code_index, shift_key_index) 
    """
    '1up': (11, 81, 111),
    '1down': (9, 59, 109),
    '1right': (15, 65, 115),
    '1left': (12, 63,113),
    '2up': (38, 88, 138),
    '2down': (40, 90, 140),
    '2right': (34, 84, 134),
    '2left': (36, 86, 136),
    '1sw1': (10, 60, 110),
    '1sw2': (12, 62, 112),
    '1sw3': (14, 64, 114),
    '1sw4': (16, 66, 116),
    '1sw5': (42, 92, 142),
    '1sw6': (46, 96, 146),
    '1sw8': (48, 98, 148),
    '2sw1': (18, 68, 118),
    '2sw2': (20, 70, 120),
    '2sw3': (22, 72, 122),
    '2sw4': (24, 74, 124),
    '2sw5': (2, 52, 104),
    '2sw6': (4, 54, 106),
    '2sw7': (6, 56, 106),
    '2sw8': (8, 58, 108),
    '1start': (26, 76, 126),
    '1coin': (30, 80, 130),
    '1a': (7, 57, 107),
    '1b': (5, 55, 105),
    '2start': (28, 78, 128),
    '2coin': (32, 82, 132),
    '2a': (3, 53, 103),
    '2b': (1, 51, 101)
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

        # List of possible 'resourceType' values in the config file for a USB button.
        resource_types = ['mini-pac-pins']

        # Validate against the base schema.
        config = self.validate_config_base(config_file, resource_types)
        if not config:
            return False

        if config['deviceClass'] != 'mini-pac':
            _logger.error(_('Configuration device class is not "mini-pac".'))
            return False

        # Determine which config resource type we have.
        if config['resourceType'] == 'mini-pac-pins':
            if not self.validate_config(config, 'mini-pac.schema'):
                return False

            # Insert the new configuration into the PacStruct data object
            data = None
            return self.write(USBRequestCode.SET_CONFIGURATION, int(0x03), MINI_PAC_INDEX, data, ct.sizeof(data))

        return False
