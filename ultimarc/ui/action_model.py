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
    def __init__(self):
        super().__init__()
        self.macro_names = []

    def set_macro_names(self, macros):
        self.beginResetModel()
        names = []
        for macro in macros:
            names.append(macro['name'])
        self.macro_names = names
        self.endResetModel()

    class ActionModelRoles(QMetaEnum):
        TEXTROLE = 1

    def roleNames(self):
        roles = {
            self.ActionModelRoles.TEXTROLE: 'textrole'.encode('utf-8')
        }
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(IPACSeriesMapping) + len(self.macro_names)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == self.ActionModelRoles.TEXTROLE:
            map_list = list(IPACSeriesMapping)
            if index.row() >= len(map_list):
                return self.macro_names[index.row() - len(map_list)]
            else:
                return map_list[index.row()]
