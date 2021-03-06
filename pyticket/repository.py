import json
import os
import os.path
import shutil
import time
from string import Template

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
        with open(path, "r") as f:
            json_data = json.loads(f.read())
            return [MetaTicket.from_json(node) for node in json_data]

    def write_tickets_file(self):
        """Replace the content of the tickets file using the current tickets
        list.
        """
        with open(self.repository + "/tickets", "w+") as f:
            json_data = [t.to_json() for t in self.tickets.values()]
            f.write(json.dumps(json_data))

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

    def get_ticket_childs(self, name, recursive=False):
        """Returns every childs of the given ticket.

        :param name: the ticket name.
        :param recursive: if ```True```, returns every descendants of this
                          ticket, and not only direct childs.
        :return: the ticket childs.
        """
        childs = []
        for candidate_key, candidate in self.tickets.items():
            candidate_parent_name = utils.get_ticket_parent_name(candidate_key)
            if candidate_parent_name and candidate_parent_name == name:
                childs.append(candidate)
                if recursive:
                    childs += self.get_ticket_childs(candidate_key, recursive)
        return childs

    def set_working_ticket(self, name):
        """Set the given ticket as the working ticket.

        :param name: the ticket name to set as working one.
        :raises PyticketException: the given ticket doesn't exist or it is
                                   closed.
        """
        if name:
            if not self.has_ticket(name):
                raise PyticketException(
                    "ticket '{}' doesn't exist".format(name)
                )

            ticket = self.get_ticket(name)
            if ticket.status == "closed":
                raise PyticketException("'{}' is a closed ticket".format(name))
        else:
            name = ""

        with open(self.repository + "/working", "w+") as f:
            f.write(name)

    def is_working_ticket(self, name):
        """Check if the given ticket is the working ticket.

        :param name: the ticket name to check.
        :return: return ```True``` if the given ticket is the working ticket.
        """
        with open(self.repository + "/working", "r") as f:
            content = f.read()
            return content == name

    def get_working_ticket(self):
        """Get the current working ticket.

        :return: The current working ticket or None if this ticket doesn't
                 exist.
        """
        with open(self.repository + "/working", "r") as f:
            content = f.read()
            if not content:
                return None
            return self.tickets[content]

    def update_ticket_mtime(self, name):
        """Update the mtime of the given ticket to the current time.

        :param name: the ticket name.
        :raises PyticketException: the ticket doesn't exist.
        """
        ticket = self.get_ticket(name)
        ticket.mtime = time.time()
        self.write_tickets_file()

    def create_ticket(self, name, status, tags, create=False):
        """Create a new ticket in the repository.

        :param name: the ticket name. This name can have some '.' to inform of
                     the ticket hierarchy.
        :param status: the ticket status.
        :param tags: the ticket tags.
        :param create: if ```True```, create the given ticket content file.
        :return: The created MetaTicket.
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

        meta_ticket = MetaTicket(name, status, tags, time.time())
        self.tickets[meta_ticket.name] = meta_ticket
        self.write_tickets_file()

        if create:
            open(self.get_ticket_content_path(name), "w+").close()

        return meta_ticket

    def write_ticket_content(self, name, content):
        """Write the ticket content file for the given ticket.

        :param name: the ticket name.
        :param content: the ticket content.
        :raises PyticketException: the ticket 'name' doesn't exist.
        """
        path = self.get_ticket_content_path(name)
        with open(path, "w+") as f:
            f.write(content)
        self.update_ticket_mtime(name)

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

        If reopening a closed ticket, every of its parents will be reopened
        too.

        If closing the working ticket, this ticket will no more be the
        working ticket.

        :param name: the ticket name.
        :param status: the new status of the ticket.
        :raises PyticketException: if the ticket doesn't exist or ```status```
                                   is invalid or if we try to close a ticket
                                   that has opened childs.
        """
        if status not in MetaTicket.VALID_STATUS:
            raise PyticketException(
                "'{}' is not a valid status".format(status)
            )

        if status == "closed":
            childs = self.get_ticket_childs(name, recursive=True)
            for child in childs:
                if child.status == "opened":
                    raise PyticketException(
                        "trying to close '{}', but its child '{}' is opened"
                        .format(name, child.name)
                    )
            if self.is_working_ticket(name):
                self.set_working_ticket(None)

        ticket = self.get_ticket(name)
        if status == "opened" and ticket.status == "closed":
            parent_name = utils.get_ticket_parent_name(name)
            while parent_name:
                parent = self.get_ticket(parent_name)
                parent.status = "opened"
                parent_name = utils.get_ticket_parent_name(parent_name)
        ticket.status = status
        self.write_tickets_file()
        self.update_ticket_mtime(name)

    def rename_ticket(self, name, new_name):
        """Rename a ticket.

        If the ticket has a content, also rename its content file.

        If the ticket has childs, also rename its childs.

        :param name: the name of the ticket to rename.
        :param new_name: the new ticket name.
        :raises PyticketException: if the given ticket cannot be found, if
                                   the new ticket's name is invalid, or if the
                                   new ticket's requested parent doesn't exist.
        """
        if not MetaTicket.is_valid_name(new_name):
            raise PyticketException(
                "'{}' is not a valid ticket name".format(new_name)
            )
        if self.has_ticket(new_name):
            raise PyticketException(
                "ticket '{}' already exists".format(new_name)
            )
        parent_name = utils.get_ticket_parent_name(new_name)
        if parent_name and not self.has_ticket(parent_name):
            raise PyticketException(
                ("requests new parent '{}' for ticket '{}', but this parent "
                 "doesn't exist (new name is '{}')").format(parent_name, name,
                                                            new_name)
            )

        has_content = self.has_ticket_content(name)
        if has_content:
            previous_content_path = self.get_ticket_content_path(name)

        # Rename the ticket
        ticket = self.get_ticket(name)
        ticket.name = new_name
        self.tickets[new_name] = self.tickets.pop(name)

        # Rename the content
        if has_content:
            new_content_path = self.get_ticket_content_path(new_name)
            shutil.move(previous_content_path, new_content_path)

        # Rename childs
        childs = self.get_ticket_childs(name)
        for child in childs:
            child_basename = utils.get_ticket_basename(child.name)
            child_new_name = new_name + '.' + child_basename
            self.rename_ticket(child.name, child_new_name)

        # Update working ticket
        if self.is_working_ticket(name):
            self.set_working_ticket(new_name)

        # Update tickets file
        self.write_tickets_file()
        self.update_ticket_mtime(new_name)

    def delete_ticket(self, name):
        """Delete the given ticket and its childs.

        :param name: the name of the ticket to delete.
        :raises PyticketException: the requested ticket doesn't exist.
        """
        if not self.has_ticket(name):
            raise PyticketException("ticket '{}' doesn't exist".format(name))

        # Delete childs
        childs = self.get_ticket_childs(name)
        for child in childs:
            self.delete_ticket(child.name)

        # Delete ticket content
        if self.has_ticket_content(name):
            os.remove(self.get_ticket_content_path(name))

        # Remove the ticket from the list
        self.tickets.pop(name)

        # Reset working ticket
        if self.is_working_ticket(name):
            self.set_working_ticket(None)

        # Write list.
        self.write_tickets_file()

    def add_tags(self, name, tags):
        """Add tags to the given ticket.

        :param name: the ticket name to which adding tags.
        :param tags: tags to add to the ticket.
        :raise PyticketException: the given ticket doesn't exist.
        """
        ticket = self.get_ticket(name)
        for tag in tags:
            if tag not in ticket.tags:
                ticket.tags.append(tag)
        self.write_tickets_file()
        self.update_ticket_mtime(name)

    def remove_tags(self, name, tags):
        """Remove tags from the given ticket.

        :param name: the ticket name to which removing tags.
        :param tags: the tags to remove.
        :raise PyticketException: the given ticket doesn't exist.
        """
        ticket = self.get_ticket(name)
        for tag in tags:
            if tag in ticket.tags:
                ticket.tags.remove(tag)
        self.write_tickets_file()
        self.update_ticket_mtime(name)

    def list_tickets(self, root=None, status=None, tags=None):
        """List tickets using filters.

        :param root: if given, list the given 'root' ticket and all of its
                     childs.
        :param status: if given, list only tickets with this status.
        :param tags: filter tickets having given tags.
        :return: the list of tickets matching filters.
        :raises PyticketException: the 'root' ticket doesn't exist or 'status'
                                   is invalid.
        """
        if root and not self.has_ticket(root):
            raise PyticketException(
                "ticket '{}' doesn't exist".format(root)
            )
        if status and not MetaTicket.is_valid_status(status):
            raise PyticketException(
                "'{}' is an invalid status".format(status)
            )

        tickets = (list(self.tickets.values()) if not root
                   else self.get_ticket_childs(root, recursive=True))
        if root:
            tickets.append(self.get_ticket(root))

        if status:
            tickets = [t for t in tickets if t.status == status]
        if tags:
            tickets = [t for t in tickets if not set(tags) - set(t.tags)]
        return tickets

    def expand_template(self, template_name, values):
        """Expand the given template with the given values.

        :param template_name: the name of the template to expand.
        :param values: values used to expand the template.
        :return: the expanded template.
        """
        path = "{}/{}".format(self.templates, template_name)
        if not os.path.isfile(path):
            raise PyticketException(
                "template '{}' doesn't exist".format(template_name)
            )
        with open(path, 'r') as f:
            content = Template(f.read())
            return content.safe_substitute(**values)
