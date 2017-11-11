"""Git commands for git integration."""
import os.path
import re
import subprocess

from pyticket import PyticketException


class Git:
    """A git wrapper used to integrate pyticket with git.

    This wrapper is a really simple one. We just use shell commands to interact
    with git, capturing and handling its output.

    The purpose of this class inside pyticket is the following:
    - When a user "works on" a ticket, we toggle the current git branch.
      If we were already working on a ticket, we need to save current changes.
      To do so, we commit every changes in a "magic commit" (a commit with
      the 'Git.MAGIC' name).

    :param directory: the directory in which the git repository is contained.
    :param no_check: if True, no check is done to know if a git repository is
                     in 'directory'.
    :raises PyticketException: 'directory' doesn't contain a git repository.
    """
    MAGIC = "Bl3ctr3F0r3v3r"

    def __init__(self, directory, no_check=False):
        if not no_check and not Git.is_git_repository(directory):
            raise PyticketException("Not a git repository")
        self.work_dir = directory

    def call_git_command(self, *args):
        """Call a git command in the repository.

        :param args: the git command parameters.
        :return: the standard output of the command.
        """
        command = [
            "git",
            "--git-dir={}/.git".format(self.work_dir),
            "--work-tree={}".format(self.work_dir),
        ]
        for arg in args:
            command.append(arg)
        result = subprocess.Popen(command, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        res_str = result.communicate()
        return res_str[0].decode("utf-8")

    def add(self, name):
        """Helper for the git add command.

        :param name: the name of the file to add.
        """
        self.call_git_command("add", name)

    def commit(self, commit_msg):
        """Commit current changes.

        :param commit_msg: the commit message.
        """
        self.call_git_command("commit", "-m", commit_msg)

    def get_log(self, count):
        """Get the git log.

        :param count: get at most 'count' entries.
        :return: a list of commit names in ante-chronologic order.
        """
        result = self.call_git_command("log", "-{}".format(count), "--oneline")
        commits = [" ".join(log.split()[1:]) for log in result.splitlines()]
        return commits

    def get_diff_files(self):
        """Get every modified files (staged and unstaged).

        :return: the of name of modified file.
        """
        not_cached = self.call_git_command("diff", "--name-only").split()
        cached = self.call_git_command(
            "diff", "--cached", "--name-only"
        ).split()
        return not_cached + cached

    def push_changes(self):
        """Save every changes (if any) in the "magic commit"."""
        files = self.get_diff_files()
        if files:
            for f in files:
                self.call_git_command("add", f)
            self.call_git_command("commit", "-m", Git.MAGIC)

    def pop_changes(self):
        """Pop the "magic commit" (if it exists)."""
        result = self.call_git_command("log", "-1", "--oneline")
        message = result.split()[1]
        if message == Git.MAGIC:
            self.call_git_command("reset", "HEAD~")

    def get_branches(self):
        """Returns the repository's list of branches."""
        result = self.call_git_command("branch")
        BRANCH_PATTERN = r"^\*?\s+(?P<name>.*)$"
        branches = []
        working_branch = None
        for line in result.splitlines():
            m = re.match(BRANCH_PATTERN, line)
            if m:
                branch_name = m.groups("name")[0]
                branches.append(branch_name)
                if line[0] == "*":
                    working_branch = branch_name
        return (working_branch, branches)

    def set_current_branch(self, name):
        """Checkout the given branch name.

        If this branch doesn't exist, create it.

        :param name: the branch name.
        """
        _, branches = self.get_branches()
        if name in branches:
            self.call_git_command("checkout", name)
        else:
            self.call_git_command("checkout", "-b", name)

    @staticmethod
    def is_git_repository(directory):
        """Check if the given directory contains a git repository."""
        return os.path.isdir(directory + "/.git")
