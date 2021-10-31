#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing

from PySide6.QtCore import QModelIndex

from ultimarc.devices import DeviceClassID
from ultimarc.devices.mini_pac import PinMapping, MiniPacDevice
from ultimarc.system_utils import JSONObject
from ultimarc.ui.device import Device
from ultimarc.ui.device_details_model import DeviceDataRoles

_logger = logging.getLogger('ultimarc')


class MiniPacUI(Device):
    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(MiniPacUI, self).__init__(args, env, attached, device_class_id, name, device_class_descr, key)

        self.icon = 'qrc:/logos/workstation'
        self.json_data = None

        if attached:
            devices = [dev for dev in
                       self.env.devices.filter(class_id=DeviceClassID.MiniPac, bus=self.args.bus,
                                               address=self.args.address)]
            for dev in devices:
                with dev as dev_h:
                    self.json_data = JSONObject(dev_h.to_json_str(dev_h.get_current_configuration()))
                    _logger.info(self.json_data)

    def get_description(self):
        return 'This is the description of the Mini-pac device'

    def rowCount(self):
        return len(PinMapping)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        pin_name = list(PinMapping)[index.row()]
        if role == DeviceDataRoles.NAME:
            return pin_name

        if self.json_data:
            for pin in self.json_data.pins:
                if pin.name == pin_name:
                    if role == DeviceDataRoles.ACTION:
                        return pin.action
                    if role == DeviceDataRoles.ALT_ACTION:
                        try:
                            return pin.alternate_action
                        except AttributeError:
                            return ''
                    if role == DeviceDataRoles.SHIFT:
                        try:
                            return pin.shift
                        except AttributeError:
                            return False
        else:
            return False if role == DeviceDataRoles.SHIFT else ''
        return None
