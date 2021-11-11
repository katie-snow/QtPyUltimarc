#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing

from PySide6.QtCore import QModelIndex

from ultimarc.devices import DeviceClassID
from ultimarc.devices.mini_pac import PinMapping
from ultimarc.system_utils import JSONObject
from ultimarc.ui.devices.device import Device
from ultimarc.ui.device_details_model import DeviceDataRoles

_logger = logging.getLogger('ultimarc')


class MiniPacUI(Device):
    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(MiniPacUI, self).__init__(args, env, attached, device_class_id, name, device_class_descr, key)

        self.icon = 'qrc:/logos/workstation'
        self.config = None

        if attached:
            devices = [dev for dev in
                       self.env.devices.filter(class_id=DeviceClassID.MiniPac, bus=self.args.bus,
                                               address=self.args.address)]
            for dev in devices:
                with dev as dev_h:
                    self.config = JSONObject(dev_h.to_json_str(dev_h.get_current_configuration()))
                    # _logger.info(self.config)
        else:
            self.config = JSONObject({'schemaVersion': 2.0, 'resourceType': 'mini-pac-pins',
                              'deviceClass': self.device_class_id, 'debounce': 'standard', 'pins': []})

    def get_description(self):
        return 'This is the description of the Mini-pac device'

    def get_qml(self):
        return 'PinDetail.qml'

    def rowCount(self):
        return len(PinMapping)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        pin_name = list(PinMapping)[index.row()]
        if role == DeviceDataRoles.NAME:
            return pin_name

        try:
            if len(self.config.pins) > 0:
                for pin in self.config.pins:
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
        except AttributeError:
            return False if role == DeviceDataRoles.SHIFT else ''

    def setData(self, index: QModelIndex, value, role: int = ...):
        pin_name = list(PinMapping)[index.row()]
        cur_pin = None

        try:
            if len(self.config.pins) > 0:
                for pin in self.config.pins:
                    if pin.name == pin_name:
                        cur_pin = pin
                        break
        except AttributeError:
            pass

        update_pin = False
        if cur_pin is None:
            cur_pin = JSONObject({'name': pin_name, 'action': '', 'alternate_action': '', 'shift': False})

        if role == DeviceDataRoles.SHIFT:
            cur_pin.shift = value
            update_pin = True

        if role == DeviceDataRoles.ACTION:
            cur_pin.action = value
            update_pin = True

        if role == DeviceDataRoles.ALT_ACTION:
            cur_pin.alternate_action = value
            update_pin = True

        if update_pin:
            self.config.pins.append(cur_pin)
            return True

        return False
