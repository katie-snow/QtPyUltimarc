#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json

from pathlib import Path
from unittest.mock import patch
from unittest import TestCase

from ultimarc.devices._device import USBDeviceHandle
from ultimarc.devices._mappings import get_ipac_series_debounce_key
from ultimarc.devices._structures import PacConfigUnion
from ultimarc.devices.ipac4 import Ipac4Device
from ultimarc.system_utils import git_project_root


class Ipac4DeviceTest(TestCase):

    ipac4_schema = None
    ipac4_config = None
    ipac4_bad_config = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(Ipac4DeviceTest, self).setUp()

        schema_file = Path(git_project_root()) / 'ultimarc/schemas/ipac4.schema'
        self.assertTrue(schema_file.is_file())
        config_file = Path(git_project_root()) / 'ultimarc/examples/ipac4.json'
        self.assertTrue(config_file.is_file())

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.ipac4_schema = json.loads(h.read())
        with open(config_file) as h:
            self.ipac4_config = json.loads(h.read())

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_ipac4_data_population (self, dev_handle_mock, lib_usb_mock):
        """ Test that data is being populated correctly when writing to device from json config """
        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        dev.__class__ = Ipac4Device

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-good.json'
        valid, data = dev._create_device_message_(config_file)
        # print(data)
        self.assertTrue(valid)
        self.assertIsNotNone(data)

        # header
        self.assertTrue(data.header.type == 0x50)
        self.assertTrue(data.header.byte_2 == 0xdd)
        self.assertTrue(data.header.byte_3 == 0x0f)
        self.assertTrue(data.header.byte_4 == 0x1c)

        # pins
        # prep work check
        self.assertTrue(data.bytes[128] == 0x01)
        self.assertTrue(data.bytes[150] == 0x01)
        self.assertTrue(data.bytes[153] == 0x0)
        self.assertTrue(data.bytes[170] == 0x0)
        self.assertTrue(data.bytes[179] == 0x0)
        self.assertTrue(data.bytes[192] == 0x0)
        self.assertTrue(data.bytes[193] == 0x0)
        self.assertTrue(data.bytes[194] == 0x0)

        # pin 3start values
        self.assertTrue(data.bytes[23] == 0x20)
        self.assertTrue(data.bytes[87] == 0x27)
        self.assertTrue(data.bytes[151] == 0x01)

        # pin 1down values
        self.assertTrue(data.bytes[13] == 0x51)
        self.assertTrue(data.bytes[77] == 0x13)

        # pin 1left shift value
        self.assertTrue(data.bytes[145] == 0x41)

        # pin 2sw1 use macro in action
        self.assertTrue(data.bytes[8] == 0xe0)

        # pin 2sw2 use macro in alternate action
        self.assertTrue(data.bytes[94] == 0xe1)

        # pin 3sw8 use macro in action
        self.assertTrue(data.bytes[57] == 0xe0)

        # pin 3sw6 use macro in alternate action
        self.assertTrue(data.bytes[65] == 0xe1)

        # pin 4sw3 use macro in action
        self.assertTrue(data.bytes[4] == 0xe0)

        # pin 4sw2 use macro in alternate action
        self.assertTrue(data.bytes[70] == 0xe1)

        # Macros
        # macro #1
        self.assertTrue(data.bytes[195] == 0xe0)
        self.assertTrue(data.bytes[196] == 0x10)
        self.assertTrue(data.bytes[197] == 0x1e)
        self.assertTrue(data.bytes[198] == 0x05)

        # macro #2
        self.assertTrue(data.bytes[199] == 0xe1)
        self.assertTrue(data.bytes[200] == 0x10)
        self.assertTrue(data.bytes[201] == 0x1f)
        self.assertTrue(data.bytes[202] == 0x1f)

        # macro #3
        self.assertTrue(data.bytes[203] == 0xe2)
        self.assertTrue(data.bytes[204] == 0x10)
        self.assertTrue(data.bytes[205] == 0x20)
        self.assertTrue(data.bytes[206] == 0x10)
        self.assertTrue(data.bytes[207] == 0x20)
        self.assertTrue(data.bytes[208] == 0x1f)
        self.assertTrue(data.bytes[209] == 0x1e)

        # macro #4 (Is macro #5 in the configuration file)
        self.assertTrue(data.bytes[210] == 0xe3)
        self.assertTrue(data.bytes[211] == 0x10)
        self.assertTrue(data.bytes[212] == 0x1e)

        for x in range(213, 252):
            self.assertTrue(data.bytes[x] == 0, 'index: ' + str(x))

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_ipac4_pin_optional_params(self, dev_handle_mock, lib_usb_mock):
        """ Test that optional parameters are handled correctly """
        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        dev.__class__ = Ipac4Device

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-pin-optional.json'
        valid, data = dev._create_device_message_(config_file)

        # pin 3sw2 values, has both optional values
        self.assertTrue(data.bytes[33] == 0x75)
        self.assertTrue(data.bytes[97] == 0xe1)
        self.assertTrue(data.bytes[161] == 0x41)

        # pin 3sw3 values no optional values
        self.assertTrue(data.bytes[7] == 0x28)
        self.assertTrue(data.bytes[71] == 0)
        self.assertTrue(data.bytes[135] == 0x01)

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_ipac4_pin_ui_connection(self, dev_handle_mock, lib_usb_mock):
        """ Test that optional parameters are handled correctly """
        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        dev.__class__ = Ipac4Device

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-pin-optional.json'
        # Validate against the base schema.
        resource_types = ['ipac4-pins']
        json_dict = dev.validate_config_base(config_file, resource_types)

        valid, data = dev._create_device_struct_(json_dict)

        # pin 3up values, has both optional values
        self.assertTrue(data.bytes[47] == 0x0c)
        self.assertTrue(data.bytes[111] == 0x0b)
        self.assertTrue(data.bytes[175] == 0x41)

        # pin 4sw3 values no optional values
        self.assertTrue(data.bytes[4] == 0x0b)
        self.assertTrue(data.bytes[67] == 0x0)
        self.assertTrue(data.bytes[133] == 0x01)

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_ipac4_large_macro_entries(self, dev_handle_mock, lib_usb_mock):
        """ Test that faults happen when the number of macros is too great
        and the number of actions doesn't exceed 85 with control characters """
        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)
        dev.__class__ = Ipac4Device

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-macro-large-count.json'
        valid, data = dev._create_device_message_(config_file)
        self.assertFalse(valid)
        self.assertIsNone(data)

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-macro-large-action-count.json'
        valid, data = dev._create_device_message_(config_file)
        self.assertFalse(valid)
        self.assertIsNone(data)

    def test_get_ipac4_series_debounce_key(self):
        """ Test the get_ipac_series_debounce_key function returns valid values """

        # valid values
        self.assertTrue(get_ipac_series_debounce_key(0x0) == 'standard')
        self.assertTrue(get_ipac_series_debounce_key(0x1) == 'none')
        self.assertTrue(get_ipac_series_debounce_key(0x2) == 'short')
        self.assertTrue(get_ipac_series_debounce_key(0x3) == 'long')

        # invalid value given
        self.assertTrue(get_ipac_series_debounce_key(0xff) == 'standard')
        self.assertTrue(get_ipac_series_debounce_key(0x05) == 'standard')

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_header_byte_4_multiple_entries(self, dev_handle_mock, lib_usb_mock):
        """ Test the value of byte 4 of the header with multiple entries """

        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        dev.__class__ = Ipac4Device

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-good.json'
        valid, data = dev._create_device_message_(config_file)

        header = PacConfigUnion()
        header.asByte = data.header.byte_4
        # paclink is True
        self.assertTrue(header.config.paclink == 0x01)
        # debounce is long (0x03)
        self.assertTrue(header.config.debounce == 0x03)

        config_file = Path(git_project_root()) / 'tests/test-data/ipac4/ipac4-pin-optional.json'
        valid, data = dev._create_device_message_(config_file)

        header = PacConfigUnion()
        header.asByte = data.header.byte_4
        # paclink is False
        self.assertTrue(header.config.paclink == 0)
        # debounce is short (0x02)
        self.assertTrue(header.config.debounce == 0x02)
