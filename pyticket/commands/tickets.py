import subprocess
import os.path

from pyticket.utils import (
    configuration, get_home_path, get_opened_tickets_path
)

def create_ticket(argv, ticket_name : "The ticket name"):
    config = configuration.load(get_home_path())
    ticket_path = "{}/{}".format(get_opened_tickets_path(), ticket_name)
    subprocess.call([config.values["editor"], ticket_path])

def edit_ticket(argv, ticket_name : "The ticket name"):
    ticket_path = "{}/{}".format(get_opened_tickets_path(), ticket_name)
    if not os.path.isfile(ticket_path):
        raise RuntimeError("Ticket '{}' doesn't exist".format(ticket_name))
    config = configuration.load(get_home_path())
    subprocess.call([config.values["editor"], ticket_path])
