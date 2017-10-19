import subprocess

from pyticket.utils import (
    configuration, get_home_path, get_opened_tickets_path
)

def create_ticket(argv, ticket_name : "The ticket name"):
    config = configuration.load(get_home_path())
    ticket_path = "{}/{}".format(get_opened_tickets_path(), ticket_name)
    subprocess.call([config.values["editor"], ticket_path])
