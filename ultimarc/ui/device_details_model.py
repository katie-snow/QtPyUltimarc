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

        if role == DeviceDataRoles.NAME:
            return self.device.data(index, role)

    def set_device(self, device):
        _logger.debug('Resetting the Device Data Model')
        self.beginResetModel()
        self.device = device
        self.endResetModel()
