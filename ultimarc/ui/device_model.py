#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, Property

from ultimarc.tools import ToolEnvironmentObject
from ultimarc.ui.devices.device import Device
from ultimarc.ui.device_details_model import DeviceDetailsModel

_logger = logging.getLogger('ultimarc')


class DeviceRoles(IntEnum):
    DEVICE_CLASS_DESCR = 1
    DEVICE_CLASS_NAME = 2
    DEVICE_CLASS_VALUE = 3
    DEVICE_NAME = 4
    DEVICE_KEY = 5
    ICON = 6
    ATTACHED = 7
    DESCRIPTION = 8
    QML = 9
    WRITE_DEVICE = 10
    SAVE_LOCATION = 11
    LOAD_LOCATION = 12
    # TODO: Create role to return result of writes and loads


# Map Role Enum values to class property names.
DeviceRolePropertyMap = OrderedDict(zip(list(DeviceRoles), [k.name.lower() for k in DeviceRoles]))


class DeviceModel(QAbstractListModel, QObject):
    """ This class/model holds the detailed information for the view.
     Other classes will copy their data into this one to display. """

    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()
        self._device_ = Device(args, env, False, '')
        self._details_model_ = DeviceDetailsModel()

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
        if role == DeviceRoles.ICON:
            return self._device_.get_icon()
        if role == DeviceRoles.DESCRIPTION:
            return self._device_.get_description()
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
        self._details_model_.set_device(device)
        self.beginResetModel()
        self._device_ = device
        self.endResetModel()

    def get_details_model(self):
        return self._details_model_

    details_model = Property(QObject, get_details_model, constant=True
                             )
