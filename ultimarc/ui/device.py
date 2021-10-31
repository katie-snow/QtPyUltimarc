#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing
from enum import Enum

from PySide6.QtCore import QModelIndex

from ultimarc.devices import DeviceClassID

_logger = logging.getLogger('ultimarc')


class Device():
    """ Holds the information for a single device """
    attached = False  # True if hardware is attached
    device_name = 'Unknown Name'  # USB_PRODUCT_DESCRIPTIONS
    device_class_descr = 'Unknown Class'  # USB_PRODUCT_DESCRIPTIONS
    device_class_id = 'Unknown Type'  # DeviceClassId
    device_key = ''  # Key representing the hardware attached
    icon = 'qrc:/logos/placeholder'  # Unknown product icon

    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):

        self.env = env
        self.args = args

        if isinstance(device_class_id, DeviceClassID):
            if attached:
                self.device_name = name
                self.device_class_descr = device_class_descr
                self.device_class_id = device_class_id
            else:
                self.device_name = device_class_id.value
                self.device_class_descr = device_class_id.name
                self.device_class_id = device_class_id
        else:
            self.device_name = 'Unknown Name'
            self.device_class_descr = 'Unknown Class'
            self.device_class_id = 'Unknown Class Id'

        self.device_key = key
        self.attached = attached

    # Implement this function in child classes
    def rowCount(self):
        return 0

    # Implement this function in child classes
    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        return None

    def get_description(self):
        return 'Device class implementation'

    def get_attached(self):
        return self.attached

    def get_device_name(self):
        return self.device_name

    def get_device_class(self):
        return self.device_class_descr

    def get_device_class_id(self):
        return self.device_class_id

    def get_device_key(self):
        return self.device_key

    def get_icon(self):
        return self.icon
