#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import QModelIndex, QObject, QSortFilterProxyModel

from ultimarc.ui.devices_model import DevicesRoles

_logger = logging.getLogger('ultimarc')


class DevicesSortProxyModel(QSortFilterProxyModel, QObject):
    def __init__(self):
        super().__init__()
        self.sort(0)

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        class_left = source_left.data(DevicesRoles.DEVICE_CLASS_DESCR)
        class_right = source_right.data(DevicesRoles.DEVICE_CLASS_DESCR)
        connected_left = source_left.data(DevicesRoles.ATTACHED)
        connected_right = source_right.data(DevicesRoles.ATTACHED)
        if connected_right == connected_left:
            return class_left < class_right
        return connected_right < connected_left
