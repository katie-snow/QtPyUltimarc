#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import Property, Signal, QModelIndex, QObject, QSortFilterProxyModel

from ultimarc.ui.devices_model import DeviceRoles, UNKNOWN_DEVICE

_logger = logging.getLogger('ultimarc')


class DeviceListProxyModel(QSortFilterProxyModel, QObject):

    _changed_front_page = Signal(bool)
    _changed_filter_text = Signal(str)

    _front_page = True
    _filter_text = ''

    def __init__(self):
        super().__init__()

    def get_front_page(self):
        return self._front_page

    def set_front_page(self, fp):
        if self._front_page != fp:
            _logger.debug('set_front_page called. {fp}')
            self._front_page = fp
            self._changed_front_page.emit(self._front_page)
            self.invalidateFilter()

    def get_filter_text(self):
        return self._filter_text

    def set_filter_text(self, filter):
        if self._filter_text != filter:
            self._filter_text = filter
            self._changed_filter_text.emit(self._filter_text)

    front_page = Property(bool, get_front_page, set_front_page, notify=_changed_front_page)
    filter_text = Property(str, get_filter_text, set_filter_text, notify=_changed_filter_text)

    # TODO: Create sort
    # def lessThan(self, source_left:QModelIndex, source_right:QModelIndex) -> bool:
    #     connected_left = source_left.data(DeviceRoles.CONNECTED)
    #     connected_right = source_right.data(DeviceRoles.CONNECTED)
    #     if connected_right is True and connected_left is True:
    #         device_class = index.data(DeviceRoles.DEVICE_CLASS)
    #         if device_class == UNKNOWN_DEVICE:
    #             return False
    #     else:

    def filterAcceptsRow(self, source_row, source_parent:QModelIndex):
        if self.front_page:
            index = self.sourceModel().index(source_row, 0, source_parent)
            connected = index.data(DeviceRoles.CONNECTED)
            if connected:
                _logger.debug(source_row)
                return True if source_row < 4 else False
            else:
                return False
        else:
            return True
