import sys
import subprocess
import os.path

from vmd import build_render, create_display_writer, load_config, build_parser

from pyticket.utils import (
    configuration, get_home_path, get_opened_tickets_path, expand_template,
    read_opened_ticket
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

    ticket_content = read_opened_ticket(ticket_name)

    parser = build_parser(parser_args)
    config = load_config()
    config.formatting.indent_paragraph_first_line = False
    config.formatting.align_content_with_headings = True
    writer = create_display_writer(sys.stdout)
    renderer = build_render(writer, config)
    doc = parser.parse(ticket_content)

    renderer.render_document(doc)
    print("")
