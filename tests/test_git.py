import random
import string
import unittest

from pyticket.git import Git

from tests import generators
from tests import utils
from tests.utils import repeat


class GitTest(unittest.TestCase):
    def setUp(self):
        self.directory = utils.get_test_root_dir()
        self.git = Git(self.directory, no_check=True)
        self.git.call_git_command("init", ".")
        self.git = Git(self.directory)

    def tearDown(self):
        pass

    def gen_file(self):
        """Create a new file and returns its name."""
        name = generators.gen_string(1, 20, charset=string.ascii_letters)
        with open(self.directory + "/" + name, "w+") as f:
            f.write(generators.gen_ticket_content())
        return name

    def update_file(self, name):
        """Update a file in the repository."""
        with open(self.directory + "/" + name, "w+") as f:
            f.write(generators.gen_ticket_content())

    def test_add(self):
        name = self.gen_file()
        self.git.add(name)
        changes = self.git.get_diff_files()
        self.assertEqual(len(changes), 1)
        self.assertTrue(name in changes)

    @repeat(100)
    def test_commit(self):
        name = self.gen_file()
        self.git.add(name)
        commit_name = generators.gen_ticket_name()
        self.git.commit(commit_name)
        log = self.git.get_log(1)
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0], "{}".format(commit_name))

    def test_set_branches(self):
        self.test_commit()

        branches = []
        for i in range(0, 10):
            branch_name = generators.gen_ticket_name()
            self.git.set_current_branch(branch_name)
            branches.append(branch_name)

        current_branch = random.choice(branches)
        self.git.set_current_branch(current_branch)
        git_current_branch, git_branches = self.git.get_branches()

        self.assertEqual(set(branches + ["master"]), set(git_branches))
        self.assertEqual(current_branch, git_current_branch)

    def test_push_changes(self):
        name = self.gen_file()
        self.git.add(name)
        self.git.push_changes()
        log = self.git.get_log(1)
        self.assertEqual(log[0], self.git.MAGIC)

    @repeat(100)
    def test_pop_changes(self):
        name = self.gen_file()
        self.git.add(name)
        self.git.commit("some commit")

        self.update_file(name)
        self.git.push_changes()
        log = self.git.get_log(1)
        self.assertEqual(log[0], self.git.MAGIC)

        self.git.pop_changes()
        log = self.git.get_log(1)
        self.assertEqual(log[0], "some commit")

        diff = self.git.get_diff_files()
        self.assertEqual(len(diff), 1)
        self.assertTrue(name in diff)


if __name__ == "__main__":
    unittest.main()
