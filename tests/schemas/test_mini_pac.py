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


class MiniPacSchemaTest(TestCase):

    mini_pac_schema = None
    mini_pac_config = None

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
