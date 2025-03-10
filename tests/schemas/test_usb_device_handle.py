#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ultimarc.devices._device import USBDeviceHandle
from ultimarc.system_utils import git_project_root


class USBDeviceHandleTest(TestCase):

    @patch.object(USBDeviceHandle, '_get_descriptor_fields', return_value=None)
    @patch('libusb.get_device', return_value='pointer')
    def test_validate_config_base(self, dev_handle_mock, lib_usb_mock):
        """ Test the validate_config_base() method of the USBDeviceHandle object. """

        dev = USBDeviceHandle('test_handle', '0000:0000')
        self.assertTrue(dev)

        config_file = Path(git_project_root()) / 'tests/test-data/usb-button/usb-button-color-good.json'
        self.assertTrue(dev.validate_config_base(config_file, ['usb-button-color']))
        self.assertIsNone(dev.validate_config_base(config_file, ['bad-resource-type']))

        config_file = Path(git_project_root()) / 'tests/test-data/usb-button/usb-button-color-bad.json'
        self.assertIsNone(dev.validate_config_base(config_file, ['usb-button-color']))
