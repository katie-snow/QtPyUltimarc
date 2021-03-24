#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
from collections import OrderedDict

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Property

from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolEnvironmentObject

_logger = logging.getLogger('ultimarc')

UNKNOWN_DEVICE = 'Ultimarc Device'


class DeviceRoles(IntEnum):
    DEVICE_CLASS = 1
    PRODUCT_NAME = 2
    PRODUCT_KEY = 3
    CATEGORY = 4
    ICON = 5
    CONNECTED = 6
    DEVICE_CLASS_ID = 7


# Map Role Enum values to class property names.
DeviceRolePropertyMap = OrderedDict(zip(list(DeviceRoles), [k.name.lower() for k in DeviceRoles]))


class UIDeviceInfo:
    """ Class fpr holding additional device data for the UI """
    product_name = ''
    device_class = ''
    device_class_id = None
    product_key = ''
    icon = ''
    connected = True

    def __init__(self, connected=True, device_class='Unknown class', product_name='Unknown Name', product_key=''):
        self.connected = connected
        self.product_name = product_name
        self.device_class = device_class
        self.product_key = product_key

        if len(self.device_class) == 0:
            self.device_class = UNKNOWN_DEVICE

    def setup_icon(self, class_id):
        """ Assign an icon to each device entry
        @param class_id: str
        """
        self.device_class_id = class_id
        # TODO: Add new images
        #   Run to get new resource file: pyside6-rcc assets.qrc  -o rc_assets.py
        if class_id == DeviceClassID.MiniPac.value:
            self.icon = 'qrc:/logos/workstation'
        else:
            self.icon = 'qrc:/logos/placeholder'


class DevicesModel(QAbstractListModel, QObject):
    """ List model that accesses the devices for the view """
    device_count = None
    category = None

    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()

        self.args = args
        self.env = env
        self._device_count = self.env.devices.device_count
        self._category_ = 'Ultimarc Configurations'
        self._ui_dev_info_ = []

        self.setup_info()
        self.device_count = Property(int, self.get_device_count, constant=True)
        self.category = Property(str, self.get_category, constant=True)

    def setup_info(self):
        """ setup up meta data for the devices and configurations """
        for dev in self.get_devices():
            tmp = UIDeviceInfo(product_name=dev.product_name, device_class=dev.class_descr,
                               product_key=dev.dev_key)
            tmp.setup_icon(dev.class_id)
            self._ui_dev_info_.append(tmp)

        # Configuration for non connected devices
        for device_class in DeviceClassID:
            tmp = UIDeviceInfo(False, device_class=device_class.name)
            tmp.setup_icon(device_class.value)
            self._ui_dev_info_.append(tmp)

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter()

    def roleNames(self):
        """ Just return the DeviceRolePropertyMap dict, but convert key values to byte arrays first for QT. """
        # TODO: Add device information to role dict
        roles = OrderedDict()
        for k, v in DeviceRolePropertyMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self._ui_dev_info_)

    def data(self, index: QModelIndex, role):
        if not index.isValid():
            return None

        if role == DeviceRoles.CATEGORY:
            return 'main' if index.row() < self._device_count else self._category_

        for x in range(len(self._ui_dev_info_)):
            if x == index.row():
                dev_cls = self._ui_dev_info_[x]
                return getattr(dev_cls, DeviceRolePropertyMap[role])
        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        # TODO: Implement for writing GUI -> Device
        return False

    def get_category(self):
        return self._category_

    def get_device_count(self):
        return self._device_count if self._device_count < 4 else 4
