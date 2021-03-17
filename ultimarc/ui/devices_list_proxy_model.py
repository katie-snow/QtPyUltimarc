#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import Property, Signal, QIdentityProxyModel, QModelIndex, QObject

_logger = logging.getLogger('ultimarc')


class DeviceListProxyModel(QIdentityProxyModel, QObject):

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

    def get_filter_text(self):
        return self._filter_text

    def set_filter_text(self, filter):
        if self._filter_text != filter:
            self._filter_text = filter
            self._changed_filter_text.emit(self._filter_text)

    front_page = Property(bool, get_front_page, set_front_page, notify=_changed_front_page)
    filter_text = Property(str, get_filter_text, set_filter_text, notify=_changed_filter_text)

    def data(self, proxyIndex, role):
        value = QIdentityProxyModel.data(proxyIndex, role)
        return value
