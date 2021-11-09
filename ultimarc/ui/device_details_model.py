#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex

_logger = logging.getLogger('ultimarc')


class DeviceDataRoles(IntEnum):
    NAME = 1
    ACTION = 2
    ALT_ACTION = 3
    SHIFT = 4


# Map Role Enum values to class property names.
DeviceDataRolePropertyMap = OrderedDict(zip(list(DeviceDataRoles), [k.name.lower() for k in DeviceDataRoles]))


class DeviceDataModel(QAbstractListModel, QObject):
    """ Model for populating the QML Repeater in the UI """

    def __init__(self):
        super().__init__()
        self.device = None

    def roleNames(self) -> typing.Dict:
        roles = OrderedDict()
        for k, v in DeviceDataRolePropertyMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self.device.rowCount() if self.device else 0

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        return self.device.data(index, role)

    def set_device(self, device):
        self.beginResetModel()
        self.device = device
        self.endResetModel()

    def setData(self, index: QModelIndex, value, role: int = ...):
        if not index.isValid():
            return None

        val = self.device.setData(index, value, role)
        self.dataChanged.emit(index, index, [])
        return val