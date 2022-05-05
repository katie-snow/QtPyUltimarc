#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing
from collections import OrderedDict

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Property

from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolEnvironmentObject
from ultimarc.ui.devices.device import Device
from ultimarc.ui.device_model import DeviceModel
from ultimarc.ui.devices.ipac2 import Ipac2UI
from ultimarc.ui.devices.ipac4 import Ipac4UI
from ultimarc.ui.devices.jpac import JpacUI
from ultimarc.ui.devices.mini_pac import MiniPacUI

_logger = logging.getLogger('ultimarc')

UNKNOWN_DEVICE = 'Ultimarc Device'


class DevicesRoles(IntEnum):
    DEVICE_CLASS_DESCR = 1
    DEVICE_CLASS_ID = 2
    DEVICE_NAME = 3
    DEVICE_KEY = 4
    CATEGORY = 5
    ICON = 6
    ATTACHED = 7
    SELECTED_DEVICE = 8
    DEVICE = 9
    DESCRIPTION = 10


# Map Role Enum values to class property names.
DeviceRolePropertyMap = OrderedDict(zip(list(DevicesRoles), [k.name.lower() for k in DevicesRoles]))


class DevicesModel(QAbstractListModel, QObject):
    """ List model that accesses the devices for the view """

    def __init__(self, args, env: (ToolEnvironmentObject, None)):
        super().__init__()

        self.args = args
        self.env = env
        self._device_count_ = self.env.devices.device_count
        self._category_ = 'Ultimarc Configurations'
        self._devices_ = []
        self._device_model_ = DeviceModel(args, env)
        self._selected_device_ = None
        self.selected_row = -1

        self.setup_info()

    def setup_info(self):
        """ setup up meta data for the devices and configurations """
        for dev in self.get_devices():
            if dev.class_id == DeviceClassID.MiniPac.value:
                device = MiniPacUI(self.args, self.env, True, DeviceClassID(dev.class_id), dev.product_name,
                                   dev.class_descr, dev.dev_key)
            elif dev.class_id == DeviceClassID.IPAC2.value:
                device = Ipac2UI(self.args, self.env, True, DeviceClassID(dev.class_id), dev.product_name,
                                 dev.class_descr, dev.dev_key)
            elif dev.class_id == DeviceClassID.IPAC4.value:
                device = Ipac4UI(self.args, self.env, True, DeviceClassID(dev.class_id), dev.product_name,
                                 dev.class_descr, dev.dev_key)
            elif dev.class_id == DeviceClassID.JPAC.value:
                device = JpacUI(self.args, self.env, True, DeviceClassID(dev.class_id), dev.product_name,
                                dev.class_descr, dev.dev_key)
            else:
                device = Device(self.args, self.env, True, DeviceClassID(dev.class_id), dev.product_name,
                                dev.class_descr, dev.dev_key)
            self._devices_.append(device)

        # Configuration for non connected devices
        for device_class in DeviceClassID:
            if device_class == DeviceClassID.MiniPac:
                tmp = MiniPacUI(self.args, self.env, False, device_class)
            elif device_class == DeviceClassID.IPAC2:
                tmp = Ipac2UI(self.args, self.env, False, device_class)
            elif device_class == DeviceClassID.IPAC4:
                tmp = Ipac4UI(self.args, self.env, False, device_class)
            elif device_class == DeviceClassID.JPAC:
                tmp = JpacUI(self.args, self.env, False, device_class)
            else:
                tmp = Device(self.args, self.env, False, device_class)
            self._devices_.append(tmp)

    def has_connected_devices(self):
        return True if self._device_count_ > 0 else False

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter()

    def roleNames(self):
        """ Return the DeviceRolePropertyMap dict, but convert key values to byte arrays first for QT. """
        # TODO: Add device information to role dict
        roles = OrderedDict()
        for k, v in DeviceRolePropertyMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            return 0
        return len(self._devices_)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == DevicesRoles.CATEGORY:
            return 'main' if index.row() < self._device_count_ else self._category_

        if role == DevicesRoles.DEVICE:
            return self._device_model_

        for x in range(len(self._devices_)):
            if x == index.row():
                dev_cls = self._devices_[x]
                return getattr(dev_cls, DeviceRolePropertyMap[role])
        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        if not index.isValid():
            return False

        if role == DevicesRoles.SELECTED_DEVICE:
            self.selected_row = index.row()
            self._selected_device_ = self._devices_[index.row()]
            self._device_model_.set_device(self._devices_[index.row()])
            return True
        return False

    def get_category(self):
        return self._category_

    def get_device_count(self):
        return self._device_count_ if self._device_count_ < 4 else 4

    def get_device_model(self):
        return self._device_model_

    def get_device(self):
        return self._selected_device_

    device = Property(QObject, get_device, constant=True)
    device_model = Property(QObject, get_device_model, constant=True)
    count = Property(int, get_device_count, constant=True)
    category = Property(str, get_category, constant=True)
