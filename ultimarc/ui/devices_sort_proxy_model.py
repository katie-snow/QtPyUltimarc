#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import QModelIndex, QObject, QSortFilterProxyModel

from ultimarc.ui.devices_model import DeviceRoles

_logger = logging.getLogger('ultimarc')


class DevicesSortProxyModel(QSortFilterProxyModel, QObject):
    def __init__(self):
        super().__init__()
        self.sort(0)

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        class_left = source_left.data(DeviceRoles.DEVICE_CLASS)
        class_right = source_right.data(DeviceRoles.DEVICE_CLASS)
        connected_left = source_left.data(DeviceRoles.CONNECTED)
        connected_right = source_right.data(DeviceRoles.CONNECTED)
        if connected_right == connected_left:
            return class_left < class_right
        return connected_right < connected_left
