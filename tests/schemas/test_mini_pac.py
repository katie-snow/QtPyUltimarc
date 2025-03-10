#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import fastjsonschema

from pathlib import Path
from unittest import TestCase

from ultimarc.system_utils import git_project_root


class MiniPacSchemaTest(TestCase):
    mini_pac_schema = None
    mini_pac_config = None
    mini_pac_bad_config = None
    config_validation = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(MiniPacSchemaTest, self).setUp()

        schema_file = Path(git_project_root()) / 'ultimarc/schemas/mini-pac.schema'
        self.assertTrue(schema_file.is_file())
        config_file = Path(git_project_root()) / 'ultimarc/examples/mini-pac.json'
        self.assertTrue(config_file.is_file())

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.mini_pac_schema = json.loads(h.read())
        with open(config_file) as h:
            self.mini_pac_config = json.loads(h.read())

        self.config_validation = fastjsonschema.compile(self.mini_pac_schema)

    def test_mini_pac_good(self):
        """ Test that the test mini-pac config matches the mini-pac schema """
        self.assertIsNotNone(self.config_validation(self.mini_pac_config))

    def test_mini_pac_bad_json(self):
        """ Test that bad json configurations fail against the mini-pac schema """

        # Macro entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/minipac/mini-pac-macro-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Pin entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/minipac/mini-pac-pin-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Debounce entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/minipac/mini-pac-debounce-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Paclink entry
        bad_config_file = Path(git_project_root()) / 'tests/test-data/minipac/mini-pac-paclink-bad.json'
        self.assertTrue(bad_config_file.is_file())

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

    def test_mini_pac_optional_json(self):
        """ Test validation when optional entries are not present """
        # Macro entry
        opt_config_file = Path(git_project_root()) / 'tests/test-data/minipac/mini-pac-pin-optional.json'
        self.assertTrue(opt_config_file.is_file())

        with open(opt_config_file) as h:
            opt_config = json.loads(h.read())

        self.assertIsNotNone(self.config_validation(opt_config))
