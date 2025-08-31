#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing

from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, QMetaEnum
from PySide6.QtCore import  Property, Signal

from python_easy_json import JSONObject

from ultimarc.devices import DeviceClassID
from ultimarc.devices.usb_button import USBButtonDevice
from ultimarc.ui.action_model import ActionModel

from ultimarc.ui.devices.device import Device

_logger = logging.getLogger('ultimarc')

KEYCOUNT = 24

class UsbButtonRoles(IntEnum):
    MODE = 1
    ACTION = 2
    RELEASE_COLOR = 4
    PRESSED_COLOR = 5

usbButtonRoleMap = OrderedDict(zip(list(UsbButtonRoles), [k.name.lower() for k in UsbButtonRoles]))


class KeySequenceUI(QAbstractListModel, QObject):
    #_change_key_ = Signal(str)
    #_change_index_ = Signal(int)

    def __init__(self):
        super().__init__()
        self._config = [''] * KEYCOUNT

    class SequenceRoles(QMetaEnum):
        ACTION = 1

    def roleNames(self) -> typing.Optional[typing.Dict]:
        roles = {
            self.SequenceRoles.ACTION: 'action'.encode('utf-8')
        }
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return KEYCOUNT

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        # _logger.debug(f'role={role} index={index.row()}')

        if role == self.SequenceRoles.ACTION:
            # _logger.debug(f'action={self._config[index.row()]}')
            return self._config[index.row()]

        _logger.debug(f'action=None')
        return None

    def setData(self, index: QModelIndex, value, role: int = ...) -> None:
        if role == self.SequenceRoles.ACTION:
            self._config[index.row()] = value

    def get_config(self):
        return self._config


class UsbButtonUI(Device):
    _changed_released_ = Signal(int)
    _changed_pressed_ = Signal(int)

    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(UsbButtonUI, self).__init__(args, env, attached, device_class_id,
                                          name, device_class_descr, key)

        self.config_color = None
        self.config_keys = None
        self._json_color = None
        self._json_keys = None

        self._action_model = ActionModel()

        self._primary_key_sequence = KeySequenceUI()
        self._secondary_key_sequence = KeySequenceUI()

    def get_qml(self):
        self.populate()
        return 'UsbButtonDetail.qml'

    def populate(self):
        if self.config_color is None:
            if self.attached:
                devices = [dev for dev in
                           self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                                   address=self.args.address)]
                for dev in devices:
                    with dev as dev_h:
                        self.config_color = dev_h.to_json_str(dev_h.get_color())
            else:
                self.config_color = {'schemaVersion': 2.0, 'resourceType': 'usb-button-color',
                                     'deviceClass': self.device_class_id.value,
                                     'colorRGB': {'red': 1, 'green': 1, 'blue': 1}}

                self.config_keys = {}
                # self.config_keys = {'schemaVersion': 2.0, 'resourceType': 'usb-button-color',
                #                      'deviceClass': self.device_class_id.value, 'action': 'extended',
                #                     'pressedColor': {'red': 255, 'green': 255, 'blue': 255},
                #                     'releasedColor': {'red': 255, 'green': 255, 'blue': 255},
                #                     'keys': {{'sequence': 'primary', 'row1': [], 'row2': [], 'row3': [], 'row4': []},
                #                     {'sequence': 'secondary', 'row1': [], 'row2': [], 'row3': [], 'row4': []}}}

        self._json_color = JSONObject(self.config_color)
        self._json_keys = JSONObject(self.config_keys)

    def write_device(self):
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                           address=self.args.address)]
        for dev in devices:
            with dev as dev_h:
                return dev_h.set_config_ui(self.config)

    def roleNames(self) -> typing.Optional[typing.Dict]:
        roles = OrderedDict()
        for k, v in usbButtonRoleMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        return True

    def get_action_model(self):
        return self._action_model

    def get_primary_key_sequence(self):
        return self._primary_key_sequence

    def get_secondary_key_sequence(self):
        return self._secondary_key_sequence

    def get_released_color (self):
        return self._json_keys.releasedColor

    def set_released_color(self, color):
        self._json_keys.releasedColor = color

    def get_pressed_color(self):
        return self._json_keys.pressedColor

    def set_pressed_color(self, color):
        self._json_keys.pressedColor = color

    action_model = Property(QObject, get_action_model, constant=True)
    primary_key_sequence = Property(QObject, get_primary_key_sequence, constant=True)
    secondary_key_sequence = Property(QObject, get_secondary_key_sequence, constant=True)
    released_color = Property(QObject, get_released_color, set_released_color, notify=_changed_released_)
    pressed_color = Property(QObject, get_pressed_color, set_pressed_color, notify=_changed_pressed_)