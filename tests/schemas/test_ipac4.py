#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import os

import fastjsonschema
from unittest import TestCase

from ultimarc.system_utils import git_project_root


class Ipac4SchemaTest(TestCase):

    ipac4_schema = None
    ipac4_config = None
    ipac4_bad_config = None
    config_validation = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(Ipac4SchemaTest, self).setUp()

        schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/ipac4.schema')
        self.assertTrue(os.path.exists(schema_file))
        config_file = os.path.join(git_project_root(), 'ultimarc/examples/ipac4.json')
        self.assertTrue(os.path.exists(config_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.ipac4_schema = json.loads(h.read())
        with open(config_file) as h:
            self.ipac4_config = json.loads(h.read())

        self.config_validation = fastjsonschema.compile(self.ipac4_schema)

    def test_ipac4_good(self):
        """ Test that the test ipac4 config matches the ipac4 schema """
        self.assertIsNotNone(self.config_validation(self.ipac4_config))

    def test_ipac4_bad_json(self):
        """ Test that bad json configurations fail against the ipac4 schema """

        # Macro entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac4/ipac4-macro-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Pin entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac4/ipac4-pin-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Debounce entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac4/ipac4-debounce-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Paclink entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac4/ipac4-paclink-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

    def test_ipac4_optional_json(self):
        """ Test validation when optional entries are not present """
        # Macro entry
        opt_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac4/ipac4-pin-optional.json')
        self.assertTrue(os.path.exists(opt_config_file))

        with open(opt_config_file) as h:
            opt_config = json.loads(h.read())

        self.assertIsNotNone(self.config_validation(opt_config))
