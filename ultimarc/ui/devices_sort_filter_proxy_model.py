#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import re
from operator import index

from PySide6.QtCore import QModelIndex, QObject, QSortFilterProxyModel, Signal, Property

from ultimarc.ui.devices_model import DevicesRoles

_logger = logging.getLogger('ultimarc')


class DevicesSortProxyModel(QSortFilterProxyModel, QObject):

    _selected_device_ = Signal(int)

    def __init__(self):
        super().__init__()
        self.sort(0)

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        class_left = source_left.data(DevicesRoles.DEVICE_CLASS_DESCR)
        class_right = source_right.data(DevicesRoles.DEVICE_CLASS_DESCR)
        connected_left = source_left.data(DevicesRoles.ATTACHED)
        connected_right = source_right.data(DevicesRoles.ATTACHED)

        # Empty devices, then connected devices
        if connected_right == connected_left:
            return class_left > class_right
        return connected_right > connected_left

    def set_selected_device(self, QModelIndex):
        # self._details_model_.set_device(device)
        self.beginResetModel()
        self._device_ = device
        self._device_.set_details_model(self._details_model_)
        self.endResetModel()

    def get_details_model(self):

        return self._device_.get_details_model()


    selected_device_model = Property(QObject, get_details_model, constant=True)


class DevicesFilterProxyModel(QSortFilterProxyModel, QObject):
    _filter_str_signal_ = Signal(str)
    filter_str = 'IPAC2'

    def __init__(self):
        super().__init__()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        name = index.data(DevicesRoles.DEVICE_NAME)
        return True if re.search(self.filter_str, name, re.IGNORECASE) else False

    def get_filter(self):
        return self.filter_str

    def set_filter(self, new_filter):
        self.filter_str = new_filter
        self.invalidateFilter()

    text = Property(str, get_filter, set_filter, notify=_filter_str_signal_)
