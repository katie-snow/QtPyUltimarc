#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import fastjsonschema

from pathlib import Path
from unittest import TestCase

from ultimarc.system_utils import git_project_root


class JpacSchemaTest(TestCase):

    jpac_schema = None
    jpac_config = None
    jpac_bad_config = None
    config_validation = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(JpacSchemaTest, self).setUp()

        schema_file = Path(git_project_root()) / 'ultimarc/schemas/jpac.schema'
        self.assertTrue(schema_file.is_file())
        config_file = Path(git_project_root()) / 'ultimarc/examples/jpac.json'
        self.assertTrue(config_file.is_file())

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.jpac_schema = json.loads(h.read())
        with open(config_file) as h:
            self.jpac_config = json.loads(h.read())

        self.config_validation = fastjsonschema.compile(self.jpac_schema)

    def test_jpac_good(self):
        """ Test that the test jpac config matches the jpac schema """
        self.assertIsNotNone(self.config_validation(self.jpac_config))

    def test_jpac_bad_json(self):
        """ Test that bad json configurations fail against the jpac schema """

        # Macro entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/jpac/jpac-macro-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Pin entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/jpac/jpac-pin-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Debounce entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/jpac/jpac-debounce-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Paclink entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/jpac/jpac-paclink-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

    def test_jpac_optional_json(self):
        """ Test validation when optional entries are not present """
        # Macro entry
        opt_config_file = Path(git_project_root()) / 'tests/test-data/jpac/jpac-pin-optional.json'
        self.assertTrue(opt_config_file.is_file())

        with open(opt_config_file) as h:
            opt_config = json.loads(h.read())

        self.assertIsNotNone(self.config_validation(opt_config))

    def test_jpac_disabled_pin(self):
        """ Test the 'disable' entry """
        bad_config_file = Path(git_project_root()) / 'tests/test-data/jpac/jpac-bad-disabled-pin.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)
