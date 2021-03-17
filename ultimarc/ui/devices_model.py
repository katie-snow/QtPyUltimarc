#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import QAbstractListModel, QModelIndex, QMetaEnum, QObject, Property, Signal
from PySide6.QtGui import QPixmap, QIcon

from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolEnvironmentObject

_logger = logging.getLogger('ultimarc')

class UIDeviceInfo():
    """ Class fpr holding additional device data for the UI """
    icon = ''

    def __init__(self):
        pass

class DevicesModel(QAbstractListModel, QObject):
    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()
        self.class_id = ''
        self.args = args
        self.env = env
        self._device_count = self.env.devices.device_count
        self.config_count = len(DeviceClassID)
        self._ui_dev_info = []

        self.setup_info()

        _changed = Signal()
        self._category = ''

    def setup_info(self):
        for dev in self.get_devices():
            tmp = UIDeviceInfo()

            # TODO: Add new images
            if dev.class_id == DeviceClassID.MiniPac.value:
                tmp.icon = 'qrc:/logos/workstation'
            else:
                tmp.icon = 'qrc:/logos/placeholder'
            self._ui_dev_info.append(tmp)

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter()

    class DeviceRoles(QMetaEnum):
        DEVICE_CLASS = 1
        PRODUCT_NAME = 2
        PRODUCT_KEY = 3
        CATEGORY = 4
        ICON = 5

    def roleNames(self):
        # TODO: Add device information to role dict
        _class_descr = 'class_descr'.encode('utf-8')
        _name = 'name'.encode('utf-8')
        _key = 'key'.encode('utf-8')
        _category = 'category'.encode('utf-8')
        _icon = 'icon'.encode('utf-8')
        roles = {
            self.DeviceRoles.DEVICE_CLASS: _class_descr,
            self.DeviceRoles.PRODUCT_NAME: _name,
            self.DeviceRoles.PRODUCT_KEY: _key,
            self.DeviceRoles.CATEGORY: _category,
            self.DeviceRoles.ICON: _icon
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
                    return 'device'
                i = i + 1

            if i in range(i, i + self.config_count):
                return DeviceClassID[self.config_count - i]

        if role == self.DeviceRoles.ICON:
            i = 0
            for dev in self.get_devices():
                if i == index.row():
                    return self._ui_dev_info[i].icon
                i = i + 1

        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        # TODO: Implement for writing GUI -> Device
        return False

    def get_category(self):
        return self._category

    def get_device_count(self):
        return self._device_count

    device_count = Property(int, get_device_count, constant=True)
    category = Property(str, get_category, constant=True)