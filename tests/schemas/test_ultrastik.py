#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
from glob import glob
import json
import os
from typing import List

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from unittest import TestCase

from ultimarc.system_utils import git_project_root

class UltraStikSchemaTest(TestCase):

    ultrastik_config_schema = None
    ultrastik_controller_id_config_schema = None

    valid_config_files: List[str] = None
    valid_controller_id_config_files: List[str] = None

    invalid_config_files: List[str] = None
    invalid_controller_id_config_files: List[str] = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(UltraStikSchemaTest, self).setUp()

        self.valid_config_files = []
        self.valid_controller_id_config_files = []

        self.invalid_config_files = []
        self.invalid_controller_id_config_files = []

        schema_root = os.path.join(git_project_root(), 'ultimarc/schemas')
        test_config_root = os.path.join(git_project_root(), 'tests/test-data/ultrastik')
        self.assertTrue(os.path.exists(test_config_root))
        example_config_root = os.path.join(git_project_root(), 'ultimarc/examples')
        self.assertTrue(os.path.exists(example_config_root))

        # Load UltraStik schema files
        config_schema_file = os.path.join(schema_root, 'ultrastik-config.schema')
        self.assertTrue(os.path.exists(config_schema_file))
        controller_schema_file = os.path.join(schema_root, 'ultrastik-controller-id.schema')
        self.assertTrue(os.path.exists(controller_schema_file))

        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(config_schema_file) as h:
            self.ultrastik_config_schema = json.loads(h.read())
        with open(controller_schema_file) as h:
            self.ultrastik_controller_id_config_schema = json.loads(h.read())

        # Load list of invalid config files
        invalid_config_files = glob(os.path.join(test_config_root, 'ultrastik_*.json'))

        for file in invalid_config_files:
            with open(file) as h:
                config = h.read()
                if '"resourceType" : "ultrastik-config"' in config:
                    self.invalid_config_files.append(file)
                elif '"resourceType" : "ultrastik-controller-id"' in config:
                    self.invalid_controller_id_config_files.append(file)
                else:
                    raise AssertionError('Invalid UltraStik config found.')

        self.assertIsNotNone(self.invalid_config_files)
        self.assertIsNotNone(self.invalid_controller_id_config_files)

        # Load list of example config files
        valid_config_files = glob(os.path.join(example_config_root, 'ultrastik-*.json'))
        for file in valid_config_files:
            with open(file) as h:
                config = h.read()
                if '"resourceType" : "ultrastik-config"' in config:
                    self.valid_config_files.append(file)
                elif '"resourceType" : "ultrastik-controller-id"' in config:
                    self.valid_controller_id_config_files.append(file)
                else:
                    raise AssertionError('Invalid UltraStik config found.')

        self.assertIsNotNone(self.valid_config_files)
        self.assertIsNotNone(self.valid_controller_id_config_files)

    def test_valid_controller_id_change_configs(self):
        """ Test valid controller configuration changes """

        self.assertTrue(len(self.valid_controller_id_config_files) > 0)

        for file in self.valid_controller_id_config_files:
            with open(file) as h:
                config = json.loads(h.read())
                self.assertIsNone(validate(config, self.ultrastik_controller_id_config_schema))

    def test_valid_configs(self):
        """ Test valid config files """
        self.assertTrue(len(self.valid_config_files) > 0)

        for file in self.valid_config_files:
            with open(file) as h:
                config = json.loads(h.read())
                self.assertIsNone(validate(config, self.ultrastik_config_schema))

    def test_invalid_controller_id_change_configs(self):
        """ Test that invalid configs raise a validation exception """

        self.assertTrue(len(self.invalid_controller_id_config_files) > 0)

        for file in self.invalid_controller_id_config_files:
            with open(file) as h:
                bad_config = json.loads(h.read())
                with self.assertRaises(ValidationError):
                    validate(bad_config, self.ultrastik_controller_id_config_schema)

    def test_invalid_configs(self):
        """ Test that invalid configs raise a validation exception """
        self.assertTrue(len(self.invalid_config_files) > 0)

        for file in self.invalid_config_files:
            with open(file) as h:
                print(file)
                bad_config = json.loads(h.read())
                with self.assertRaises(ValidationError):
                    validate(bad_config, self.ultrastik_config_schema)
