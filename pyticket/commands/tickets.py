import subprocess
import sys

import vmd

from pyticket import PyticketException
from pyticket import utils as utils
from pyticket.repository import Repository
from pyticket.configuration import Configuration


def create_ticket(options,
                  ticket_name: "The ticket name",
                  template: "The template to use" = None):
    r = Repository(".")
    r.create_ticket(ticket_name, "opened", [])

    if template:
        content = r.expand_template(template, {"ticket": ticket_name})
        r.write_ticket_content(ticket_name, content)

    if "no-edit" in options:
        if not template:
            open(r.get_ticket_content_path(ticket_name), "w+").close()
    else:
        config = Configuration.load(utils.get_home_path())
        subprocess.call([
            config.values["editor"],
            r.get_ticket_content_path(ticket_name)
        ])


def edit_ticket(argv, ticket_name: "The ticket name"):
    r = Repository(".")
    config = Configuration.load(utils.get_home_path())
    subprocess.call([
        config.values["editor"], r.get_ticket_content_path(ticket_name)
    ])


def show_ticket(options, ticket_name: "The ticket name"):
    class parser_args:
        tab_spaces = 4
    r = Repository(".")

    if not r.has_ticket_content(ticket_name):
        raise PyticketException("'{}' has no content".format(ticket_name))

    ticket_content = r.read_ticket_content(ticket_name)

    config = vmd.load_config()
    config.formatting.indent_paragraph_first_line = False
    config.formatting.align_content_with_headings = True
    writer = vmd.create_display_writer(sys.stdout)
    renderer = vmd.build_render(writer, config)
    doc = vmd.parser.parse(ticket_content)

    renderer.render_document(doc)
    print("")


def list_tickets(options,
                 ticket_name: "List given ticket and its childs" = None):
    def print_ticket(working, ticket):
        print("  {} {}".format("*" if working else " ", ticket.name))

    r = Repository(".")

    status = None
    if "opened" in options:
        status = "opened"
    if "closed" in options:
        status = "closed"

    tags = None
    if "tags" in options:
        tags = options["tags"].split(",")

    tickets = r.list_tickets(root=ticket_name, status=status, tags=tags)
    categories = (
        ("opened", [t for t in tickets if t.status == "opened"]),
        ("closed", [t for t in tickets if t.status == "closed"])
    )

    for (status, tickets) in categories:
        print(status + ":")
        for ticket in tickets:
            print_ticket(r.is_working_ticket(ticket.name), ticket)


def close_ticket(options, name: "The ticket name"):
    r = Repository(".")
    r.switch_ticket_status(name, "closed")


def reopen_ticket(options, name: "The ticket name"):
    r = Repository(".")
    r.switch_ticket_status(name, "opened")


def delete_ticket(options, name: "The ticket name"):
    force = "force" in options
    remove = True
    if not force:
        answer = input(
            ("Are you sure you want to supress '{}' and all its childs ? "
             "[Y/n] ").format(name)
        )
        remove = answer == "Y" or answer == "y" or answer == ""
    if remove:
        r = Repository(".")
        r.delete_ticket(name)


def rename_ticket(options, name: "The ticket name",
                  new_name: "The new ticket name"):
    r = Repository(".")
    r.rename_ticket(name, new_name)


def works_on(options, name: "The ticket to work on"):
    r = Repository(".")
    r.set_working_ticket(name)


def release(options):
    r = Repository(".")
    r.set_working_ticket(None)
