import subprocess
import sys
import os
import time

import vmd

from pyticket import PyticketException
from pyticket import utils as utils
from pyticket.repository import Repository
from pyticket.configuration import Configuration


def create_ticket(options,
                  ticket_name: "The ticket name",
                  template: "The template to use" = None):
    tags = options["tags"].split(",") if "tags" in options else []
    r = Repository(".")
    r.create_ticket(ticket_name, "opened", tags)

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
    r.update_ticket_mtime(ticket_name)


def show_ticket(options, ticket_name: "The ticket name"):
    class parser_args:
        tab_spaces = 4
    r = Repository(".")

    if not r.has_ticket_content(ticket_name):
        raise PyticketException("'{}' has no content".format(ticket_name))

    ticket_content = r.read_ticket_content(ticket_name)

    parser = vmd.build_parser(parser_args)
    config = vmd.load_config()
    config.formatting.indent_paragraph_first_line = False
    config.formatting.align_content_with_headings = True
    writer = vmd.create_display_writer(sys.stdout)
    renderer = vmd.build_render(writer, config)
    doc = parser.parse(ticket_content)

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
        for ticket in sorted(tickets, key=lambda t: t.name):
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


def configure(options,
              what: "Which configuration key to configure",
              value: "Key value"):
    config = Configuration.load(utils.get_home_path())
    config.set_value(what, value)
    config.save(utils.get_home_path())


def init(options, directory: "The pyticket repository directory"):
    Repository(directory, create=True)


def table(options, ticket: "Show only this ticket tree" = None):
    HEADER = ["Ticket", "Status", "Last update", "Tags"]

    def get_terminal_width():
        width, height = os.popen("stty size", "r").read().split()
        return int(width)

    def get_row_cols_min_size(row):
        sizes = []
        for field in row:
            sizes.append(len(field) + 3)
        return sizes

    def get_table_cols_min_size(table):
        min_sizes = get_row_cols_min_size(table[0])
        for row in range(1, len(table)):
            sizes = get_row_cols_min_size(table[row])
            for col in range(0, len(sizes)):
                if sizes[col] > min_sizes[col]:
                    min_sizes[col] = sizes[col]
        return min_sizes

    def print_row(row, sizes):
        line = ""
        for i in range(0, len(row)):
            line += " {}".format(row[i]).ljust(sizes[i])
        print(line)

    def format_row(row):
        return [
            row[0], row[1],
            time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(row[2])),
            ", ".join(row[3])
        ]

    def format_table(table):
        formatted_table = [HEADER]
        for i in range(0, len(table)):
            formatted_table.append(format_row(table[i]))
        return formatted_table

    sorted_field = 2
    sorted_reverse = True
    if "sorted-name" in options:
        sorted_field = 0
        sorted_reverse = False

    count = int(options.get("count", -1))

    status = None
    if "opened" in options:
        status = "opened"
    elif "closed" in options:
        status = "closed"

    tags = []
    if "tags" in options:
        tags = options["tags"].split(",")

    r = Repository(".")

    table = [[t.name, t.status, t.mtime, t.tags]
             for t in r.list_tickets(ticket, status, tags)]

    table = sorted(table,
                   key=lambda row: row[sorted_field], reverse=sorted_reverse)
    if count > 0:
        table = table[:count]

    formatted_table = format_table(table)
    sizes = get_table_cols_min_size(formatted_table)
    print("-" * sum(sizes))
    print_row(formatted_table[0], sizes)
    print("-" * sum(sizes))
    for i in range(1, len(formatted_table)):
        print_row(formatted_table[i], sizes)
    print("-" * sum(sizes))


def add_tags(options, ticket: "The ticket to modify",
             tags: "The tags to add to the ticket"):
    r = Repository(".")
    r.add_tags(ticket, tags.split(","))


def remove_tags(options, ticket: "The ticket to modify",
                tags: "The tag to remove from the ticket"):
    r = Repository(".")
    r.remove_tags(ticket, tags.split(","))
