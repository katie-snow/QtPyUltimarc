#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import ctypes as ct
import json
from pathlib import Path
from unittest import TestCase

from ultimarc.system_utils import git_project_root
from ultimarc.devices.usb_button import (
    USBButtonDevice,
    USBButtonColorStruct,
    USBButtonConfigStruct,
    RGBValueStruct,
    ROWARRAY,
    ButtonModeMapping,
)
from ultimarc.devices._device import USBRequestCode


class DummyButton(USBButtonDevice):
    def __init__(self):
        # do not call super; avoid libusb
        self.dev_key = 'd209:1200'
        self.interface = 0
        self._writes = []
        self._reads = []
        self._read_success = True
        self._color_to_read = (1, 2, 3)

    # override USB I/O to avoid libusb
    def write(self, b_request, report_id, w_index, data=None, size=None, request_type=None, recipient=None):
        self._writes.append(('write', b_request, report_id, w_index, data, size))
        return True

    def write_alt(self, b_request, report_id, w_index, data=None, size=None, request_type=None, recipient=None):
        self._writes.append(('write_alt', b_request, report_id, w_index, data, size))
        return True

    def read(self, b_request, w_value, w_index, data=None, size=None, request_type=None, recipient=None):
        # emulate filling structure for get_color
        try:
            data.rgb.red = self._color_to_read[0]
            data.rgb.green = self._color_to_read[1]
            data.rgb.blue = self._color_to_read[2]
        except Exception:
            pass
        self._reads.append(('read', b_request, w_value, w_index, size))
        return self._read_success


class USBButtonDeviceTests(TestCase):
    def setUp(self):
        self.dev = DummyButton()

    def test_set_color_validates_and_writes(self):
        # valid
        ok = self.dev.set_color(10, 20, 30)
        self.assertTrue(ok)
        # one write recorded with struct
        self.assertEqual(len(self.dev._writes), 1)
        call = self.dev._writes[0]
        self.assertEqual(call[0], 'write')
        self.assertEqual(call[1], USBRequestCode.SET_CONFIGURATION)
        data = call[4]
        self.assertIsInstance(data, USBButtonColorStruct)
        self.assertEqual((data.rgb.red, data.rgb.green, data.rgb.blue), (10, 20, 30))

        # invalid values raise
        with self.assertRaises(ValueError):
            self.dev.set_color(-1, 0, 0)
        with self.assertRaises(ValueError):
            self.dev.set_color(0, 256, 0)
        with self.assertRaises(ValueError):
            self.dev.set_color('a', 0, 0)

    def test_get_color_success_and_failure(self):
        self.dev._color_to_read = (7, 8, 9)
        r, g, b = self.dev.get_color()
        self.assertEqual((r, g, b), (7, 8, 9))
        # failure path returns (None, None, None)
        self.dev._read_success = False
        r, g, b = self.dev.get_color()
        self.assertIsNone(r)
        self.assertIsNone(g)
        self.assertIsNone(b)

    def test_set_config_color_json(self):
        # use example color config file
        root = Path(git_project_root())
        cfg = root / 'ultimarc/examples/usb-button-color.json'
        self.assertTrue(cfg.is_file())
        ok = self.dev.set_config(str(cfg))
        self.assertTrue(ok)
        # ensure write was called with a color struct
        kind, *_rest, data, size = self.dev._writes[-1]
        self.assertEqual(kind, 'write')
        self.assertIsInstance(data, USBButtonColorStruct)

    def test_set_config_full_json(self):
        # use example full config
        root = Path(git_project_root())
        cfg = root / 'ultimarc/examples/usb-button-config.json'
        self.assertTrue(cfg.is_file())
        ok = self.dev.set_config(str(cfg))
        self.assertTrue(ok)
        # ensure write_alt was called with a config struct
        kind, *_rest, data, size = self.dev._writes[-1]
        self.assertEqual(kind, 'write_alt')
        self.assertIsInstance(data, USBButtonConfigStruct)

    def test_create_json_from_struct(self):
        # Build a minimal USBButtonConfigStruct containing key mapping values
        released = RGBValueStruct(1, 2, 3)
        pressed = RGBValueStruct(4, 5, 6)
        rows = []
        # Fill rows with a sequence of known values that map back using get_ipac_series_mapping_key
        # We'll use SPACE (0x2C) and 'A'(0x04), 'B'(0x05) etc from mapping; but create by value directly.
        row_vals = [0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D]  # U V W X Y Z
        for _ in range(8):
            arr = ROWARRAY(0)
            for i, v in enumerate(row_vals):
                arr[i] = v
            rows.append(arr)
        data = USBButtonConfigStruct(0x50, 0xdd, list(ButtonModeMapping.values())[0], 0x00,
                                     released, pressed,
                                     rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], ROWARRAY(0))
        json_obj = self.dev.create_json(data)
        self.assertIsInstance(json_obj, dict)
        self.assertEqual(json_obj['deviceClass'], 'usb-button')
        self.assertIn(json_obj['action'], ButtonModeMapping.keys())
        self.assertEqual(json_obj['releasedColor'], {'red': 1, 'green': 2, 'blue': 3})
        self.assertEqual(json_obj['pressedColor'], {'red': 4, 'green': 5, 'blue': 6})
        # keys primary and secondary should both exist with rows of 6 entries
        self.assertEqual(len(json_obj['keys']), 2)
        for keyset in json_obj['keys']:
            self.assertEqual(len(keyset['row1']), 6)
            self.assertEqual(len(keyset['row2']), 6)
            self.assertEqual(len(keyset['row3']), 6)
            self.assertEqual(len(keyset['row4']), 6)

    def test_write_to_file(self):
        tmp = Path(git_project_root()) / 'tests' / 'tmp-usb-button.json'
        try:
            obj = {'a': 1}
            ok = self.dev.write_to_file(obj, str(tmp), indent=2)
            self.assertTrue(ok)
            with open(tmp) as h:
                data = json.load(h)
            self.assertEqual(data, obj)
        finally:
            if tmp.exists():
                tmp.unlink()

        # invalid path
        bad_path = str(Path('/nonexistent/dir/path/file.json'))
        ok = self.dev.write_to_file({'a': 1}, bad_path)
        self.assertFalse(ok)
