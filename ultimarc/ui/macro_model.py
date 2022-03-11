#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import logging
import typing
from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex

_logger = logging.getLogger('ultimarc')


class MacroModelRoles(IntEnum):
    NAME = 1
    ACTION = 2


# Map Role Enum values to class property names.
MacroModelRoleMap = OrderedDict(zip(list(MacroModelRoles), [k.name.lower() for k in MacroModelRoles]))


class MacroModel(QAbstractListModel, QObject):
    def __init__(self):
        super().__init__()
        self._macros_ = []

    def set_macros(self, macros):
        self._macros_ = macros

    def roleNames(self):
        roles = OrderedDict()
        for k, v in MacroModelRoleMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._macros_)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == MacroModelRoles.NAME:
            return self._macros_[index.row()]['name']

        if role == MacroModelRoles.ACTION:
            return ', '.join(self._macros_[index.row()]['action'])

    def setData(self, index:QModelIndex, value:typing.Any, role:int=...) -> bool:
        if not index.isValid():
            return False

        if role == MacroModelRoles.NAME:
            self._macros_[index.row()]['name'] = value

        if role == MacroModelRoles.ACTION:
            actions = [action.strip() for action in list(value.split(','))]
            self._macros_[index.row()]['action'] = actions

        self.dataChanged.emit(index, index, [])
        return True
