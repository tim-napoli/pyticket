#!/usr/bin/env python3
"""
PyTicket main program.
"""
import sys
from pyticket.command import (
    command, argument, print_usage, execute_argv, option
)
from pyticket.commands.init import init
from pyticket.commands.configure import configure
from pyticket.commands.tickets import (
    create_ticket, edit_ticket, show_ticket, list_tickets_command,
    close_ticket, reopen_ticket, delete_ticket, rename_ticket
)

COMMANDS = [
    command(
        "init",
        "Initialize a pyticket repository",
        init
    ),
    command(
        "configure",
        "Configure the pyticket repository",
        configure
    ),
    command(
        "create",
        "Create a new ticket",
        create_ticket
    ),
    command(
        "edit",
        "Edit an existing ticket",
        edit_ticket
    ),
    command(
        "delete",
        "Delete an existing ticket",
        delete_ticket,
        [ option("force", "don't ask for confirmation", False) ]
    ),
    command(
        "rename",
        "Rename a ticket",
        rename_ticket
    ),
    command(
        "close",
        "Close an opened ticket",
        close_ticket
    ),
    command(
        "reopen",
        "Reopen a closed ticket",
        reopen_ticket
    ),
    command(
        "show",
        "Show an existing ticket",
        show_ticket
    ),
    command(
        "list",
        "List tickets using criteria",
        list_tickets_command,
        [ option("opened", "only list opened tickets", False)
        , option("closed", "only list closed tickets", False)
        , option("tags",
                 ( "list tickets having the given tags (separated by a comma)."
                   " Listed tickets must have every given tags."),
                 True)
        ]
    )
]

def main():
    args = sys.argv[1:]

    if not args:
        print_usage(sys.argv[0], COMMANDS)
        sys.exit(0)

    execute_argv(COMMANDS, args)

if __name__ == '__main__':
    main()
