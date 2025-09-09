#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import logging
import typing

from collections import OrderedDict
from enum import IntEnum

from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, QMetaEnum
from PySide6.QtCore import  Property, Signal

from python_easy_json import JSONObject

from ultimarc.devices import DeviceClassID
from ultimarc.devices.usb_button import USBButtonDevice
from ultimarc.ui.action_model import ActionModel

from ultimarc.ui.devices.device import Device

_logger = logging.getLogger('ultimarc')

KEYCOUNT = 24

class UsbButtonRoles(IntEnum):
    MODE = 1
    RELEASE_COLOR = 4
    PRESSED_COLOR = 5

usbButtonRoleMap = OrderedDict(zip(list(UsbButtonRoles), [k.name.lower() for k in UsbButtonRoles]))


class KeySequenceUI(QAbstractListModel, QObject):
    #_change_key_ = Signal(str)
    #_change_index_ = Signal(int)

    def __init__(self):
        super().__init__()
        self._config = [''] * KEYCOUNT

    class SequenceRoles(QMetaEnum):
        ACTION = 1

    def roleNames(self) -> typing.Optional[typing.Dict]:
        roles = {
            self.SequenceRoles.ACTION: 'action'.encode('utf-8')
        }
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return KEYCOUNT

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        # _logger.debug(f'role={role} index={index.row()}')

        if role == self.SequenceRoles.ACTION:
            # _logger.debug(f'action={self._config[index.row()]}')
            return self._config[index.row()]

        _logger.debug(f'action_model=None')
        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        if role == self.SequenceRoles.ACTION:
            self._config[index.row()] = value

        return True

    def get_config(self):
        return self._config


class UsbButtonUI(Device):
    _changed_released_ = Signal()  # notify QML when released_color changes
    _changed_pressed_ = Signal()   # notify QML when pressed_color changes
    _changed_action_ = Signal(str)

    def __init__(self, args, env, attached,
                 device_class_id,
                 name=None, device_class_descr=None,
                 key=''):
        super(UsbButtonUI, self).__init__(args, env, attached, device_class_id,
                                          name, device_class_descr, key)

        self.config_color = None
        self.config_keys = None
        self._json_color = None
        self._json_keys = None
        self._action = 'extended'

        self._action_model = ActionModel()

        self._primary_key_sequence = KeySequenceUI()
        self._secondary_key_sequence = KeySequenceUI()

        # Internal color state (0..255 ints)
        self._released_color = {'red': 255, 'green': 255, 'blue': 255}
        self._pressed_color = {'red': 255, 'green': 255, 'blue': 255}

    def get_qml(self):
        self.populate()
        return 'UsbButtonDetail.qml'

    def populate(self):
        if self.config_color is None:
            if self.attached:
                devices = [dev for dev in
                           self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                                   address=self.args.address)]
                for dev in devices:
                    with dev as dev_h:
                        self.config_color = dev_h.to_json_str(dev_h.get_color())
            else:
                self.config_color = {'schemaVersion': 2.0, 'resourceType': 'usb-button-color',
                                     'deviceClass': self.device_class_id.value,
                                     'colorRGB': {'red': 1, 'green': 1, 'blue': 1}}

                self.config_keys = {}
                # self.config_keys = {'schemaVersion': 2.0, 'resourceType': 'usb-button-color',
                #                      'deviceClass': self.device_class_id.value, 'action': 'extended',
                #                     'pressedColor': {'red': 255, 'green': 255, 'blue': 255},
                #                     'releasedColor': {'red': 255, 'green': 255, 'blue': 255},
                #                     'keys': {{'sequence': 'primary', 'row1': [], 'row2': [], 'row3': [], 'row4': []},
                #                     {'sequence': 'secondary', 'row1': [], 'row2': [], 'row3': [], 'row4': []}}}

        self._json_color = JSONObject(self.config_color)
        self._json_keys = JSONObject(self.config_keys)

    def write_device(self):
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                           address=self.args.address)]
        for dev in devices:
            with dev as dev_h:
                return dev_h.set_config_ui(self.config)

    def roleNames(self) -> typing.Optional[typing.Dict]:
        roles = OrderedDict()
        for k, v in usbButtonRoleMap.items():
            roles[k] = v.encode('utf-8')
        return roles

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        return True

    def get_action_model(self):
        return self._action_model

    def get_primary_key_sequence(self):
        return self._primary_key_sequence

    def get_secondary_key_sequence(self):
        return self._secondary_key_sequence

    def _validate_color(self, color):
        """Return a sanitized dict with red, green, blue ints in [0,255].
        Accepts various inputs from QML/PySide (dict/QVariantMap, objects with attributes, or indexable mappings).
        """
        if color is None:
            return None

        def extract(component):
            # Try dict-like access first
            if isinstance(color, dict):
                return color.get(component)
            # Try mapping-style access via []
            try:
                return color[component]
            except Exception:
                pass
            # Try attribute access (e.g., QObject/JS object proxy)
            try:
                return getattr(color, component)
            except Exception:
                pass
            # Some QML bindings may pass objects with .toVariant() returning a dict
            try:
                to_variant = getattr(color, 'toVariant', None)
                if callable(to_variant):
                    v = to_variant()
                    if isinstance(v, dict):
                        return v.get(component)
            except Exception:
                pass
            return None

        def to_int(v):
            try:
                iv = int(round(float(v)))
            except Exception:
                return None
            return max(0, min(255, iv))

        r = to_int(extract('red'))
        g = to_int(extract('green'))
        b = to_int(extract('blue'))
        if r is None or g is None or b is None:
            return None
        return {'red': r, 'green': g, 'blue': b}

    def get_released_color(self):
        return dict(self._released_color)

    def set_released_color(self, color):
        new_color = self._validate_color(color)
        if new_color is None:
            _logger.debug(f'Invalid released_color received: {color}')
            return
        if new_color == self._released_color:
            return
        self._released_color = new_color
        try:
            self._changed_released_.emit()
        except Exception as e:
            _logger.debug(f'emit released_color changed failed: {e}')

    def get_pressed_color(self):
        return dict(self._pressed_color)

    def set_pressed_color(self, color):
        new_color = self._validate_color(color)
        if new_color is None:
            _logger.debug(f'Invalid pressed_color received: {color}')
            return
        if new_color == self._pressed_color:
            return
        self._pressed_color = new_color
        try:
            self._changed_pressed_.emit()
        except Exception as e:
            _logger.debug(f'emit pressed_color changed failed: {e}')

    # Action for how the button will behave when pressed
    # Extended: Send both sequences on every press
    # Alternate: Send primary then secondary on alternate press
    # Both: Send primary on short press, Secondary on long press
    def get_action(self):
        return self._action

    def set_action(self, action):
        if self._action == action:
            return
        self._action = action
        #_logger.debug(f'action={self._action}')
        try:
            self._changed_action_.emit(self._action)
        except Exception as e:
            _logger.debug(f'emit action changed failed: {e}')

    # action_model is for the grid combo boxes that contain key presses
    action_model = Property(QObject, get_action_model, constant=True)
    primary_key_sequence = Property(QObject, get_primary_key_sequence, constant=True)
    secondary_key_sequence = Property(QObject, get_secondary_key_sequence, constant=True)
    released_color = Property('QVariant', get_released_color, set_released_color, notify=_changed_released_)
    pressed_color = Property('QVariant', get_pressed_color, set_pressed_color, notify=_changed_pressed_)
    # action is the three options for usb-button (extended, both, alternate)
    action = Property(str, get_action, set_action, notify=_changed_action_)