#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import os

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from unittest import TestCase

from ultimarc.system_utils import git_project_root


class USBButtonSchemaTest(TestCase):

    color_schema = None
    color_config = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class. """
        super(USBButtonSchemaTest, self).setUp()

        schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/usb-button-color.schema')
        self.assertTrue(os.path.exists(schema_file))
        config_file = os.path.join(git_project_root(), 'ultimarc/examples/usb-button-color.json')
        self.assertTrue(os.path.exists(config_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.color_schema = json.loads(h.read())
        with open(config_file) as h:
            self.color_config = json.loads(h.read())

    def test_button_color_good(self):
        """ Test that the test color config matches the color schema. """
        self.assertIsNone(validate(self.color_config, self.color_schema))

    def test_button_color_out_of_range(self):
        """ Test that the test color config matches the color schema. """
        # Set an invalid color range value that is more than 255.
        self.color_config['colorRGB']['red'] = 900

        with self.assertRaises(ValidationError):
            validate(self.color_config, self.color_schema)

        self.color_config['colorRGB']['red'] = 100
        self.color_config['colorRGB']['green'] = 900

        with self.assertRaises(ValidationError):
            validate(self.color_config, self.color_schema)

        self.color_config['colorRGB']['green'] = 100
        self.color_config['colorRGB']['blue'] = 900

        with self.assertRaises(ValidationError):
            validate(self.color_config, self.color_schema)

        # reset values and test a good result.
        self.color_config['colorRGB']['red'] = 100
        self.color_config['colorRGB']['green'] = 100
        self.color_config['colorRGB']['blue'] = 100
        self.assertIsNone(validate(self.color_config, self.color_schema))

        # Set an invalid color range value that is less than 0.
        self.color_config['colorRGB']['red'] = -900

        with self.assertRaises(ValidationError):
            validate(self.color_config, self.color_schema)

        self.color_config['colorRGB']['red'] = 100
        self.color_config['colorRGB']['green'] = -900

        with self.assertRaises(ValidationError):
            validate(self.color_config, self.color_schema)

        self.color_config['colorRGB']['green'] = 100
        self.color_config['colorRGB']['blue'] = -900

        with self.assertRaises(ValidationError):
            validate(self.color_config, self.color_schema)
