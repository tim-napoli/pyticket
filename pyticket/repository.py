import os
import os.path

from pyticket import PyticketException
from pyticket import migrations
from pyticket import utils
from pyticket.configuration import Configuration
from pyticket.ticket import MetaTicket

DEFAULT_BUG_TEMPLATE = ("""# Bug $ticket

## Description

## Reproduction

## Solution

tags: bug
""")

DEFAULT_FEATURE_TEMPLATE = ("""# Feature $ticket

## Description

## Design

tags: feature
""")


class Repository:
    """Pyticket repository management.

    :param root: the directory on which instantiating the pyticket repository.
    :param create: if ```True``` the repository will be created, else, it will
                   be loaded.
    """
    def __init__(self, root=".", create=False):
        self.root = root
        self.repository = self.root + "/.pyticket"
        self.contents = self.repository + "/contents"
        self.templates = self.repository + "/templates"
        self.tickets = {}
        if create:
            self.init()
        else:
            if not os.path.isdir(self.repository):
                raise PyticketException(
                    "{} is not a pyticket repository".format(self.root)
                )
            migrations.apply_migrations(self.repository)
            tickets = Repository.read_tickets_file(
                    self.repository + "/tickets"
            )
            for ticket in tickets:
                self.tickets[ticket.name] = ticket

    @staticmethod
    def read_tickets_file(path):
        """Read every tickets meta-information form the given tickets
        repository file.

        :param path: the repository's tickets file path.
        :return: the list of every ```MetaTicket``` of the repository.
        """
        meta_tickets = []
        with open(path, "r") as f:
            content = f.read()
            lines = content.splitlines()
            for line in lines:
                meta_tickets.append(MetaTicket.parse(line))
        return meta_tickets

    def write_tickets_file(self):
        """Replace the content of the tickets file using the current tickets
        list.
        """
        with open(self.repository + "/tickets", "w+") as f:
            for name, ticket in self.tickets.items():
                f.write(ticket.to_string() + "\n")

    def init(self):
        """Initialize a new pyticket repository in the "root" directory."""
        if os.path.isdir(self.repository):
            raise PyticketException(
                "there already exists a pyticket repository at '{}'".format(
                    self.repository
                )
            )

        os.mkdir("{}/".format(self.repository))
        os.mkdir(self.contents)
        os.mkdir(self.templates)

        with open(self.templates + "/bug", "w+") as f:
            f.write(DEFAULT_BUG_TEMPLATE)
        with open(self.templates + "/feature", "w+") as f:
            f.write(DEFAULT_FEATURE_TEMPLATE)

        migrations.update_current_migration(self.repository)

        # Create working file.
        open("{}/working".format(self.repository), "w+").close()

        # Create tickets meta file.
        open("{}/tickets".format(self.repository), "w+").close()

        # Create default configuration file if needed.
        if not os.path.isdir(utils.get_home_path()):
            os.mkdir(utils.get_home_path())
            config = Configuration({
                "editor": "nano"
            })
            config.save(utils.get_home_path())

        print("Pyticket repository created in '{}'".format(self.repository))

    def has_ticket(self, name):
        """Check the repository has the given ticket."""
        return name in self.tickets

    def get_ticket(self, name):
        """Return the requested ticket.

        :param name: the ticket's name.
        :return: the requested ticket.
        :raises PyticketException: the repository doesn't contain the requested
                                   ticket.
        """
        if self.has_ticket(name):
            return self.tickets[name]
        raise PyticketException("ticket '{}' doesn't exist".format(name))

    def get_ticket_content_path(self, name):
        """Returns the full path of the of the given ticket's content.

        :params name: the ticket name.
        :return: the ticket content.
        :raises PyticketException: the given ticket doesn't exist.
        """
        if not self.has_ticket(name):
            raise PyticketException("ticket '{}' doesn't exist".format(name))
        return "{}/{}".format(self.contents, name)

    def has_ticket_content(self, name):
        """Returns true if the given ticket has a content file.

        :param name: the ticket name.
        :return: True if the ticket has a content file.
        :raises PyticketException: the givent ticket doesn't exist.
        """
        path = self.get_ticket_content_path(name)
        return os.path.isfile(path)

    def create_ticket(self, name, status, tags, create=False):
        """Create a new ticket in the repository.

        :param name: the ticket name. This name can have some '.' to inform of
                     the ticket hierarchy.
        :param status: the ticket status.
        :param tags: the ticket tags.
        :param create: if ```True```, create the given ticket content file.
        :raises PyticketException: the ticket cannot be created for one of the
                                   following reasons:
                                   - a ticket already has the given name ;
                                   - the name is invalid ;
                                   - the status is invalid ;
                                   - the ticket's parent (contained in the
                                     name) doesn't exist ;
                                   - a given tag name is invalid.

        :Exemple:
        >>> r = Repository()
        >>> r.create_ticket("root", "opened")
        >>> # Create a root's child:
        >>> r.create_ticket("root.child", "opened", ["some-tag"])
        >>> # Will fail because "missing-root" doesn't exist:
        >>> r.create_ticket("missing-root.child", "opened")
        >>> # Create the ticket content file:
        >>> r.create_ticket("with-content", "opened", [], create=True)
        """
        if not MetaTicket.is_valid_name(name):
            raise PyticketException(
                "'{}' is not a valid ticket name".format(name)
            )

        if self.has_ticket(name):
            raise PyticketException("ticket '{}' already exists".format(name))

        parent_name = utils.get_ticket_parent_name(name)
        if parent_name and not self.has_ticket(parent_name):
            raise PyticketException(
                "parent ticket '{}' doesn't exist".format(parent_name)
            )

        if not MetaTicket.is_valid_status(status):
            raise PyticketException(
                "'{}' is not a valid status".format(status)
            )

        for tag in tags:
            if not MetaTicket.is_valid_tag_name(tag):
                raise PyticketException(
                    "'{}' is not a valid tag name".format(tag)
                )

        meta_ticket = MetaTicket(name, status, tags)
        self.tickets[meta_ticket.name] = meta_ticket
        self.write_tickets_file()

        if create:
            open(self.get_ticket_content_path(name), "w+").close()

    def write_ticket_content(self, name, content):
        """Write the ticket content file for the given ticket.

        :param name: the ticket name.
        :param content: the ticket content.
        :raises PyticketException: the ticket 'name' doesn't exist.
        """
        path = self.get_ticket_content_path(name)
        with open(path, "w+") as f:
            f.write(content)

    def read_ticket_content(self, name):
        """Read the ticket content of the given ticket.

        :param name: the ticket name.
        :return: the ticket content.
        :raises PyticketException: the ticket doesn't exist or has no content.
        """
        if not self.has_ticket_content(name):
            raise PyticketException(
                "ticket '{}' has no content".format(name)
            )
        path = self.get_ticket_content_path(name)
        with open(path, "r") as f:
            return f.read()

    def switch_ticket_status(self, name, status):
        """Switch the status of the given ticket.

        This is dumb since status is now a meta-data. We don't need more
        than one content folder.

        :param name: the ticket name.
        :param status: the new status of the ticket.
        :raises PyticketException: if the ticket doesn't exist or ```status```
                                   is invalid.
        """
        if status not in MetaTicket.VALID_STATUS:
            raise PyticketException(
                "'{}' is not a valid status".format(status)
            )
        ticket = self.get_ticket(name)
        ticket.status = status
        self.write_tickets_file()
