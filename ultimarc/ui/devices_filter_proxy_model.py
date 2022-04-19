#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import re

from PySide6.QtCore import Property, Signal, QModelIndex, QObject, QSortFilterProxyModel

from ultimarc.ui.devices_model import DevicesRoles
from ultimarc.ui.pages import Pages

_logger = logging.getLogger('ultimarc')


class ClassFilterProxyModel(QSortFilterProxyModel, QObject):
    _changed_filter_class_ = Signal(str)

    _filter_class_ = 'all'

    def __init__(self, _pages):
        super().__init__()

        assert isinstance(_pages, Pages)
        self.pages = _pages

    def get_filter_class(self):
        return self._filter_class_

    def set_filter_class(self, new_filter):
        if self._filter_class_ != new_filter:
            # _logger.debug(f'class filter: set_filter_class {new_filter}')
            self._filter_class_ = new_filter
            self._changed_filter_class_.emit(self._filter_class_)
            self.invalidateFilter()

    filter = Property(str, get_filter_class, set_filter_class, notify=_changed_filter_class_)

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        index = self.sourceModel().index(source_row, 0, source_parent)
        if self.pages.get_front():
            return True
        else:
            if self._filter_class_ == 'all':
                return True
            else:
                device_class_id = index.data(DevicesRoles.DEVICE_CLASS_ID)
                cb_filter = device_class_id.value == self._filter_class_
                # _logger.debug(f'cb_filter {device_class_id}, {self._filter_class_}: {cb_filter}')
                return cb_filter


# noinspection PyUnresolvedReferences
class DevicesFilterProxyModel(QSortFilterProxyModel, QObject):
    _changed_filter_text_ = Signal(str)

    _filter_text_ = ''

    def __init__(self, _pages):
        super().__init__()

        assert isinstance(_pages, Pages)
        self.pages = _pages

    def custom_invalidate_filter(self):
        self.invalidateFilter()
        return None

    def get_filter_text(self):
        return self._filter_text_

    def set_filter_text(self, new_filter):
        if self._filter_text_ != new_filter:
            self._filter_text_ = new_filter
            self._changed_filter_text_.emit(self._filter_text_)
            self.invalidateFilter()

    invalidate_filter = Property(int, custom_invalidate_filter, constant=True)
    filter_text = Property(str, get_filter_text, set_filter_text, notify=_changed_filter_text_)

    def filterAcceptsRow(self, source_row, source_parent: QModelIndex):
        index = self.sourceModel().index(source_row, 0, source_parent)
        if self.pages.get_front():
            connected = index.data(DevicesRoles.ATTACHED)
            return True if connected and source_row < 4 else False
        else:
            if len(self._filter_text_) == 0:
                return True
            else:
                product_name = index.data(DevicesRoles.DEVICE_NAME)
                device_class = index.data(DevicesRoles.DEVICE_CLASS_DESCR)
                product_key = index.data(DevicesRoles.DEVICE_KEY)

                re_name = re.search(self._filter_text_, product_name, re.IGNORECASE) is not None
                re_class = re.search(self._filter_text_, device_class, re.IGNORECASE) is not None
                re_key = re.search(self._filter_text_, product_key, re.IGNORECASE) is not None
                re_filter = re_name or re_class or re_key
                # _logger.debug(f're filter ({device_class}: {re_filter}')
                return re_filter
