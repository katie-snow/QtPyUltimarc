#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import os

import fastjsonschema
from unittest import TestCase

from ultimarc.system_utils import git_project_root


class Ipac2SchemaTest(TestCase):

    ipac2_schema = None
    ipac2_config = None
    ipac2_bad_config = None
    config_validation = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(Ipac2SchemaTest, self).setUp()

        schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/ipac2.schema')
        self.assertTrue(os.path.exists(schema_file))
        config_file = os.path.join(git_project_root(), 'ultimarc/examples/ipac2.json')
        self.assertTrue(os.path.exists(config_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            self.ipac2_schema = json.loads(h.read())
        with open(config_file) as h:
            self.ipac2_config = json.loads(h.read())

        self.config_validation = fastjsonschema.compile(self.ipac2_schema)

    def test_ipac2_good(self):
        """ Test that the test ipac2 config matches the ipac2 schema """
        self.assertIsNotNone(self.config_validation(self.ipac2_config))

    def test_ipac2_bad_json(self):
        """ Test that bad json configurations fail against the ipac2 schema """

        # Macro entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac2/ipac2-macro-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Pin entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac2/ipac2-pin-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Debounce entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac2/ipac2-debounce-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

        # Paclink entry
        bad_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac2/ipac2-paclink-bad.json')
        self.assertTrue(os.path.exists(bad_config_file))

        with open(bad_config_file) as h:
            bad_config = json.loads(h.read())

        with self.assertRaises(fastjsonschema.JsonSchemaValueException):
            self.config_validation(bad_config)

    def test_ipac2_optional_json(self):
        """ Test validation when optional entries are not present """
        # Macro entry
        opt_config_file = os.path.join(git_project_root(),
                                       'tests/test-data/ipac2/ipac2-pin-optional.json')
        self.assertTrue(os.path.exists(opt_config_file))

        with open(opt_config_file) as h:
            opt_config = json.loads(h.read())

        self.assertIsNotNone(self.config_validation(opt_config))
