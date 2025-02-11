#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing
import re
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QModelIndex, QObject, Property, Signal, QSortFilterProxyModel, QPersistentModelIndex

from python_easy_json import JSONObject
from ultimarc.devices import DeviceClassID
from ultimarc.devices.jpac import PinMapping, JpacDevice
from ultimarc.ui.action_model import ActionModel
from ultimarc.ui.devices.device import Device
from ultimarc.ui.macro_model import MacroModel
from ultimarc.ui.pac_filter_model import PacFilterModel

_logger = logging.getLogger('ultimarc')


class JpacRoles(IntEnum):
    NAME = 1
    ACTION = 2
    ALT_ACTION = 3
    SHIFT = 4
    DISABLED = 5


# Map Role Enum values to class property names.
jpacRoleMap = OrderedDict(zip(list(JpacRoles), [k.name.lower() for k in JpacRoles]))

class PacDetailsFilterProxyModel(QSortFilterProxyModel, QObject):
    _changed_filter_ = Signal(str)

    def __init__(self):
        super().__init__()
        self._filter = ''

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        index = self.sourceModel().index(source_row, 0, source_parent)

        pin_name = self.sourceModel().data(index, JpacRoles.NAME)
        if re.match(self._filter, pin_name) is None:
            return False

        return True

    def get_filter (self):
        return self._filter

    def set_filter(self, new_filter):
        self.beginResetModel()
        self._filter = new_filter
        self.endResetModel()
        self.invalidateFilter()

    filter = Property(str, get_filter, set_filter, notify=_changed_filter_)


class JpacUI(Device):
    _changed_debounce_ = Signal(str)
    _changed_paclink_ = Signal(bool)

    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(JpacUI, self).__init__(args, env, attached, device_class_id,
                                     name, device_class_descr, key)

        self.config = None
        self._json_obj = None

        self._action_model = ActionModel()
        self._alternate_action_model = ActionModel()
        self._macro_model_ = MacroModel()

        self._filter_model_ = PacFilterModel()
        self._filter_pins = PacDetailsFilterProxyModel()

    def populate(self):
        self._filter_model_.set_filter_names(['Player 1', 'Player 2', 'All'], ['1', '2', ''])
        self._filter_pins.setSourceModel(self)
        self._filter_pins.set_filter('1')

        if self.config is None:
            if self.attached:
                devices = [dev for dev in
                           self.env.devices.filter(class_id=DeviceClassID.JPAC, bus=self.args.bus,
                                                   address=self.args.address)]
                for dev in devices:
                    with dev as dev_h:
                        self.config = dev_h.to_json_str(dev_h.read_device())
            else:
                self.config = {'schemaVersion': 2.0, 'resourceType': 'jpac-pins',
                               'deviceClass': self.device_class_id.value, 'debounce': 'standard',
                               'paclink': False, 'pins': []}

            self._json_obj = JSONObject(self.config)

            self.set_macros()

    def get_qml(self):
        self.populate()
        return 'PacDetail.qml'

    def write_device(self):
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.JPAC, bus=self.args.bus,
                                           address=self.args.address)]
        for dev in devices:
            with dev as dev_h:
                return dev_h.set_config_ui(self.config)

    def write_file(self, file):
        if JpacDevice.validate_config(self.config, 'jpac.schema'):
            JpacDevice.write_to_file(JSONObject(self.config), file.toLocalFile(), indent=2)
            return True
        return False

    def load_file(self, file):
        resource_types = ['jpac-pins']
        config = JpacDevice.validate_config_base(file.toLocalFile(), resource_types)

        if config is not None:
            if JpacDevice.validate_config(config, 'jpac.schema'):
                self.config = config
                self._json_obj = JSONObject(self.config)
                self.set_macros()
                self._action_model.set_macro_names(self.config['macros'])
                self._alternate_action_model.set_macro_names(self.config['macros'])
                return True
        return False

    def roleNames(self) -> typing.Dict:
        roles = OrderedDict()
        for k, v in jpacRoleMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
        return len(PinMapping)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        pin_name = list(PinMapping)[index.row()]
        if role == JpacRoles.NAME:
            return pin_name

        for pin in self._json_obj.pins:
            if pin.name == pin_name:
                if role == JpacRoles.ACTION:
                    return pin.action
                if role == JpacRoles.ALT_ACTION:
                    try:
                        return pin.alternate_action
                    except AttributeError:
                        return ''
                if role == JpacRoles.SHIFT:
                    try:
                        return pin.shift
                    except AttributeError:
                        return False
#                if role == JpacRoles.DISABLED:

        else:
            return False if role == JpacRoles.SHIFT else ''

    def setData(self, index: QModelIndex, value, role: int = ...):
        pin_name = list(PinMapping)[index.row()]

        for pin in self.config['pins']:
            if pin['name'] == pin_name:
                break
        else:
            pin = {'name': pin_name, 'action': ''}
            self.config['pins'].append(pin)

        if role == JpacRoles.SHIFT:
            pin['shift'] = value

        if role == JpacRoles.ACTION:
            pin['action'] = value

        if role == JpacRoles.ALT_ACTION:
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

    def get_pac_filter(self):
        return self._filter_model_

    def get_pin_filter(self):
        return self._filter_pins

    actions = Property(QObject, get_action_model, constant=True)
    alt_actions = Property(QObject, get_alternate_action_model, constant=True)
    debounce = Property(str, get_debounce, set_debounce, notify=_changed_debounce_)
    paclink = Property(bool, get_paclink, set_paclink, notify=_changed_paclink_)
    macros = Property(QObject, get_macros, constant=True)
    update_macro = Property(bool, update_macros, constant=True)
    pac_filter = Property(QObject, get_pac_filter, constant=True)
    pin_filter = Property(QObject, get_pin_filter, constant=True)
