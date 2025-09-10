#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
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
    ### Holds the model data for the USB Button key sequence for the Primary and Secondary actions ###

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

        if role == self.SequenceRoles.ACTION:
            return self._config[index.row()]

        return None

    def setData(self, index: QModelIndex, value, role: int = ...):
        if role == self.SequenceRoles.ACTION:
            self._config[index.row()] = value

        return True

    def get_config(self):
        return self._config

    def set_config(self, seq):
        # Replace entire sequence with a new one and notify views
        self.beginResetModel()
        items = list(seq or [])
        # pad or truncate to KEYCOUNT
        if len(items) < KEYCOUNT:
            items.extend([''] * (KEYCOUNT - len(items)))
        else:
            items = items[:KEYCOUNT]
        # ensure strings (allow None -> '')
        self._config = [s if isinstance(s, str) else ('' if s is None else str(s)) for s in items]
        self.endResetModel()


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

        self.config = None
        self._json_config = None

        self._action_model = ActionModel()
        self._primary_key_sequence = KeySequenceUI()
        self._secondary_key_sequence = KeySequenceUI()

    def get_qml(self):
        self.populate()
        return 'UsbButtonDetail.qml'

    def populate(self):
        if self.config is None:
            if self.attached:
                devices = [dev for dev in
                           self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                                   address=self.args.address)]
                for dev in devices:
                    with dev as dev_h:
                        # TODO: Add function to device for getting the complete configuration
                        self.config_color = dev_h.to_json_str(dev_h.get_color())
            else:
                self.config = {'schemaVersion': 2.0, 'resourceType': 'usb-button-config',
                               'deviceClass': self.device_class_id.value,
                               'action': 'extended',
                               'releasedColor': {'red': 255, 'green': 255, 'blue': 255},
                               'pressedColor': {'red': 255, 'green': 255, 'blue': 255},
                               'keys': [{'sequence': 'primary',
                                         'row1':[], 'row2': [], 'row3': [], 'row4': []},
                                        {'sequence': 'secondary',
                                         'row1': [], 'row2': [], 'row3': [], 'row4': []}
                                        ]}

        self._json_config = JSONObject(self.config)
        # Ensure UI key sequence models reflect current config
        self._update_sequences_from_config()

    def _build_rows(self, flat_seq: typing.List[typing.Any]):
        """Convert a flat sequence of 24 entries into 4 rows of 6 strings each."""
        # Ensure length
        seq = list(flat_seq or [])
        if len(seq) < KEYCOUNT:
            seq.extend([''] * (KEYCOUNT - len(seq)))
        else:
            seq = seq[:KEYCOUNT]
        # Coerce to strings; allow None -> ''
        seq = [s if isinstance(s, str) else ('' if s is None else str(s)) for s in seq]
        return {
            'row1': seq[0:6],
            'row2': seq[6:12],
            'row3': seq[12:18],
            'row4': seq[18:24],
        }

    def _update_keys_from_sequences(self):
        """Build self.config['keys'] from the current KeySequenceUI models."""
        primary_rows = self._build_rows(self._primary_key_sequence.get_config())
        secondary_rows = self._build_rows(self._secondary_key_sequence.get_config())
        self.config['keys'] = [
            dict(sequence='primary', **primary_rows),
            dict(sequence='secondary', **secondary_rows),
        ]
        # Refresh JSON view used elsewhere
        self._json_config = JSONObject(self.config)

    def _flatten_rows(self, rows_dict: dict) -> typing.List[str]:
        """Flatten a rows dict {'row1':[],..'row4':[]} into a 24-length list of strings."""
        seq = []
        if not rows_dict:
            return [''] * KEYCOUNT
        for key in ('row1', 'row2', 'row3', 'row4'):
            row = rows_dict.get(key, [])
            # ensure list of 6 elements
            row = list(row or [])
            if len(row) < 6:
                row.extend([''] * (6 - len(row)))
            else:
                row = row[:6]
            # force to strings
            seq.extend([s if isinstance(s, str) else ('' if s is None else str(s)) for s in row])
        # safety: ensure 24
        if len(seq) < KEYCOUNT:
            seq.extend([''] * (KEYCOUNT - len(seq)))
        else:
            seq = seq[:KEYCOUNT]
        return seq

    def _update_sequences_from_config(self):
        """Populate KeySequenceUI models from self.config['keys'] entries."""
        keys_list = (self.config or {}).get('keys', []) or []
        # find primary and secondary dicts
        primary = None
        secondary = None
        for k in keys_list:
            if isinstance(k, dict):
                if k.get('sequence') == 'primary':
                    primary = k
                elif k.get('sequence') == 'secondary':
                    secondary = k
        # set sequences
        self._primary_key_sequence.set_config(self._flatten_rows(primary))
        self._secondary_key_sequence.set_config(self._flatten_rows(secondary))

    def write_device(self):
        # Ensure keys are up-to-date from UI models before writing to device
        self._update_keys_from_sequences()
        devices = [dev for dev in
                   self.env.devices.filter(class_id=DeviceClassID.USBButton, bus=self.args.bus,
                                           address=self.args.address)]
        for dev in devices:
            with dev as dev_h:
                return dev_h.set_config_ui(self.config)

    def write_file(self, file):
        # Ensure keys are up-to-date from UI models before writing to file
        self._update_keys_from_sequences()
        if USBButtonDevice.validate_config(self.config, 'usb-button-config.schema'):
            USBButtonDevice.write_to_file(self.config, file.toLocalFile(), indent=2)
            return True
        return False

    def load_file(self, file):
        resource_types = ['usb-button-config']
        config = USBButtonDevice.validate_config_base(file.toLocalFile(), resource_types)
        if not config:
            return False
        # ensure it matches full schema
        if not USBButtonDevice.validate_config(config, 'usb-button-config.schema'):
            return False
        # assign and propagate to models
        self.config = config
        self._json_config = JSONObject(self.config)
        # update key sequences for UI from loaded file
        self._update_sequences_from_config()
        return True
    
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
        return dict(self.config['releasedColor'])

    def set_released_color(self, color):
        new_color = self._validate_color(color)
        if new_color is None:
            _logger.debug(f'Invalid released_color received: {color}')
            return
        if new_color == self.config['releasedColor']:
            return
        self.config['releasedColor'] = new_color
        self._json_config = JSONObject(self.config)

    def get_pressed_color(self):
        return dict(self.config['pressedColor'])

    def set_pressed_color(self, color):
        new_color = self._validate_color(color)
        if new_color is None:
            _logger.debug(f'Invalid pressed_color received: {color}')
            return
        if new_color == self.config['pressedColor']:
        #if new_color == self._pressed_color:
            return
        self.config['pressedColor'] = new_color
        self._json_config = JSONObject(self.config)

    # Action for how the button will behave when pressed
    # Extended: Send both sequences on every press
    # Alternate: Send primary then secondary on alternate press
    # Both: Send primary on short press, Secondary on long press
    def get_action(self):
        return self._json_config.action

    def set_action(self, action):
        if self.config['action'] == action:
            return
        self.config['action'] = action
        self._json_config = JSONObject(self.config)

    # action_model is for the grid combo boxes that contain key presses
    action_model = Property(QObject, get_action_model, constant=True)
    primary_key_sequence = Property(QObject, get_primary_key_sequence, constant=True)
    secondary_key_sequence = Property(QObject, get_secondary_key_sequence, constant=True)
    released_color = Property('QVariant', get_released_color, set_released_color, notify=_changed_released_)
    pressed_color = Property('QVariant', get_pressed_color, set_pressed_color, notify=_changed_pressed_)
    action = Property(str, get_action, set_action, notify=_changed_action_)
