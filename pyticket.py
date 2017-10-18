#!/usr/bin/env python3
"""
PyTicket main program.
"""
import sys
from pyticket.command import command, argument, print_usage, execute_argv
from pyticket.commands.init import init
from pyticket.commands.configure import configure

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
