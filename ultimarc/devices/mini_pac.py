#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import logging

from ultimarc import translate_gettext as _
from ultimarc.devices._device import USBDeviceHandle

MINI_PAC_SET_REPORT = ct.c_uint8(0x09)
MINI_PAC_INDEX = ct.c_uint16(0x02)


class MiniPacDevice(USBDeviceHandle):
    """ Manage a MINI-pac device """
    class_id = 'mini-pac'  # Used to match/filter devices
    class_descr = _('Mini-PAC')
    interface = 2

    def get_current_configuration(self):
        """ Return the current Mini-PAC pins configuration """

        request = (ct.c_uint8 * 4)(0x59, 0xdd, 0x0f, 0)
        ret = self.write(MINI_PAC_SET_REPORT, int(0x03), MINI_PAC_INDEX,
                         request, ct.sizeof(request))

        actual_length = int(0)

        if ret:
            # TODO-Katie: Create loop and structure to handle all the data coming in
            ret = self.read_interrupt(0x84, request, 5, actual_length)
            print(_(' '.join(hex(x) for x in request)))
