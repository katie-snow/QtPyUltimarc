#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing

from PySide6.QtCore import QModelIndex

from ultimarc.devices.mini_pac import PinMapping
from ultimarc.ui.device import Device
from ultimarc.ui.device_details_model import DeviceDataRoles

_logger = logging.getLogger('ultimarc')


class MiniPacUI(Device):
    def __init__(self, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(MiniPacUI, self).__init__(attached, device_class_id, name, device_class_descr, key)

        self.icon = 'qrc:/logos/workstation'

    def get_description(self):
        return 'This is the description of the Mini-pac device'

    def rowCount(self):
        return len(PinMapping)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == DeviceDataRoles.NAME:
            return list(PinMapping)[index.row()]
