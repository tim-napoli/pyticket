import unittest
import os.path
import shutil

from pyticket import PyticketException, migrations
from pyticket.repository import (
        Repository, DEFAULT_BUG_TEMPLATE, DEFAULT_FEATURE_TEMPLATE
)

from tests import utils


class RepositoryTest(unittest.TestCase):

    def setUp(self):
        self.root = "/tmp/pyticket-test"
        if os.path.isdir(self.root):
            shutil.rmtree(self.root)
        os.mkdir(self.root)

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_new(self):
        Repository(self.root, create=True)

        pyticket_path = self.root + "/.pyticket"
        contents_path = pyticket_path + "/contents"
        templates_path = pyticket_path + "/templates"
        bug_template_path = templates_path + "/bug"
        feature_template_path = templates_path + "/feature"
        migration_file_path = pyticket_path + "/migration"
        working_file_path = pyticket_path + "/working"
        tickets_file_path = pyticket_path + "/tickets"

        # Check directories are created
        self.assertTrue(os.path.isdir(pyticket_path))
        self.assertTrue(os.path.isdir(contents_path))
        self.assertTrue(os.path.isdir(templates_path))

        # Check template files
        self.assertTrue(os.path.isfile(bug_template_path))
        self.assertTrue(os.path.isfile(feature_template_path))
        self.assertTrue(
            utils.read_file_content(bug_template_path), DEFAULT_BUG_TEMPLATE
        )
        self.assertTrue(
            utils.read_file_content(bug_template_path),
            DEFAULT_FEATURE_TEMPLATE
        )

        # Check migration file
        self.assertTrue(os.path.isfile(migration_file_path))
        migration_version = utils.read_file_content(migration_file_path)
        self.assertEqual(int(migration_version), len(migrations.MIGRATIONS))

        # Check other files
        self.assertTrue(os.path.isfile(working_file_path))
        self.assertTrue(os.path.isfile(tickets_file_path))

        # TODO check default configuration file (use mock)

        # Test init cannot recreate a repository on an existing repository
        self.assertRaises(
            PyticketException, Repository, self.root, create=True
        )


if __name__ == "__main__":
    unittest.main()
