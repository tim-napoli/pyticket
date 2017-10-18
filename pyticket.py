#!/usr/bin/env python3
"""
PyTicket main program.
"""
import sys
from pyticket.command import command, argument, print_usage, execute_argv
from pyticket.commands.init import init

COMMANDS = [
    command(
        "init",
        "Initialize a pyticket repository",
        init
    )
]

def main():
    args = sys.argv[1:]

    if not args:
        print_usage(sys.argv[0], COMMANDS)
        sys.exit(0)

    try:
        execute_argv(COMMANDS, args)
    except Exception as ex:
        print("error: {}".format(str(ex)))
        sys.exit(1)

if __name__ == '__main__':
    main()
