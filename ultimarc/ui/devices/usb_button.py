#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing
import re
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QModelIndex, QObject, Property, Signal, QPersistentModelIndex, QSortFilterProxyModel, \
    QAbstractListModel, QMetaEnum

from python_easy_json import JSONObject

from ultimarc.devices import DeviceClassID
from ultimarc.devices.usb_button import USBButtonDevice
from ultimarc.ui.action_model import ActionModel

from ultimarc.ui.devices.device import Device

_logger = logging.getLogger('ultimarc')

KEYCOUNT = 24

class UsbButtonRoles(IntEnum):
    MODE = 1
    RELEASE_COLOR = 4
    PRESSED_COLOR = 5

usbButtonRoleMap = OrderedDict(zip(list(UsbButtonRoles), [k.name.lower() for k in UsbButtonRoles]))

class KeySequenceUI(QAbstractListModel, QObject):
    _change_key_ = Signal(str)
    _change_index_ = Signal(int)

    def __init__(self):
        super().__init__()

        self._config = [0] * KEYCOUNT
        self._index = -1

    class KeySequenceRoles(QMetaEnum):
        TEXTROLE = 1

    def roleNames(self) -> typing.Optional[typing.Dict]:
        roles = {
            self.KeySequenceRoles.TEXTROLE: 'textrole'.encode('utf-8')
        }
        return roles

    def rowCount(self, parent: typing.Union[QModelIndex, QPersistentModelIndex] = ...) -> int:
        return KEYCOUNT

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == self.KeySequenceRoles.TEXTROLE:
            return self._config[index.row()]

    def setData(self, index, value, role = ...):
        if role == self.KeySequenceRoles.TEXTROLE:
            self._config[index.row()] = value
        return True

    def set_key(self, key):
        if self._index != -1:
            self._config[self._index] = key

    def get_key(self):
        if self._index != -1:
            return self._config[self._index]
        else:
            return None

    def set_index(self, index):
        self._index = index

    def get_index(self):
        return self._index

    key = Property(str, get_key, set_key, notify=_change_key_)
    keyIndex = Property(int, get_index, set_index, notify=_change_index_)


class UsbButtonUI(Device):

    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(UsbButtonUI, self).__init__(args, env, attached, device_class_id,
                                          name, device_class_descr, key)

        self.config_color = None
        self.config = None
        self._json_obj = None

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
                                     'deviceClass': self.device_class_id.value}

        self._json_obj = JSONObject(self.config_color)

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

    def rowCount(self, parent: typing.Union[QModelIndex, QPersistentModelIndex] = ...) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:

        return True

    def get_action_model(self):
        return self._action_model

    def get_primary_key_sequence(self):
        return self._primary_key_sequence

    def get_secondary_key_sequence(self):
        return self._secondary_key_sequence

    action_model = Property(QObject, get_action_model, constant=True)
    primary_key_sequence = Property(QObject, get_primary_key_sequence, constant=True)
    secondary_key_sequence = Property(QObject, get_secondary_key_sequence, constant=True)
