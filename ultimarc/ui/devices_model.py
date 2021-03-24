#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging

from PySide6.QtCore import QAbstractListModel, QModelIndex, QMetaEnum, QObject, Property

from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolEnvironmentObject

_logger = logging.getLogger('ultimarc')

UNKNOWN_DEVICE = 'Ultimarc Device'


class DeviceRoles(QMetaEnum):
    DEVICE_CLASS = 1
    PRODUCT_NAME = 2
    PRODUCT_KEY = 3
    CATEGORY = 4
    ICON = 5
    CONNECTED = 6
    DEVICE_CLASS_ID = 7


class UIDeviceInfo:
    """ Class fpr holding additional device data for the UI """
    name = ''
    class_descr = ''
    class_id = None
    key = ''
    icon = ''
    connected = True

    def __init__(self, connected=True, class_descr='Unknown class', name='Unknown Name', key=''):
        self.connected = connected
        self.name = name
        self.class_descr = class_descr
        self.key = key

        if len(self.class_descr) == 0:
            self.class_descr = UNKNOWN_DEVICE

    def setup_icon(self, class_id):
        """ Assign an icon to each device entry
        @param class_id: str
        """
        self.class_id = class_id
        # TODO: Add new images
        #   Run to get new resource file: pyside6-rcc assets.qrc  -o rc_assets.py
        if class_id == DeviceClassID.MiniPac.value:
            self.icon = 'qrc:/logos/workstation'
        else:
            self.icon = 'qrc:/logos/placeholder'


class DevicesModel(QAbstractListModel, QObject):
    """ List model that accesses the devices for the view """
    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()

        self.args = args
        self.env = env
        self._device_count = self.env.devices.device_count
        self._category_ = 'Ultimarc Configurations'
        self._ui_dev_info_ = []

        self.setup_info()

    def setup_info(self):
        """ setup up meta data for the devices and configurations """
        for dev in self.get_devices():
            tmp = UIDeviceInfo(name=dev.product_name, class_descr=dev.class_descr,
                               key=dev.dev_key)
            tmp.setup_icon(dev.class_id)
            self._ui_dev_info_.append(tmp)

        # Configuration for non connected devices
        for device_class in DeviceClassID:
            tmp = UIDeviceInfo(False, class_descr=device_class.name)
            tmp.setup_icon(device_class.value)
            self._ui_dev_info_.append(tmp)

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter()

    def roleNames(self):
        # TODO: Add device information to role dict
        class_descr = 'class_descr'.encode('utf-8')
        class_id = 'class_id'.encode('utf-8')
        name = 'name'.encode('utf-8')
        key = 'key'.encode('utf-8')
        category = 'category'.encode('utf-8')
        icon = 'icon'.encode('utf-8')
        connected = 'connected'.encode('utf-8')
        roles = {
            DeviceRoles.DEVICE_CLASS: class_descr,
            DeviceRoles.DEVICE_CLASS_ID: class_id,
            DeviceRoles.PRODUCT_NAME: name,
            DeviceRoles.PRODUCT_KEY: key,
            DeviceRoles.CATEGORY: category,
            DeviceRoles.ICON: icon,
            DeviceRoles.CONNECTED: connected
        }

        return roles

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self._ui_dev_info_)

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None

        if role == DeviceRoles.DEVICE_CLASS:
            i = 0
            for ui_dev in self._ui_dev_info_:
                if i == index.row():
                    return ui_dev.class_descr
                i = i + 1

        if role == DeviceRoles.DEVICE_CLASS_ID:
            i = 0
            for ui_dev in self._ui_dev_info_:
                if i == index.row():
                    return ui_dev.class_id
                i = i + 1

        if role == DeviceRoles.PRODUCT_NAME:
            i = 0
            for ui_dev in self._ui_dev_info_:
                if i == index.row():
                    return ui_dev.name
                i = i + 1

        if role == DeviceRoles.PRODUCT_KEY:
            i = 0
            for ui_dev in self._ui_dev_info_:
                if i == index.row():
                    return ui_dev.key
                i = i + 1

        if role == DeviceRoles.CATEGORY:
            return 'main' if index.row() < self._device_count else self._category_

        if role == DeviceRoles.ICON:
            i = 0
            for ui_dev in self._ui_dev_info_:
                if i == index.row():
                    return ui_dev.icon
                i = i + 1

        if role == DeviceRoles.CONNECTED:
            i = 0
            for ui_dev in self._ui_dev_info_:
                if i == index.row():
                    return ui_dev.connected
                i = i + 1

        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        # TODO: Implement for writing GUI -> Device
        return False

    def get_category(self):
        return self._category_

    def get_device_count(self):
        return self._device_count if self._device_count < 4 else 4

    device_count = Property(int, get_device_count, constant=True)
    category = Property(str, get_category, constant=True)
