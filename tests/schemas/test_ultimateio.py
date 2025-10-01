#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import os
from unittest import TestCase

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from ultimarc.system_utils import git_project_root


class UltimateIOSchemaTest(TestCase):
    ultimateio_led_schema = None
    ultimateio_pin_schema = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(UltimateIOSchemaTest, self).setUp()

        led_schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/ultimate-io-led.schema')
        self.assertTrue(os.path.exists(led_schema_file))
        pin_schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/ultimate-io-pin.schema')
        self.assertTrue(os.path.exists(pin_schema_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(led_schema_file) as h:
            self.ultimateio_led_schema = json.loads(h.read())
        with open(pin_schema_file) as h:
            self.ultimateio_pin_schema = json.loads(h.read())

    def test_ultimateio_good(self):
        """ Test that the ultimate-io-pin and ultimate-io-led config matches their respective schemas """
        config_file = os.path.join(git_project_root(), 'ultimarc/examples/ultimateIO/ultimateio-led.json')
        self.assertTrue(os.path.exists(config_file))
        with open(config_file) as h:
            good_config = json.loads(h.read())
        self.assertIsNone(validate(good_config, self.ultimateio_led_schema))

        config_file = os.path.join(git_project_root(), 'ultimarc/examples/ultimateIO/ultimateio-pin.json')
        self.assertTrue(os.path.exists(config_file))
        with open(config_file) as h:
            good_config = json.loads(h.read())
        self.assertIsNone(validate(good_config, self.ultimateio_pin_schema))

    def test_ultimateio_bad_led_json(self):
        """ Test that bad json configurations fail against the led ultimateio schema """

        # intensities
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-led-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))
        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())
        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)

        # RandomState
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-randomState-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))
        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())
        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)

        # FadeRate
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-fadeRate-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))
        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())
        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)

    def test_ultimateio_bad_pin_json(self):
        """ Test that bad json configurations fail against the ultimate-io pin schema """

        # Macro entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-macro-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_pin_schema)

        # Pin entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-pin-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_pin_schema)

        # Debounce entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-debounce-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_pin_schema)

    def test_ultimateio_bad_led_json(self):
        """ Test that bad json configurations fail against the ultimate-io led schema """

        # all intensities
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-all-intensities-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)

        # intensities
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-led-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)

        # random states
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-randomState-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)

        # fade rate
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ultimateIO/ultimateio-fadeRate-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.ultimateio_led_schema)