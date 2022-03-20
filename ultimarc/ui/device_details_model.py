#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex

_logger = logging.getLogger('ultimarc')


class DeviceDetailsModel(QAbstractListModel, QObject):
    """ Model for populating the QML UI with device details """

    def __init__(self):
        super().__init__()
        self._device = None

    def roleNames(self) -> typing.Dict:
        roles = OrderedDict()
        for k, v in self._device.roleNames():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self._device.rowCount() if self._device else 0

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        return self._device.data(index, role)

    def set_device(self, device):
        self.beginResetModel()
        self._device = device
        self.endResetModel()

    def setData(self, index: QModelIndex, value, role: int = ...):
        if not index.isValid():
            return None

        val = self._device.setData(index, value, role)
        self.dataChanged.emit(index, index, [])
        return val
