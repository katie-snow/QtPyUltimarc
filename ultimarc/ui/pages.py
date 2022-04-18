#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging

from PySide6.QtCore import QObject, Signal, Property

_logger = logging.getLogger('ultimarc')


class Pages(QObject):
    _changed_front_ = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self._front_ = True

    def get_front(self):
        return self._front_

    def set_front(self, new_front):
        if self._front_ != new_front:
            self._front_ = new_front
            self._changed_front_.emit(self._front_)

    front_page = Property(bool, get_front, set_front, notify=_changed_front_)
