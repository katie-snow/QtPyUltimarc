#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from PySide6.QtCore import QAbstractListModel, QObject, QMetaEnum, QModelIndex

from ultimarc.devices import DeviceClassID


class DeviceClassModel(QAbstractListModel, QObject):
    def __init__(self):
        super().__init__()

        self.classes = []
        self.classes.append('All')
        for name, value in DeviceClassID.__members__.items():
            self.classes.append(value.value)

    class DeviceClassRoles(QMetaEnum):
        DEVICE_CLASS = 1

    def roleNames(self):
        # TODO: Add device information to role dict
        _class_descr = 'class_descr'.encode('utf-8')
        roles = {
            self.DeviceClassRoles.DEVICE_CLASS: _class_descr
        }
        return roles

    def rowCount(self, parent: QModelIndex):
        return 0 if parent.isValid() else len(self.classes)

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None

        if role == self.DeviceClassRoles.DEVICE_CLASS:
            return self.classes[index.row()]
