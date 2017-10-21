import sys
import shutil
import subprocess
import os.path

from vmd import build_render, create_display_writer, load_config, build_parser

from pyticket.utils import (
    configuration, get_home_path, get_opened_tickets_path, expand_template,
    read_opened_ticket, read_ticket, list_tickets, get_ticket_tags,
    get_closed_tickets_path, find_ticket_directory, get_root_path
)

def create_ticket(options,
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

def show_ticket(options, ticket_name : "The ticket name"):
    class parser_args:
        tab_spaces = 4

    directory = find_ticket_directory(ticket_name)
    ticket_content = read_ticket(directory, ticket_name)

    parser = build_parser(parser_args)
    config = load_config()
    config.formatting.indent_paragraph_first_line = False
    config.formatting.align_content_with_headings = True
    writer = create_display_writer(sys.stdout)
    renderer = build_render(writer, config)
    doc = parser.parse(ticket_content)

    renderer.render_document(doc)
    print("")

def list_tickets_command(options):
    def show_list_tickets(directory, tickets, tags):
        for ticket in tickets:
            ticket_content = read_ticket(directory, ticket)
            show_ticket = True
            if tags:
                ticket_tags = get_ticket_tags(ticket_content)
                inter = list(set(tags).intersection(ticket_tags))
                show_ticket = len(inter) == len(tags)
            if show_ticket:
                print("    {}".format(ticket))

    tickets_from = ["opened", "closed"]
    if "opened" in options:
        tickets_from = ["opened"]
    if "closed" in options:
        tickets_from = ["closed"]
    tags = []
    if "tags" in options:
        tags = options["tags"].split(",")

    for directory in tickets_from:
        print(directory + ":")
        show_list_tickets(directory, list_tickets(directory), tags)

def close_ticket(options, name : "The ticket name"):
    open_path = get_opened_tickets_path() + "/" + name
    close_path = get_closed_tickets_path() + "/" + name
    shutil.move(open_path, close_path)

def reopen_ticket(options, name : "The ticket name"):
    open_path = get_opened_tickets_path() + "/" + name
    close_path = get_closed_tickets_path() + "/" + name
    shutil.move(close_path, open_path)

def delete_ticket(options, name : "The ticket name"):
    force = "force" in options
    directory = find_ticket_directory(name)
    if not force:
        answer = input(
            "Are you sure you want to supress '{}' ? [Y/n] ".format(name)
        )
        if answer == "Y" or answer == "y" or answer == "":
            os.remove("{}/{}/{}".format(get_root_path(), directory, name))
    else:
        os.remove("{}/{}/{}".format(get_root_path(), directory, name))
