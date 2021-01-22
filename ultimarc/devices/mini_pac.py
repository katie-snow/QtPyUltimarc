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
