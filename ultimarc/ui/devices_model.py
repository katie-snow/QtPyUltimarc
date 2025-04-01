#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing
from collections import OrderedDict

from enum import IntEnum
from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Property, Signal

from ultimarc.devices import DeviceClassID
from ultimarc.tools import ToolEnvironmentObject
from ultimarc.ui.devices.device import Device
from ultimarc.ui.device_model import DeviceModel
from ultimarc.ui.devices.ipac2 import Ipac2UI
from ultimarc.ui.devices.ipac4 import Ipac4UI
from ultimarc.ui.devices.jpac import JpacUI
from ultimarc.ui.devices.mini_pac import MiniPacUI
from ultimarc.ui.devices.usb_button import UsbButtonUI

_logger = logging.getLogger('ultimarc')

UNKNOWN_DEVICE = 'Ultimarc Device'


class DevicesRoles(IntEnum):
    DEVICE_CLASS_DESCR = 1
    DEVICE_NAME = 3
    ATTACHED = 5
    SELECTED_DEVICE = 6


# Map Role Enum values to class property names.
DevicesRolePropertyMap = OrderedDict(zip(list(DevicesRoles), [k.name.lower() for k in DevicesRoles]))


class DevicesModel(QAbstractListModel, QObject):
    """ List model that accesses the devices for the view """
    _change_selected_device_ = Signal(int)

    def __init__(self, args, env: (ToolEnvironmentObject, None), device_model: DeviceModel):
        super().__init__()

        self.args = args
        self.env = env
        self._devices_ = []
        self._device_model_ = device_model

        self.setup_info()

    def setup_info(self):
        """ setup up metadata for the devices and configurations """
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
            elif dev.class_id == DeviceClassID.USBButton.value:
                device = UsbButtonUI(self.args, self.env, True, DeviceClassID(dev.class_id), dev.product_name,
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
            elif device_class == DeviceClassID.USBButton:
                tmp = UsbButtonUI(self.args, self.env, False, device_class)
            else:
                tmp = Device(self.args, self.env, False, device_class)
            self._devices_.append(tmp)

    def get_devices(self):
        """ Return a list of devices we should show information for. """
        return self.env.devices.filter()

    def roleNames(self):
        """ Return the DevicesRolePropertyMap dict, but convert key values to byte arrays first for QT. """
        # TODO: Add device information to role dict
        roles = OrderedDict()
        for k, v in DevicesRolePropertyMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            return 0
        return len(self._devices_)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        for x in range(len(self._devices_)):
            if x == index.row():
                dev_cls = self._devices_[x]
                return getattr(dev_cls, DevicesRolePropertyMap[role])
        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        if not index.isValid():
            return False

        if role == DevicesRoles.SELECTED_DEVICE:
            self._device_model_.set_device(self._devices_[index.row()])
            return True
        return False

    def get_selected_device(self):
        return self._device_model_

    selected_device = Property(QObject, get_selected_device,  constant=True)
