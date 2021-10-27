#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex

from ultimarc.ui.device import Device

_logger = logging.getLogger('ultimarc')


class DeviceRoles(IntEnum):
    DEVICE_CLASS_DESCR = 1
    DEVICE_CLASS_NAME = 2
    DEVICE_CLASS_VALUE = 3
    DEVICE_NAME = 4
    DEVICE_KEY = 5
    ICON = 6
    ATTACHED = 7


# Map Role Enum values to class property names.
DeviceRolePropertyMap = OrderedDict(zip(list(DeviceRoles), [k.name.lower() for k in DeviceRoles]))


class DeviceModel(QAbstractListModel, QObject):
    """ This class/model holds the detailed information for the view.
     Other classes will copy their data into this one to display. """

    # Internal member for the currently displayed device
    _device_ = None

    def __init__(self):
        super().__init__()
        self._device_ = Device(False, '')

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
            return 'true' if self._device_.get_attached() else 'false'
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

        return None

    def set_device(self, device):
        self.beginResetModel()
        self._device_ = device
        self.endResetModel()