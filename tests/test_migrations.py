"""Tests migrations."""
import unittest
import os
import os.path
import shutil
import random

from pyticket import migrations
from pyticket.ticket import MetaTicket

from tests import generators
from tests.utils import repeat


class MigrationsTest(unittest.TestCase):

    def setUp(self):
        self.directory = "/tmp/pyticket-test"
        if os.path.isdir(self.directory):
            shutil.rmtree(self.directory)
        os.makedirs(self.directory)

    def tearDown(self):
        shutil.rmtree(self.directory)

    def test_working_ticket_migration(self):
        migrations.working_ticket_migration(self.directory)
        self.assertTrue(os.path.isfile(self.directory + "/working"))

    @repeat(10)
    def test_meta_files_migration(self):
        def gen_ticket_content():
            """Generate a random ticket contents.

            :return: a couple (tags, content) where tags is a list of tags,
                     and content is the ticket content.
            """
            content = generators.gen_ticket_content()
            tags = []
            if random.choice([True, False]):
                tags = generators.gen_tags()
                content = content + "\ntags: " + ",".join(tags)
            return (tags, content)

        if os.path.isdir(self.directory + "/contents"):
            shutil.rmtree(self.directory + "/contents")
        if os.path.isdir(self.directory + "/opened"):
            shutil.rmtree(self.directory + "/opened")
        if os.path.isdir(self.directory + "/closed"):
            shutil.rmtree(self.directory + "/closed")
        os.mkdir(self.directory + "/opened")
        os.mkdir(self.directory + "/closed")

        # Generate some tickets.
        tickets = []
        taken_names = []
        for i in range(0, 100):
            name = generators.gen_ticket_name()
            if name in taken_names:
                continue
            taken_names.append(name)
            status = random.choice(["opened", "closed"])
            tags, content = gen_ticket_content()
            path = "{}/{}/{}".format(self.directory, status, name)
            with open(path, "w+") as f:
                f.write(content)
            tickets.append(MetaTicket(name, status, tags))

        # Apply the migration.
        migrations.tickets_meta_files_migration(self.directory)

        # Check there is no more opened and closed directory
        self.assertFalse(os.path.isdir(self.directory + "/opened"))
        self.assertFalse(os.path.isdir(self.directory + "/closed"))

        # Check the tickets file.
        with open(self.directory + "/tickets", "r") as f:
            lines = f.read().splitlines()
            self.assertEqual(len(lines), len(tickets))
            for line in lines:
                meta_ticket = MetaTicket.parse(line)
                self.assertTrue(meta_ticket in tickets)
                self.assertTrue(os.path.isfile(
                    self.directory + "/contents/" + meta_ticket.name
                ))


if __name__ == "__main__":
    unittest.main()
