import subprocess
import os.path

from pyticket.utils import (
    configuration, get_home_path, get_opened_tickets_path, expand_template
)

def create_ticket(argv,
                  ticket_name : "The ticket name",
                  template : "The template to use" = None):
    ticket_path = "{}/{}".format(get_opened_tickets_path(), ticket_name)
    if template:
        content = expand_template(template, {"ticket": ticket_name})
        with open(ticket_path, "w+") as f:
            f.write(content)
    config = configuration.load(get_home_path())
    subprocess.call([config.values["editor"], ticket_path])

def edit_ticket(argv, ticket_name : "The ticket name"):
    ticket_path = "{}/{}".format(get_opened_tickets_path(), ticket_name)
    if not os.path.isfile(ticket_path):
        raise RuntimeError("Ticket '{}' doesn't exist".format(ticket_name))
    config = configuration.load(get_home_path())
    subprocess.call([config.values["editor"], ticket_path])
