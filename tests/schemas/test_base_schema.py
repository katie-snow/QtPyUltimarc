#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import os
import fastjsonschema

from glob import glob

from unittest import TestCase

from ultimarc.system_utils import git_project_root


class BaseSchemaTest(TestCase):

    def test_all_schemas(self):
        """
        Test all example JSON configuration files against base.schema.
        """
        schema_file = os.path.join(git_project_root(), 'ultimarc/schemas/base.schema')
        self.assertTrue(os.path.exists(schema_file))
        # https://python-jsonschema.readthedocs.io/en/stable/
        with open(schema_file) as h:
            schema = json.loads(h.read())

        path = os.path.join(git_project_root(), 'ultimarc/examples/')
        files = glob(os.path.join(path, "*.json"))
        for file in files:
            with open(file) as h:
                config = json.loads(h.read())
                validate_config = fastjsonschema.compile(schema)
                self.assertTrue(validate_config(config), 'Testing config: ' + file)

