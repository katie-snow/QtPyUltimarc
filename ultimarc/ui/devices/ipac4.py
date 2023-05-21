#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QModelIndex, QObject, Property, Signal

from python_easy_json import JSONObject
from ultimarc.devices import DeviceClassID
from ultimarc.devices.ipac4 import PinMapping, Ipac4Device
from ultimarc.ui.action_model import ActionModel
from ultimarc.ui.devices.device import Device
from ultimarc.ui.macro_model import MacroModel

_logger = logging.getLogger('ultimarc')


class Ipac4Roles(IntEnum):
    NAME = 1
    ACTION = 2
    ALT_ACTION = 3
    SHIFT = 4


# Map Role Enum values to class property names.
ipac4RoleMap = OrderedDict(zip(list(Ipac4Roles), [k.name.lower() for k in Ipac4Roles]))


class Ipac4UI(Device):
    _changed_debounce_ = Signal(str)
    _changed_paclink_ = Signal(bool)

    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(Ipac4UI, self).__init__(args, env, attached, device_class_id,
                                      name, device_class_descr, key)

        self.icon = 'qrc:/logos/workstation'
        self.description = '56-Input USB interface for buttons and joysticks'
        self.config = None
        self._json_obj = None

        self._action_model = ActionModel()
        self._alternate_action_model = ActionModel()
        self._macro_model_ = MacroModel()

    def populate(self):
        if self.config is None:
            if self.attached:
                devices = [dev for dev in
                           self.env.devices.filter(class_id=DeviceClassID.Ipac4, bus=self.args.bus,
                                                   address=self.args.address)]
                for dev in devices:
                    with dev as dev_h:
                        self.config = dev_h.to_json_str(dev_h.read_device())
            else:
                self.config = {'schemaVersion': 2.0, 'resourceType': 'ipac4-pins',
                               'deviceClass': self.device_class_id.value, 'debounce': 'standard',
                               'paclink': False, 'pins': []}

            self._json_obj = JSONObject(self.config)

            self.set_macros()

    def get_qml(self):
        self.populate()
        return 'PacDetail.qml'

    def write_device(self):
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.IPAC4, bus=self.args.bus,
                                           address=self.args.address)]
        for dev in devices:
            with dev as dev_h:
                return dev_h.set_config_ui(self.config)

    def write_file(self, file):
        if Ipac4Device.validate_config(self.config, 'ipac4.schema'):
            Ipac4Device.write_to_file(self.config, file.toLocalFile(), indent=2)
            return True
        return False

    def load_file(self, file):
        resource_types = ['ipac4-pins']
        config = Ipac4Device.validate_config_base(file.toLocalFile(), resource_types)

        if config is not None:
            if Ipac4Device.validate_config(config, 'ipac4.schema'):
                self.config = config
                self._json_obj = JSONObject(self.config)
                self.set_macros()
                self._action_model.set_macro_names(self.config['macros'])
                self._alternate_action_model.set_macro_names(self.config['macros'])
                return True
        return False

    def roleNames(self):
        return ipac4RoleMap.items()

    def rowCount(self):
        return len(PinMapping)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        pin_name = list(PinMapping)[index.row()]
        if role == Ipac4Roles.NAME:
            return pin_name

        for pin in self._json_obj.pins:
            if pin.name == pin_name:
                if role == Ipac4Roles.ACTION:
                    return pin.action
                if role == Ipac4Roles.ALT_ACTION:
                    try:
                        return pin.alternate_action
                    except AttributeError:
                        return ''
                if role == Ipac4Roles.SHIFT:
                    try:
                        return pin.shift
                    except AttributeError:
                        return False
        else:
            return False if role == Ipac4Roles.SHIFT else ''

    def setData(self, index: QModelIndex, value, role: int = ...):
        pin_name = list(PinMapping)[index.row()]

        for pin in self.config['pins']:
            if pin['name'] == pin_name:
                break
        else:
            pin = {'name': pin_name, 'action': ''}
            self.config['pins'].append(pin)

        if role == Ipac4Roles.SHIFT:
            pin['shift'] = value

        if role == Ipac4Roles.ACTION:
            pin['action'] = value

        if role == Ipac4Roles.ALT_ACTION:
            pin['alternate_action'] = value

        self._json_obj = JSONObject(self.config)
        return True

    def set_macros(self):
        try:
            self._macro_model_.set_macros(self.config['macros'])
        except KeyError:
            pass

    def get_debounce(self):
        return self._json_obj.debounce

    def set_debounce(self, debounce):
        self.config['debounce'] = debounce
        self._json_obj = JSONObject(self.config)

    def get_action_model(self):
        return self._action_model

    def get_alternate_action_model(self):
        return self._alternate_action_model

    def get_paclink(self):
        return self._json_obj.paclink

    def set_paclink(self, paclink):
        self.config['paclink'] = paclink
        self._json_obj = JSONObject(self.config)

    def get_macros(self):
        return self._macro_model_

    def update_macros(self):
        self.config['macros'] = self._macro_model_.get_macros()
        self._action_model.set_macro_names(self.config['macros'])
        self._alternate_action_model.set_macro_names(self.config['macros'])

    actions = Property(QObject, get_action_model, constant=True)
    alt_actions = Property(QObject, get_alternate_action_model, constant=True)
    debounce = Property(str, get_debounce, set_debounce, notify=_changed_debounce_)
    paclink = Property(bool, get_paclink, set_paclink, notify=_changed_paclink_)
    macros = Property(QObject, get_macros, constant=True)
    update_macro = Property(bool, update_macros, constant=True)
