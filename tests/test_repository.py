import unittest
import os.path
import shutil
import random

from pyticket import PyticketException, migrations
from pyticket.ticket import MetaTicket
from pyticket.repository import (
        Repository, DEFAULT_BUG_TEMPLATE, DEFAULT_FEATURE_TEMPLATE
)
import pyticket.utils

from tests import utils
from tests import generators
from tests.utils import repeat


class RepositoryTest(unittest.TestCase):

    def setUp(self):
        self.root = utils.get_test_root_dir()
        self.maxDiff = None
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

    def test_create_ticket(self):
        r = Repository(self.root, create=True)

        taken_names = []
        tickets = []
        for i in range(0, random.randrange(1000)):
            if not random.randrange(10):
                name = generators.gen_child_ticket_name(taken_names)
            else:
                name = generators.gen_ticket_name()
            if name in taken_names:
                continue
            taken_names.append(name)
            status = random.choice(["opened", "closed"])
            tags = generators.gen_tags()
            created = random.choice([True, False])

            r.create_ticket(name, status, tags, created)

            meta = MetaTicket(name, status, tags)
            tickets.append((meta, created))

        # We reload the repository to check if the tickets file has been
        # updated.
        r = Repository(self.root)
        self.assertEqual(len(tickets), len(r.tickets))
        for ticket, created in tickets:
            repo_ticket = r.get_ticket(ticket.name)
            self.assertEqual(repo_ticket, ticket)
            if created:
                path = "{}/{}".format(r.contents, repo_ticket.name)
                self.assertTrue(os.path.isfile(path))

    def test_create_ticket_invalid_name(self):
        r = Repository(self.root, create=True)
        ticket_name = "this-is-an#~ê³²¹invalid-name"
        self.assertRaises(
            PyticketException, r.create_ticket, ticket_name, "opened", []
        )

    def test_create_ticket_invalid_parent(self):
        r = Repository(self.root, create=True)
        ticket_name = "unexisting-root.child"
        self.assertRaises(
            PyticketException, r.create_ticket, ticket_name, "opened", []
        )

    def test_create_ticket_invalid_status(self):
        r = Repository(self.root, create=True)
        ticket_name = generators.gen_ticket_name()
        self.assertRaises(
            PyticketException, r.create_ticket, ticket_name, "dksbidsg", []
        )

    def test_create_ticket_invalid_tags(self):
        r = Repository(self.root, create=True)
        ticket_name = generators.gen_ticket_name()
        tags = ["valid-tag", "inv[[@ê³*ù$alid-tag"]
        self.assertRaises(
            PyticketException, r.create_ticket, ticket_name, "opened", tags
        )

    @repeat(100)
    def test_write_and_read_ticket_content(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = generators.gen_tags()

        r.create_ticket(name, status, tags)

        content = generators.gen_ticket_content()
        r.write_ticket_content(name, content)

        read_content = r.read_ticket_content(name)
        self.assertEqual(content, read_content)

    def test_write_wrong_name(self):
        r = Repository(self.root, create=True)
        self.assertRaises(
            PyticketException, r.write_ticket_content, "blectre", "content"
        )

    def test_read_wrong_name(self):
        r = Repository(self.root, create=True)
        self.assertRaises(
            PyticketException, r.read_ticket_content, "blectre"
        )

    def test_read_no_content(self):
        r = Repository(self.root, create=True)
        r.create_ticket("test", "opened", [])
        self.assertRaises(
            PyticketException, r.read_ticket_content, "test"
        )

    @repeat(100)
    def test_switch_ticket_status(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)

        new_status = generators.gen_status()
        r.switch_ticket_status(name, new_status)
        self.assertEqual(r.get_ticket(name).status, new_status)

        # Reload repository and tickets file
        r = Repository(self.root)
        self.assertEqual(r.get_ticket(name).status, new_status)

    def test_switch_ticket_status_invalid_status(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)

        self.assertRaises(
            PyticketException, r.switch_ticket_status, name, "blectre"
        )

    def test_switch_ticket_status_invalid_name(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)

        self.assertRaises(
            PyticketException, r.switch_ticket_status, name + "x", status
        )

    def test_switch_ticket_status_opened_child(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = "opened"
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)

        child_name = name + "." + generators.gen_ticket_name()
        status = "opened"
        tags = generators.gen_tags()
        r.create_ticket(child_name, status, tags)

        self.assertRaises(
            PyticketException, r.switch_ticket_status, name, "closed"
        )

    def test_closing_working_ticket(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = "opened"
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)
        r.set_working_ticket(name)

        r.switch_ticket_status(name, "closed")
        self.assertFalse(r.get_working_ticket())

    @repeat(10)
    def test_switch_ticket_status_reopening_parents(self):
        r = Repository(self.root, create=True)

        count = random.randrange(1, 10)
        parents = []
        name = generators.gen_ticket_name()
        for i in range(0, count):
            status = "closed"
            tags = generators.gen_tags()
            r.create_ticket(name, status, tags)
            parents.append(name)
            name = name + "." + generators.gen_ticket_name()

        r.switch_ticket_status(parents[-1], "opened")
        for ticket in parents:
            self.assertEqual(r.get_ticket(ticket).status, "opened")

    @staticmethod
    def set_ticket_as_child_of_its_ancestors(parents, name):
        """Given a map ```parents``` associating to a ticket name the
        list of every of its descendants, add the ticket ```name``` to
        every of its ancestor's childs list.
        """
        parent = pyticket.utils.get_ticket_parent_name(name)
        while parent:
            if parent not in parents:
                parents[parent] = [name]
            else:
                parents[parent].append(name)
            parent = pyticket.utils.get_ticket_parent_name(parent)

    @staticmethod
    def generate_tickets(repository, count, gen_child_probability):
        """Generate ```count``` tickets for the given repository.

        :param repository: the repository for which creating tickets.
        :param count: the number of tickets to create.
        :param gen_child_probability: the probability to generate a child
                                      ticket.
        :return: a couple (tickets, parents) where :
                 - tickets is a list of every created ticket names ;
                 - parents is a map associating to a ticket name every of its
                   descendants.
        """
        taken_names = []
        parents = {}
        tickets = []
        while count > 0:
            # Generate a ticket name.
            if taken_names and random.random() <= gen_child_probability:
                name = generators.gen_child_ticket_name(taken_names)
            else:
                name = generators.gen_ticket_name()
            if name in taken_names:
                continue
            taken_names.append(name)

            RepositoryTest.set_ticket_as_child_of_its_ancestors(parents, name)

            status = generators.gen_status()
            tags = generators.gen_tags()
            created = random.choice([True, False])

            repository.create_ticket(name, status, tags, created)

            tickets.append(name)

            count = count - 1
        return (tickets, parents)

    def test_get_ticket_childs(self):
        # Create a repository with some parent tickets.
        r = Repository(self.root, create=True)
        _, parents = RepositoryTest.generate_tickets(r, 1000, 0.3)

        # Check the get_ticket_childs method.
        for parent, childs in parents.items():
            returned_childs = [t.name for t in r.get_ticket_childs(parent)]
            self.assertTrue(set(childs).issuperset(returned_childs))

            returned_childs = [
                t.name for t in r.get_ticket_childs(parent, recursive=True)
            ]
            self.assertFalse(set(childs) - set(returned_childs))

    def test_rename_ticket(self):
        def rename_parent(ticket, prev_parent, new_parent):
            basename = ticket[len(prev_parent)+1:]
            return new_parent + "." + basename

        def get_renamed_childs_list(tickets, name, new_name):
            renamed = []
            for ticket in tickets:
                if ticket.startswith(name + "."):
                    new_child_name = rename_parent(ticket, name, new_name)
                    renamed.append(new_child_name)
                else:
                    renamed.append(ticket)
            return renamed

        def get_renamed_new_names_map(new_names, name, new_name):
            renamed = {}
            for candidate_name, candidate_new_name in new_names.items():
                if candidate_new_name.startswith(name + "."):
                    new_child_new_name = rename_parent(
                        candidate_new_name, name, new_name
                    )
                    renamed[candidate_name] = new_child_new_name
                else:
                    renamed[candidate_name] = candidate_new_name
            return renamed

        # Create a repository with some parent tickets.
        r = Repository(self.root, create=True)
        tickets, parents = RepositoryTest.generate_tickets(r, 100, 0.3)

        # Renaming some tickets
        new_names = {}
        to_rename = random.sample(tickets, random.randrange(len(tickets)))
        for ticket in to_rename:
            r.write_ticket_content(ticket, "blablabla")

        while to_rename:
            ticket = to_rename.pop(0)
            if new_names and random.random() < 0.2:
                parent_name = random.choice(list(new_names.values()))
            else:
                parent_name = pyticket.utils.get_ticket_parent_name(ticket)
            new_name = None
            while not new_name:
                new_basename = generators.gen_ticket_name()
                new_name = (parent_name + "." + new_basename if parent_name
                            else new_basename)
                if new_name in tickets:
                    new_name = None
            r.rename_ticket(ticket, new_name)
            new_names[ticket] = new_name

            # Update eventual childs in both collections
            to_rename = get_renamed_childs_list(to_rename, ticket, new_name)
            new_names = get_renamed_new_names_map(new_names, ticket, new_name)

        # Checking all is right
        for prev_name, new_name in new_names.items():
            # Check we have no more previous name
            self.assertFalse(r.has_ticket(prev_name))
            # Check we have new name
            self.assertTrue(r.has_ticket(new_name))
            # Check content has been renamed
            self.assertRaises(
                PyticketException, r.has_ticket_content, prev_name
            )
            self.assertTrue(r.has_ticket_content(new_name))
            # If the tickets had childs, check childs are correctly renamed
            # too
            if prev_name not in parents:
                continue
            for child in parents[prev_name]:
                self.assertFalse(r.has_ticket(child))

    def test_rename_ticket_unknown_name(self):
        r = Repository(self.root, create=True)
        self.assertRaises(
            PyticketException, r.rename_ticket, "blectre", "new-blectre"
        )

    def test_rename_ticket_invalid_name(self):
        r = Repository(self.root, create=True)
        r.create_ticket("blectre", "opened", [])
        self.assertRaises(
            PyticketException, r.rename_ticket, "blectre", "new-bl£$`ectre"
        )

    def test_rename_ticket_invalid_new_parent(self):
        r = Repository(self.root, create=True)
        r.create_ticket("blectre", "opened", [])
        self.assertRaises(
            PyticketException, r.rename_ticket, "blectre", "parent.blectre"
        )

    def test_delete_ticket(self):
        def removed_ticket_childs(tickets, to_delete, name):
            remaining = []
            deleted = []
            for ticket in tickets:
                if ticket.startswith(name + "."):
                    deleted.append(ticket)
            for ticket in to_delete:
                if not ticket.startswith(name + "."):
                    remaining.append(ticket)
            return (remaining, deleted)

        r = Repository(self.root, create=True)
        tickets, parents = RepositoryTest.generate_tickets(r, 500, 0.3)

        deleted = []
        to_delete = random.sample(tickets, random.randrange(len(tickets)))
        while to_delete:
            ticket = to_delete.pop(0)
            r.delete_ticket(ticket)
            to_delete, rec_deleted = removed_ticket_childs(
                tickets, to_delete, ticket
            )
            deleted.append(ticket)
            deleted += rec_deleted

        for ticket in deleted:
            self.assertFalse(r.has_ticket(ticket))
        for ticket in tickets:
            if ticket not in deleted:
                self.assertTrue(r.has_ticket(ticket))

    def test_delete_ticket_invalid_name(self):
        r = Repository(self.root, create=True)
        self.assertRaises(PyticketException, r.delete_ticket, "blectre")

    @repeat(100)
    def test_add_tags(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = generators.gen_tags()

        r.create_ticket(name, status, tags)

        new_tags = generators.gen_tags()
        r.add_tags(name, new_tags)

        ticket = r.get_ticket(name)
        for tag in new_tags:
            self.assertTrue(tag in ticket.tags)
        for tag in ticket.tags:
            self.assertTrue(tag in tags or tag in new_tags)

    def test_add_tags_invalid_name(self):
        r = Repository(self.root, create=True)

        name = "blectre"
        status = generators.gen_status()
        tags = generators.gen_tags()

        r.create_ticket(name, status, tags)

        new_tags = generators.gen_tags()
        self.assertRaises(PyticketException, r.add_tags, "cocorico", new_tags)

    @repeat(100)
    def test_remove_tags(self):
        r = Repository(self.root, create=True)

        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = None
        while not tags:
            tags = generators.gen_tags()

        r.create_ticket(name, status, tags)

        removed_tags = random.sample(tags, random.randrange(len(tags)))
        r.remove_tags(name, removed_tags)

        ticket = r.get_ticket(name)
        for tag in tags:
            if tag not in removed_tags:
                self.assertTrue(tag in ticket.tags)
            else:
                self.assertFalse(tag not in ticket.tags)

    def test_remove_tags_invalid_name(self):
        r = Repository(self.root, create=True)

        name = "blectre"
        status = generators.gen_status()
        tags = generators.gen_tags()

        r.create_ticket(name, status, tags)

        new_tags = generators.gen_tags()
        self.assertRaises(
            PyticketException, r.remove_tags, "cocorico", new_tags
        )

    def test_list(self):
        r = Repository(self.root, create=True)
        tickets, parents = RepositoryTest.generate_tickets(r, 500, 0.3)

        self.assertEqual(len(r.list_tickets()), len(tickets))

        # Testing status filter
        for status in MetaTicket.VALID_STATUS:
            listed = set(r.list_tickets(status=status))
            in_repo = set([t for t in list(r.tickets.values())
                          if t.status == status])
            self.assertEqual(listed, in_repo)

        # Testing tags filter
        for ticket in list(r.tickets.values()):
            listed = r.list_tickets(tags=ticket.tags)
            self.assertTrue(ticket in listed)

        # Testing root filter
        for parent in parents:
            listed = set([t.name for t in (r.list_tickets(root=parent))])
            self.assertEqual(
                set(parents[parent] + [parent]).intersection(listed), listed
            )

    def test_list_invalid_root(self):
        r = Repository(self.root, create=True)
        name = "blectre"
        status = generators.gen_status()
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)
        self.assertRaises(PyticketException, r.list_tickets, root="cocorico")

    def test_list_invalid_status(self):
        r = Repository(self.root, create=True)
        name = "blectre"
        status = generators.gen_status()
        tags = generators.gen_tags()
        r.create_ticket(name, status, tags)
        self.assertRaises(PyticketException, r.list_tickets, status="cocorico")

    def test_expand_template(self):
        r = Repository(self.root, create=True)
        r.expand_template("feature", {})

    def test_expand_template_invalid_name(self):
        r = Repository(self.root, create=True)
        self.assertRaises(PyticketException, r.expand_template, "blectre", {})

    def test_working_ticket(self):
        r = Repository(self.root, create=True)
        tickets, _ = RepositoryTest.generate_tickets(r, 100, 0.3)

        ticket = random.choice(tickets)
        self.assertFalse(r.is_working_ticket(ticket))
        self.assertEqual(r.get_working_ticket(), None)

        for ticket in tickets:
            r.get_ticket(ticket).status = "opened"
            r.set_working_ticket(ticket)
            self.assertTrue(r.is_working_ticket(ticket))
            self.assertEqual(r.get_working_ticket().name, ticket)

    def test_working_ticket_invalid_name(self):
        r = Repository(self.root, create=True)
        self.assertRaises(PyticketException, r.set_working_ticket, "blectre")


if __name__ == "__main__":
    unittest.main()
