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


class MiniPacSchemaTest(TestCase):
    mini_pac_schema = None
    mini_pac_config = None
    mini_pac_bad_config = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(MiniPacSchemaTest, self).setUp()

        schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/mini-pac.schema')
        self.assertTrue(os.path.exists(schema_file))
        config_file = os.path.join(git_project_root(), 'ultimarc/examples/mini-pac.json')
        self.assertTrue(os.path.exists(config_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.mini_pac_schema = json.loads(h.read())
        with open(config_file) as h:
            self.mini_pac_config = json.loads(h.read())

    def test_mini_pac_good(self):
        """ Test that the test mini-pac config matches the mini-pac schema """
        self.assertIsNone(validate(self.mini_pac_config, self.mini_pac_schema))

    def test_mini_pac_bad_json(self):
        """ Test that bad json configurations fail against the mini-pac schema """

        # Macro entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/minipac/mini-pac-macro-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.mini_pac_schema)

        # Pin entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/minipac/mini-pac-pin-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.mini_pac_schema)

        # Debounce entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/minipac/mini-pac-debounce-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.mini_pac_schema)

        # Paclink entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/minipac/mini-pac-paclink-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(ValidationError):
            validate(bad_config, self.mini_pac_schema)

    def test_mini_pac_optional_json(self):
        """ Test validation when optional entries are not present """
        # Macro entry
        opt_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/minipac/mini-pac-pin-optional.json')
        self.assertTrue(os.path.exists(opt_config_file))

        with open(opt_config_file) as h:
            opt_config = json.loads(h.read())

        self.assertIsNone(validate(opt_config, self.mini_pac_schema))
