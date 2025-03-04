#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, Property, Signal

from ultimarc.tools import ToolEnvironmentObject
from ultimarc.ui.devices.device import Device

_logger = logging.getLogger('ultimarc')


class DeviceRoles(IntEnum):
    DEVICE_CLASS_DESCR = 1
    DEVICE_CLASS_NAME = 2
    DEVICE_CLASS_VALUE = 3
    DEVICE_NAME = 4
    DEVICE_KEY = 5
    ATTACHED = 6
    QML = 7
    WRITE_DEVICE = 8
    SAVE_LOCATION = 9
    LOAD_LOCATION = 10
    # TODO: Create role to return result of writes and loads


# Map Role Enum values to class property names.
DeviceRolePropertyMap = OrderedDict(zip(list(DeviceRoles), [k.name.lower() for k in DeviceRoles]))


class DeviceModel(QAbstractListModel, QObject):
    """ This class/model holds the detailed information for the view.
     Other classes will copy their data into this one to display. """

    _device_ = Signal(int)

    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()
        self._device_ = Device(args, env, False, '')

    def roleNames(self) -> typing.Dict:
        roles = OrderedDict()
        for k, v in DeviceRolePropertyMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == DeviceRoles.DEVICE_CLASS_DESCR:
            return self._device_.get_device_class()
        if role == DeviceRoles.ATTACHED:
            return self._device_.get_attached()
        if role == DeviceRoles.DEVICE_NAME:
            return self._device_.get_device_name()
        if role == DeviceRoles.DEVICE_CLASS_NAME:
            return self._device_.get_device_class_id()
        if role == DeviceRoles.DEVICE_CLASS_VALUE:
            return self._device_.get_device_class_id().value
        if role == DeviceRoles.DEVICE_KEY:
            return self._device_.get_device_key()
        if role == DeviceRoles.QML:
            return self._device_.get_qml()
        if role == DeviceRoles.WRITE_DEVICE:
            return self._device_.write_device()
        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return False

        if role == DeviceRoles.SAVE_LOCATION:
            ret = self._device_.write_file(value)
            self.dataChanged.emit(index, index, [])
            return ret
        if role == DeviceRoles.LOAD_LOCATION:
            # do the model reset since we are changing all the config data
            self.beginResetModel()
            ret = self._device_.load_file(value)
            self.endResetModel()
            return ret
        return False

    def set_device(self, device):
        self.beginResetModel()
        self._device_ = device
        self.endResetModel()

    def get_device(self):
        return self._device_

    device = Property(QObject, get_device, constant=True)
