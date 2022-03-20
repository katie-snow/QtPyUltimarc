#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import typing
from PySide6.QtCore import QAbstractListModel, QObject, QMetaEnum, QModelIndex

from ultimarc.devices import DeviceClassID


class DeviceClassModel(QAbstractListModel, QObject):
    def __init__(self):
        super().__init__()

        self.classes = []
        self.classes.append({'name': 'All', 'value': 'all'})
        for name, value in DeviceClassID.__members__.items():
            self.classes.append({'name': name, 'value': value.value})

    class DeviceClassRoles(QMetaEnum):
        DEVICE_CLASS_NAME = 1
        DEVICE_CLASS_VALUE = 2

    def roleNames(self):
        # TODO: Add device information to role dict
        _class_name = 'class_name'.encode('utf-8')
        _class_value = 'class_value'.encode('utf-8')

        roles = {
            self.DeviceClassRoles.DEVICE_CLASS_NAME: _class_name,
            self.DeviceClassRoles.DEVICE_CLASS_VALUE: _class_value
        }
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 0 if parent.isValid() else len(self.classes)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == self.DeviceClassRoles.DEVICE_CLASS_NAME:
            return self.classes[index.row()]['name']

        if role == self.DeviceClassRoles.DEVICE_CLASS_VALUE:
            return self.classes[index.row()]['value']

