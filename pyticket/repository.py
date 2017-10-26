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
        self.tickets = []
        if create:
            self.init()
        else:
            if not os.path.isdir(self.repository):
                raise PyticketException(
                    "{} is not a pyticket repository".format(self.root)
                )
            migrations.apply_migrations(self.repository)
            self.tickets = Repository.read_tickets_file(
                    self.repository + "/tickets"
            )

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

    def init(self):
        """Initialize a new pyticket repository in the "root" directory."""
        if os.path.isdir(self.repository):
            raise PyticketException(
                "there already exists a pyticket repository in '{}'".format(
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
