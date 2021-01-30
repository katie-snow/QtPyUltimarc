#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import os
from unittest.mock import patch

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from unittest import TestCase

from ultimarc.devices._device import USBDeviceHandle
from ultimarc.devices.mini_pac import MiniPacDevice
from ultimarc.system_utils import git_project_root


class MiniPacDeviceTest(TestCase):

    mini_pac_schema = None
    mini_pac_config = None
    mini_pac_bad_config = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(MiniPacDeviceTest, self).setUp()

        schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/mini-pac.schema')
        self.assertTrue(os.path.exists(schema_file))
        config_file = os.path.join(git_project_root(), 'ultimarc/examples/mini-pac.json')
        self.assertTrue(os.path.exists(config_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.mini_pac_schema = json.loads(h.read())
        with open(config_file) as h:
            self.mini_pac_config = json.loads(h.read())

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_mini_pac_data_population (self, dev_handle_mock, lib_usb_mock):
        """ Test that data is being populated correctly when writing to device from json config """
        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        dev.__class__ = MiniPacDevice

        config_file = os.path.join(git_project_root(), 'tests/test-data/mini-pac-good.json')
        valid, data = dev._create_message_(config_file)
        #print(data)
        self.assertTrue(valid)
        self.assertIsNotNone(data)

        # header
        self.assertTrue(data.header.type == 0x50)
        self.assertTrue(data.header.byte_2 == 0xdd)
        self.assertTrue(data.header.byte_3 == 0x0f)
        self.assertTrue(data.header.byte_4 == 0)

        # pins
        # prep work check
        self.assertTrue(data.bytes[16] == 0xff)
        self.assertTrue(data.bytes[32] == 0x00)
        self.assertTrue(data.bytes[34] == 0x00)
        self.assertTrue(data.bytes[49] == 0xff)
        self.assertTrue(data.bytes[50] == 0x0)
        self.assertTrue(data.bytes[108] == 0x01)
        self.assertTrue(data.bytes[147] == 0x01)

        # pin 2b values
        self.assertTrue(data.bytes[0] == 0x29)
        self.assertTrue(data.bytes[50] == 0x0)
        self.assertTrue(data.bytes[100] == 0x0)

        # pin 1down values
        self.assertTrue(data.bytes[8] == 0x51)
        self.assertTrue(data.bytes[58] == 0x13)
        self.assertTrue(data.bytes[110] == 0x40)

        # Macros
        # macro #1
        self.assertTrue(data.bytes[166] == 0xe0)
        self.assertTrue(data.bytes[167] == 0x16)
        self.assertTrue(data.bytes[168] == 0x04)
        self.assertTrue(data.bytes[169] == 0x05)

        # macro #2
        self.assertTrue(data.bytes[170] == 0xe1)
        self.assertTrue(data.bytes[171] == 0x10)
        self.assertTrue(data.bytes[172] == 0x1f)

        # macro #3
        self.assertTrue(data.bytes[173] == 0xe2)
        self.assertTrue(data.bytes[174] == 0x10)
        self.assertTrue(data.bytes[175] == 0x20)
        self.assertTrue(data.bytes[176] == 0x10)
        self.assertTrue(data.bytes[177] == 0x20)
        self.assertTrue(data.bytes[178] == 0x1f)
        self.assertTrue(data.bytes[179] == 0x1e)

        # macro #4 (Is macro #5 in the configuration file)
        self.assertTrue(data.bytes[180] == 0xe3)
        self.assertTrue(data.bytes[181] == 0x10)
        self.assertTrue(data.bytes[182] == 0x1e)

        for x in range(183, 252):
            self.assertTrue(data.bytes[x] == 0)

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_mini_pac_pin_optional_params(self, dev_handle_mock, lib_usb_mock):
        """ Test that optional parameters are handled correctly """
        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        dev.__class__ = MiniPacDevice

        config_file = os.path.join(git_project_root(), 'tests/test-data/mini-pac-pin-optional.json')
        valid, data = dev._create_message_(config_file)

        # pin 1up values, has both optional values
        self.assertTrue(data.bytes[10] == 0x52)
        self.assertTrue(data.bytes[60] == 0x35)
        self.assertTrue(data.bytes[110] == 0x40)

        # pin 1sw2 values no optional values
        self.assertTrue(data.bytes[11] == 0x72)
        self.assertTrue(data.bytes[61] == 0)
        self.assertTrue(data.bytes[111] == 0)
