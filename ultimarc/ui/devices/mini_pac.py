#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import logging
import typing

from PySide6.QtCore import QModelIndex

from ultimarc.devices import DeviceClassID
from ultimarc.devices.mini_pac import PinMapping, MiniPacDevice

from ultimarc.ui.devices.device import Device
from ultimarc.ui.device_details_model import DeviceDataRoles
from ultimarc.system_utils import JSONObject

_logger = logging.getLogger('ultimarc')


class MiniPacUI(Device):
    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(MiniPacUI, self).__init__(args, env, attached, device_class_id,
                                        name, device_class_descr, key)

        self.icon = 'qrc:/logos/workstation'
        self.config = None
        self._json_obj = None

    def get_description(self):
        return 'This is the description of the Mini-pac device'

    def load_config(self):
        if self.config is None:
            if self.attached:
                devices = [dev for dev in
                           self.env.devices.filter(class_id=DeviceClassID.MiniPac, bus=self.args.bus,
                                                   address=self.args.address)]
                for dev in devices:
                    with dev as dev_h:
                        self.config = dev_h.to_json_str(dev_h.get_current_configuration())
            else:
                self.config = {'schemaVersion': 2.0, 'resourceType': 'mini-pac-pins',
                               'deviceClass': self.device_class_id.value, 'debounce': 'standard', 'pins': []}

            self._json_obj = JSONObject(self.config)

    def get_qml(self):
        self.load_config()
        return 'PinDetail.qml'

    def write_device(self):
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.MiniPac, bus=self.args.bus,
                                           address=self.args.address)]
        for dev in devices:
            with dev as dev_h:
                return dev_h.set_config_ui(self.config)

    def write_file(self, file):
        if MiniPacDevice.validate_config(self.config, 'mini-pac.schema'):
            MiniPacDevice.write_to_file(self.config, file.toLocalFile(), indent=2)
            return True
        return False

    def load_file(self, file):
        resource_types = ['mini-pac-pins']
        config = MiniPacDevice.validate_config_base(file.toLocalFile(), resource_types)

        if config is not None:
            if MiniPacDevice.validate_config(config, 'mini-pac.schema'):
                self.config = config
                self._json_obj = JSONObject(self.config)
                return True
        return False

    def rowCount(self):
        return len(PinMapping)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        pin_name = list(PinMapping)[index.row()]
        if role == DeviceDataRoles.NAME:
            return pin_name

        for pin in self._json_obj.pins:
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

    def setData(self, index: QModelIndex, value, role: int = ...):
        pin_name = list(PinMapping)[index.row()]

        for pin in self.config['pins']:
            if pin['name'] == pin_name:
                break
        else:
            pin = {'name': pin_name, 'action': ''}
            self.config['pins'].append(pin)

        if role == DeviceDataRoles.SHIFT:
            pin['shift'] = value

        if role == DeviceDataRoles.ACTION:
            pin['action'] = value

        if role == DeviceDataRoles.ALT_ACTION:
            pin['alternate_action'] = value

        self._json_obj = JSONObject(self.config)
        return True

    def get_debounce(self):
        return self._json_obj.debounce

    def set_debounce(self, debounce):
        self.config['debounce'] = debounce
        self._json_obj = JSONObject(self.config)

