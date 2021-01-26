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

PinMapping = {
    """ Pin mapping for Mini-pac device
    code_index: Normal action
    shifted_code_index: Shifted action
    shift_key_index: Which code is the shift code 
    pin name: (action_index, shifted_action_index, shift_action_index) 
    """
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
    '1sw6': (45, 95, 145),
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
        data = None
        return self.write(USBRequestCode.SET_CONFIGURATION, int(0x03), MINI_PAC_INDEX, data, ct.sizeof(data))

        #return False

    def _create_message_(self, config_file, cur_device_config=None):
        """ Create the message to be sent to the device """
        data = PacStruct()

        # List of possible 'resourceType' values in the config file for a Mini-pac device.
        resource_types = ['mini-pac-pins']

        # Validate against the base schema.
        config = JSONObject(self.validate_config_base(config_file, resource_types))
        if not config:
            return False

        if config['deviceClass'] != 'mini-pac':
            _logger.error(_('Configuration device class is not "mini-pac".'))
            return False

        # Determine which config resource type we have.
        if config['resourceType'] == 'mini-pac-pins':
            if not self.validate_config(config, 'mini-pac.schema'):
                return False

            # Dict - JSONObject of pins
            # Dict - PINMap
            # Need to go through the JSONObject get the name, action and shift_action, place
            # place those values in the PacStruct Object
            for obj in config['pins'].items():
                mapping = PinMapping[obj.name]
                data[mapping[0]] = IPACSeriesMapping[obj.action]
                data[mapping[1]] = IPACSeriesMapping[obj.shift_action]

            return data

        return None