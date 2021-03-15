#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import QAbstractListModel, QModelIndex, QMetaEnum, QObject

from ultimarc.tools import ToolEnvironmentObject

_logger = logging.getLogger('ultimarc')


class DevicesModel(QAbstractListModel, QObject):
    class_id = ''

    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()

        self.args = args
        self.env = env

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter()

    class DeviceRoles(QMetaEnum):
        DEVICE_CLASS = 1
        PRODUCT_NAME = 2
        PRODUCT_KEY = 3
        CATEGORY = 4

    def roleNames(self):
        # TODO: Add device information to role dict
        _class_descr = 'class_descr'.encode('utf-8')
        _name = 'name'.encode('utf-8')
        _key = 'key'.encode('utf-8')
        _category = 'category'.encode('utf-8')
        roles = {
            self.DeviceRoles.DEVICE_CLASS: _class_descr,
            self.DeviceRoles.PRODUCT_NAME: _name,
            self.DeviceRoles.PRODUCT_KEY: _key,
            self.DeviceRoles.CATEGORY: _category
        }

        return roles

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self.env.devices.device_count

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None

        if role == self.DeviceRoles.DEVICE_CLASS:
            i = 0
            for dev in self.get_devices():
                if i == index.row():
                    return dev.class_descr
                i = i + 1

        if role == self.DeviceRoles.PRODUCT_NAME:
            i = 0
            for dev in self.get_devices():
                if i == index.row():
                    return dev.product_name
                i = i + 1

        if role == self.DeviceRoles.PRODUCT_KEY:
            i = 0
            for dev in self.get_devices():
                if i == index.row():
                    return dev.dev_key
                i = i + 1

        if role == self.DeviceRoles.CATEGORY:
            i = 0
            for dev in self.get_devices():
                if i == index.row():
                    return None
                i = i + 1

        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        # TODO: Implement for writing GUI -> Device
        return False
