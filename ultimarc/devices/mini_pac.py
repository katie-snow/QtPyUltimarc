#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle


MINI_PAC_SET_REPORT = ct.c_uint8(0x09)
MINI_PAC_INDEX = ct.c_uint8(0x02)


class MiniPacDevice(USBDeviceHandle):
    """ Manage a MINI-pac device """
    class_id = 'mini-pac'  # Used to match/filter devices
    class_descr = _('Mini-PAC')
    interface = 2

    def get_current_configuration(self):
        """ Return the current Mini-PAC pins configuration """

        request = [0x59, 0xdd, 0x0f, 0]
        ret = self.write(MINI_PAC_SET_REPORT, ct.c_uint8(0x203), MINI_PAC_INDEX, \
                         request, ct.sizeof(request))
