#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#

import json
import fastjsonschema

from pathlib import Path
from typing import List
from glob import glob

from unittest import TestCase

from ultimarc.system_utils import git_project_root

class UltraStikSchemaTest(TestCase):

    ultrastik_config_schema = None
    ultrastik_controller_id_config_schema = None

    valid_config_files: List[str] = None
    valid_controller_id_config_files: List[str] = None

    invalid_config_files: List[str] = None
    invalid_controller_id_config_files: List[str] = None

    config_validation = None
    controller_id_config_validation = None

    def setUp(self) -> None:
        """ This is called before every test method in the test class """
        super(UltraStikSchemaTest, self).setUp()

        self.valid_config_files = []
        self.valid_controller_id_config_files = []

        self.invalid_config_files = []
        self.invalid_controller_id_config_files = []

        test_config_root = Path(git_project_root()) / 'tests/test-data/ultrastik'
        self.assertTrue(test_config_root.is_dir())
        example_config_root = Path(git_project_root()) / 'ultimarc/examples'
        self.assertTrue(example_config_root.is_dir())

        # Load UltraStik schema files
        schema_dir = Path(git_project_root()) / 'ultimarc/schemas'
        config_schema_file = Path(git_project_root()) / schema_dir / 'ultrastik-config.schema'
        self.assertTrue(config_schema_file.is_file())
        controller_schema_file = Path(git_project_root()) / schema_dir / 'ultrastik-controller-id.schema'
        self.assertTrue(controller_schema_file.is_file())

        with open(config_schema_file) as h:
            self.ultrastik_config_schema = json.loads(h.read())
        with open(controller_schema_file) as h:
            self.ultrastik_controller_id_config_schema = json.loads(h.read())

        self.config_validation = fastjsonschema.compile(self.ultrastik_config_schema)
        self.controller_id_config_validation = fastjsonschema.compile(self.ultrastik_controller_id_config_schema)

        # Load list of invalid config files
        invalid_config_files = glob((test_config_root / 'ultrastik_*.json').__str__())

        # Load the invalid config test files and sort them by ResourceType value.
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

        # Load list of example config files and sort them by ResourceType value.
        valid_config_files = glob((example_config_root / 'ultrastik-*.json').__str__())
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
                self.assertIsNotNone(self.controller_id_config_validation(config))

    def test_valid_configs(self):
        """ Test valid config files """
        self.assertTrue(len(self.valid_config_files) > 0)

        for file in self.valid_config_files:
            with open(file) as h:
                config = json.loads(h.read())
                self.assertIsNotNone(self.config_validation(config))


    def test_invalid_controller_id_change_configs(self):
        """ Test that invalid configs raise a validation exception """

        self.assertTrue(len(self.invalid_controller_id_config_files) > 0)

        for file in self.invalid_controller_id_config_files:
            with open(file) as h:
                bad_config = json.loads(h.read())
                with self.assertRaises(fastjsonschema.JsonSchemaValueException):
                    self.controller_id_config_validation(bad_config)

    def test_invalid_configs(self):
        """ Test that invalid configs raise a validation exception """
        self.assertTrue(len(self.invalid_config_files) > 0)

        for file in self.invalid_config_files:
            with open(file) as h:
                bad_config = json.loads(h.read())
                with self.assertRaises(fastjsonschema.JsonSchemaValueException):
                    self.config_validation(bad_config)
