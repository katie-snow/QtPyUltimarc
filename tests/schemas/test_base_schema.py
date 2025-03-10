#
# This file is subject to the terms and conditions defined in the
# file 'LICENSE', which is part of this source code package.
#
import json
import fastjsonschema

from pathlib import Path
from glob import glob

from unittest import TestCase

from ultimarc.system_utils import git_project_root


class BaseSchemaTest(TestCase):

    def test_all_schemas(self):
        """
        Test all example JSON configuration files against base.schema.
        """
        schema_file = Path(git_project_root()) / 'ultimarc/schemas/base.schema'
        self.assertTrue(schema_file.is_file())

        with open(schema_file) as h:
            schema = json.loads(h.read())

        path = Path(git_project_root()) /  'ultimarc/examples/'
        files = glob(Path(path / "*.json").__str__())
        for file in files:
            with open(file) as h:
                config = json.loads(h.read())
                validate_config = fastjsonschema.compile(schema)
                self.assertTrue(validate_config(config), 'Testing config: ' + file)

