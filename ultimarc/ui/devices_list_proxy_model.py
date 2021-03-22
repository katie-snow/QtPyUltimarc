#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import Property, Signal, QModelIndex, QObject, QSortFilterProxyModel

from ultimarc.ui.devices_model import DeviceRoles

_logger = logging.getLogger('ultimarc')


class DeviceListSortProxyModel(QSortFilterProxyModel, QObject):
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


class DeviceListProxyModel(QSortFilterProxyModel, QObject):
    _changed_front_page_ = Signal(bool)
    _changed_filter_class_ = Signal(str)
    _changed_filter_text_ = Signal(str)

    _front_page_ = True
    _filter_text_ = ''
    _filter_class_ = 0

    def __init__(self):
        super().__init__()

    def get_front_page(self):
        return self._front_page_

    def set_front_page(self, fp):
        if self._front_page_ != fp:
            self._front_page_ = fp
            self._changed_front_page_.emit(self._front_page_)
            self.invalidateFilter()

    def get_filter_text(self):
        return self._filter_text_

    def set_filter_text(self, new_filter):
        if self._filter_text_ != new_filter:
            self._filter_text_ = new_filter
            self._changed_filter_text_.emit(self._filter_text_)
            self.invalidateFilter()

    def get_filter_class(self):
        return self._filter_class_

    def set_filter_class(self, new_filter):
        if self._filter_class_ != new_filter:
            _logger.debug(f'set_filter_class: {new_filter}')
            self._filter_class_ = new_filter
            self._changed_filter_class_.emit(self._filter_class_)
            self.invalidateFilter()

    front_page = Property(bool, get_front_page, set_front_page, notify=_changed_front_page_)
    filter_class = Property(str, get_filter_class, set_filter_class, notify=_changed_filter_class_)
    filter_text = Property(str, get_filter_text, set_filter_text, notify=_changed_filter_text_)

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        index = self.sourceModel().index(source_row, 0, source_parent)
        if self.front_page:
            connected = index.data(DeviceRoles.CONNECTED)
            return True if connected and source_row < 4 else False
        else:
            if len(self._filter_text_) == 0 and self._filter_class_ == 'all':
                return True
            else:
                name = index.data(DeviceRoles.PRODUCT_NAME)
                dev_class = index.data(DeviceRoles.DEVICE_CLASS)
                dev_class_id = index.data(DeviceRoles.DEVICE_CLASS_ID)
                key = index.data(DeviceRoles.PRODUCT_KEY)

                cb_filter = dev_class_id == self._filter_class_
                return cb_filter and (str(name).find(self._filter_text_) > -1 or
                                      str(dev_class).find(
                                          self._filter_text_) > -1 or
                                      str(key).find(self._filter_text_) > -1)
