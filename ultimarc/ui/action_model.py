#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, QMetaEnum

from ultimarc.devices._mappings import IPACSeriesMapping

_logger = logging.getLogger('ultimarc')


class ActionModel(QAbstractListModel, QObject):
    def __init__(self, legacy=False):
        super().__init__()

        self.legacy = legacy

    class ActionModelRoles(QMetaEnum):
        TEXTROLE = 1

    def roleNames(self):
        roles = {
            self.ActionModelRoles.TEXTROLE: 'textrole'.encode('utf-8')
        }
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(IPACSeriesMapping) if not self.legacy else 0

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == self.ActionModelRoles.TEXTROLE:
            return list(IPACSeriesMapping)[index.row()] if not self.legacy else None
