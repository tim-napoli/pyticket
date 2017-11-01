#!/usr/bin/env python3
"""
PyTicket main program.
"""
import sys
from pyticket import PyticketException
from pyticket import utils as utils
from pyticket import migrations as migrations
from pyticket.command import (
    command, argument, print_usage, execute_argv, option
)
from pyticket import commands as commands

COMMANDS = [
    command(
        "init",
        "Initialize a pyticket repository",
        commands.init
    ),
    command(
        "configure",
        "Configure the pyticket repository",
        commands.configure
    ),
    command(
        "create",
        "Create a new ticket",
        commands.create_ticket,
        [ option("no-edit", "don't edit the created ticket", False) ]
    ),
    command(
        "edit",
        "Edit an existing ticket",
        commands.edit_ticket
    ),
    command(
        "delete",
        "Delete an existing ticket",
        commands.delete_ticket,
        [ option("force", "don't ask for confirmation", False) ]
    ),
    command(
        "rename",
        "Rename a ticket",
        commands.rename_ticket
    ),
    command(
        "close",
        "Close an opened ticket",
        commands.close_ticket
    ),
    command(
        "reopen",
        "Reopen a closed ticket",
        commands.reopen_ticket
    ),
    command(
        "show",
        "Show an existing ticket",
        commands.show_ticket
    ),
    command(
        "list",
        "List tickets using criteria",
        commands.list_tickets,
        [ option("opened", "only list opened tickets", False)
        , option("closed", "only list closed tickets", False)
        , option("tags",
                 ( "list tickets having the given tags (separated by a comma)."
                   " Listed tickets must have every given tags."),
                 True)
        ]
    ),
    command(
        "add-tag",
        "Add a tag to the given ticket",
        commands.add_tag
    ),
    command(
        "remove-tag",
        "Remove a tag from the given ticket",
        commands.remove_tag
    ),
    command(
        "works-on",
        "Set the current working ticket",
        commands.works_on
    ),
    command(
        "release",
        "Release the working ticket",
        commands.release
    ),
    command(
        "table",
        "Show tickets in a table",
        commands.table,
        [ option("sorted-name", "Sort the table with ticket names", False),
          option("count", "Number of tickets to show", True),
          option("opened", "Show opened tickets", False),
          option("closed", "Show closed tickets", False),
          option("tags", "Filter using given tags", True)
        ]
    )
]

def help_(options, command : "Print the help of the given command" = None):
    if command:
        for cmd in COMMANDS:
            if cmd.name == command:
                cmd.usage()
                return
        raise PyticketException("command '{}' doesn't exist".format(command))
    else:
        print_usage("pyticket", COMMANDS)

def main(args=[]):
    COMMANDS.insert(0, command("help", "Show this help", help_))

    if not args:
        print_usage("pyticket", COMMANDS)
        sys.exit(0)


    extern_commands = ["init", "configure"]
    cmd = args[0]
    if cmd not in extern_commands and not utils.is_pyticket_repository():
        print('pyticket: current directory is not a pyticket repository.')
        sys.exit(1)

    try:
        execute_argv(COMMANDS, args)
    except PyticketException as ex:
        print('pyticket: ' + str(ex))
        sys.exit(1)

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
