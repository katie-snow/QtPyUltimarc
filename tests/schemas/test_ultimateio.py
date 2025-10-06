#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import fastjsonschema

from pathlib import Path
from unittest import TestCase

from ultimarc.system_utils import git_project_root


class UltimateIOSchemaTest(TestCase):
    ultimateio_led_schema = None
    ultimateio_pin_schema = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(UltimateIOSchemaTest, self).setUp()

        led_schema_file = Path(git_project_root()) / 'ultimarc/schemas/ultimate-io-led.schema'
        self.assertTrue(led_schema_file.is_file())
        pin_schema_file = Path(git_project_root()) / 'ultimarc/schemas/ultimate-io-pin.schema'
        self.assertTrue(pin_schema_file.is_file())

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(led_schema_file) as h:
            self.ultimateio_led_schema = json.loads(h.read())
        with open(pin_schema_file) as h:
            self.ultimateio_pin_schema = json.loads(h.read())

        self.config_led_validation = fastjsonschema.compile(self.ultimateio_led_schema)
        self.config_pin_validation = fastjsonschema.compile(self.ultimateio_pin_schema)

    def test_ultimateio_good(self):
        """ Test that the ultimate-io-pin and ultimate-io-led config matches their respective schemas """
        config_file = Path(git_project_root()) / 'ultimarc/examples/ultimateIO/ultimate-io-led.json'
        self.assertTrue(config_file.is_file())
        with open(config_file) as h:
            good_config = json.loads(h.read())
        self.assertIsNotNone(self.config_led_validation(good_config))

        config_file = Path(git_project_root()) / 'ultimarc/examples/ultimateIO/ultimate-io-pin.json'
        self.assertTrue(config_file.is_file())
        with open(config_file) as h:
            good_config = json.loads(h.read())
        self.assertIsNotNone(self.config_pin_validation(good_config))

    def test_ultimateio_bad_pin_json(self):
        """ Test that bad json configurations fail against the ultimate-io pin schema """

        # Macro entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-macro-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_pin_validation(bad_config)

        # Pin entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-pin-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_pin_validation(bad_config)

        # Debounce entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-debounce-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_pin_validation(bad_config)

    def test_ultimateio_bad_led_json(self):
        """ Test that bad json configurations fail against the ultimate-io led schema """

        # all intensities
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-all-intensities-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_led_validation(bad_config)

        # intensities
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-led-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_led_validation(bad_config)

        # random states
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-randomState-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_led_validation(bad_config)

        # fade rate
        bad_config_file = Path(git_project_root()) / 'tests/test-data/ultimateIO/ultimateio-fadeRate-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_led_validation(bad_config)
