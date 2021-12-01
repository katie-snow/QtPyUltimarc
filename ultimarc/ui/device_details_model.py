#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, Signal, Property

_logger = logging.getLogger('ultimarc')


class DeviceDataModel(QAbstractListModel, QObject):
    """ Model for populating the QML Repeater in the UI """
    _changed_debounce_ = Signal(str)

    def __init__(self):
        super().__init__()
        self.device = None

    def roleNames(self) -> typing.Dict:
        roles = OrderedDict()
        for k, v in self.device.roleNames():
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

    def get_debounce(self):
        return self.device.get_debounce() if self.device is not None else None

    def set_debounce(self, debounce):
        if self.device:
            self.device.set_debounce(debounce)
            self._changed_debounce_.emit(debounce)

    debounce = Property(str, get_debounce, set_debounce, notify=_changed_debounce_)
