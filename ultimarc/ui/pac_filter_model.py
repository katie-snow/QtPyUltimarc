#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, QMetaEnum

_logger = logging.getLogger('ultimarc')


class PacFilterModelRoles(IntEnum):
    NAME = 1
    FILTER = 2


# Map Role Enum values to class property names.
MacroModelRoleMap = OrderedDict(zip(list(PacFilterModelRoles), [k.name.lower() for k in PacFilterModelRoles]))


class PacFilterModel(QAbstractListModel, QObject):
    def __init__(self):
        super().__init__()
        self.filter_names = []
        self.filter_values = []

    def set_filter_names(self, pac_names, pac_filters):
        self.beginResetModel()
        self.filter_names = pac_names
        self.filter_values = pac_filters
        self.endResetModel()

    def roleNames(self):
        roles = OrderedDict()
        for k, v in MacroModelRoleMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.filter_names)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == PacFilterModelRoles.NAME:
            return self.filter_names[index.row()]

        if role == PacFilterModelRoles.FILTER:
            return self.filter_values[index.row()]
