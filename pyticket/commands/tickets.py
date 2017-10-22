import sys
import shutil
import subprocess
import os.path

from vmd import build_render, create_display_writer, load_config, build_parser

from pyticket import PyticketException
from pyticket import utils as utils

def create_ticket(options,
                  ticket_name : "The ticket name",
                  template : "The template to use" = None):
    if utils.is_ticket(ticket_name):
        raise PyticketException(
            "ticket '{}' already exist.".format(ticket_name)
        )
    parent = utils.get_ticket_parent(ticket_name)
    if parent and not utils.is_ticket(parent):
        raise PyticketException(
            "ticket's parent '{}' doesn't exist".format(parent)
        )

    ticket_path = "{}/{}".format(utils.get_opened_tickets_path(), ticket_name)
    if template:
        content = utils.expand_template(template, {"ticket": ticket_name})
        with open(ticket_path, "w+") as f:
            f.write(content)

    if "no-edit" in options:
        if not template:
            open(ticket_path, "w+").close()
    else:
        config = utils.configuration.load(utils.get_home_path())
        subprocess.call([config.values["editor"], ticket_path])

def edit_ticket(argv, ticket_name : "The ticket name"):
    directory = utils.find_ticket_directory(ticket_name)
    ticket_path = "{}/{}/{}".format(utils.get_root_path(), directory,
                                    ticket_name)
    if not os.path.isfile(ticket_path):
        raise PyticketException(
            "ticket '{}' doesn't exist".format(ticket_name)
        )
    config = utils.configuration.load(utils.get_home_path())
    subprocess.call([config.values["editor"], ticket_path])

def show_ticket(options, ticket_name : "The ticket name"):
    class parser_args:
        tab_spaces = 4

    directory = utils.find_ticket_directory(ticket_name)
    ticket_content = utils.read_ticket(directory, ticket_name)

    parser = build_parser(parser_args)
    config = load_config()
    config.formatting.indent_paragraph_first_line = False
    config.formatting.align_content_with_headings = True
    writer = create_display_writer(sys.stdout)
    renderer = build_render(writer, config)
    doc = parser.parse(ticket_content)

    renderer.render_document(doc)
    print("")

def list_tickets_command(options,
                     ticket_name : "List given ticket and its childs" = None):
    def show_list_tickets(directory, tickets, tags):
        working_ticket = utils.get_working_ticket()
        indentations = {}
        tickets.sort()
        for ticket in tickets:
            if (ticket_name and not ticket == ticket_name and
                    not utils.is_child_of(ticket, ticket_name)):
                continue
            ticket_content = utils.read_ticket(directory, ticket)
            show_ticket = True
            ticket_tags = utils.get_ticket_tags(ticket_content)
            if tags:
                inter = list(set(tags).intersection(ticket_tags))
                show_ticket = len(inter) == len(tags)

            if not show_ticket:
                continue

            parent = utils.get_ticket_parent(ticket)
            if parent and parent in indentations:
                indentations[ticket] = indentations[parent] + 2
            else:
                indentations[ticket] = 0

            print("  {} {}{} ({})".format(
                " " if not ticket == working_ticket else "*",
                " " * indentations[ticket] ,ticket, ", ".join(ticket_tags)
            ))

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
        show_list_tickets(directory, utils.list_tickets(directory), tags)

def close_ticket(options, name : "The ticket name"):
    childs = utils.find_tickets_childs_deep("opened", name)
    if childs:
        raise PyticketException(
            "cannot close '{}', it has opened childs ({})".format(
                name, ", ".join(childs)
            )
    )

    working_ticket = utils.get_working_ticket()
    if name == working_ticket:
        release(name)

    open_path = utils.get_opened_tickets_path() + "/" + name
    close_path = utils.get_closed_tickets_path() + "/" + name
    shutil.move(open_path, close_path)

def reopen_ticket(options, name : "The ticket name"):
    parent = utils.get_ticket_parent(name)
    if utils.is_closed_ticket(parent):
        reopen_ticket(options, parent)
    open_path = utils.get_opened_tickets_path() + "/" + name
    close_path = utils.get_closed_tickets_path() + "/" + name
    shutil.move(close_path, open_path)

def delete_ticket(options, name : "The ticket name"):
    force = "force" in options
    directory = utils.find_ticket_directory(name)
    remove = True
    if not force:
        answer = input(
            ("Are you sure you want to supress '{}' and all its childs ? "
             "[Y/n] ").format(name)
        )
        remove = answer == "Y" or answer == "y" or answer == ""
    if remove:
        childs = (  utils.find_tickets_childs("opened", name)
                  + utils.find_tickets_childs("closed", name))
        for child in childs:
            delete_ticket({"force": None}, child)
        os.remove("{}/{}/{}".format(utils.get_root_path(), directory, name))

def rename_ticket(options, name : "The ticket name",
                  new_name : "The new ticket name"):
    childs = (  utils.find_tickets_childs("opened", name)
              + utils.find_tickets_childs("closed", name))
    for child in childs:
        child_split = child.split(".")
        child_new_name = new_name + "." + child_split[-1]
        rename_ticket(options, child, child_new_name)

    directory = utils.find_ticket_directory(name)
    src_path = "{}/{}/{}".format(utils.get_root_path(), directory, name)
    dst_path = "{}/{}/{}".format(utils.get_root_path(), directory, new_name)
    shutil.move(src_path, dst_path)

def works_on(options, name : "The ticket to work on"):
    directory = utils.find_ticket_directory(name)
    if directory == "closed":
        raise PyticketException("ticket '{}' is closed.".format(name))
    utils.set_working_ticket(name)

def release(options):
    utils.set_working_ticket("")
