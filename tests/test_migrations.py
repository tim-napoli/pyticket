"""Tests migrations."""
import unittest
import os
import os.path
import shutil
import random

from pyticket import migrations
from pyticket.ticket import MetaTicket

from tests import generators
from tests import utils
from tests.utils import repeat


class MigrationsTest(unittest.TestCase):

    def setUp(self):
        self.directory = utils.get_test_root_dir()
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

    def test_mtime_migration(self):
        os.mkdir(self.directory + "/contents")

        # Generate some tickets.
        tickets = {}
        with open(self.directory + "/tickets", "w+") as f:
            for i in range(0, 100):
                name = generators.gen_ticket_name()
                status = generators.gen_status()
                tags = generators.gen_tags()
                mtime = None
                if random.choice([True, False]):
                    content = generators.gen_ticket_content()
                    path = "{}/contents/{}".format(self.directory, name)
                    with open(path, "w+") as f_content:
                        f_content.write(content)
                        mtime = os.path.getmtime(path)
                f.write("{} {} ({})\n".format(name, status, ",".join(tags)))
                tickets[name] = (status, tags, mtime)

        # Apply migration
        migrations.tickets_mtime_migration(self.directory)

        # Tests
        with open(self.directory + "/tickets", "r") as f:
            lines = f.read().splitlines()
            self.assertEqual(len(lines), len(tickets))
            for line in lines:
                ticket = MetaTicket.parse(line)
            self.assertTrue(ticket.name in tickets)
            self.assertEqual(ticket.status, tickets[ticket.name][0])
            self.assertEqual(ticket.tags, tickets[ticket.name][1])
            if tickets[ticket.name][2]:
                self.assertEqual(ticket.mtime, tickets[ticket.name][2])


if __name__ == "__main__":
    unittest.main()
