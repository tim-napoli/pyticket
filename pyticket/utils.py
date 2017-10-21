import json
import os
import os.path

from string import Template

def get_root_path(directory = "."):
    return "{}/.pyticket".format(directory)

def get_home_path():
    return os.path.expanduser("~/.pyticket")

def get_opened_tickets_path(directory = "."):
    return "{}/opened".format(get_root_path(directory))

def get_closed_tickets_path(directory = "."):
    return "{}/closed".format(get_root_path(directory))

def get_templates_path(directory = "."):
    return "{}/templates".format(get_root_path(directory))

class configuration:
    ALLOWED_VALUES = ["editor"]

    def __init__(self, values):
        self.values = values

    def set_value(self, name, value):
        if name not in configuration.ALLOWED_VALUES:
            raise ValueError(
                "'{}' is not a valid configuration key".format(name)
            )
        self.values[name] = value

    def to_json(self):
        return self.values

    def save(self, directory):
        path = "{}/config.json".format(directory)
        with open(path, "w+") as f:
            f.write(json.dumps(self.to_json(), indent=4))

    @staticmethod
    def load(directory):
        path = "{}/config.json".format(directory)
        with open(path, "r") as f:
            content = json.loads(f.read())
            return configuration(content)

def expand_template(template_name, values):
    path = "{}/{}".format(get_templates_path(), template_name)
    if not os.path.isfile(path):
        raise RuntimeError("Template '{}' doesn't exist".format(template_name))
    with open(path, 'r') as f:
        content = Template(f.read())
        return content.safe_substitute(**values)

def read_ticket(directory, ticket_name):
    path = "{}/{}/{}".format(get_root_path(), directory, ticket_name)
    with open(path, "r") as f:
        return f.read()

def read_opened_ticket(ticket_name):
    return read_ticket("opened", ticket_name)

def read_closed_ticket(ticket_name):
    return read_ticket("closed", ticket_name)

def list_tickets(directory):
    path = "{}/{}".format(get_root_path(), directory)
    tickets = os.listdir(path)
    return tickets

def get_ticket_tags(ticket_content):
    lines = ticket_content.splitlines()
    if not lines:
        return []
    tag_line = lines[-1]
    if tag_line.startswith("tags:"):
        return tag_line.split()[1:]
    return []

def find_ticket_directory(name):
    opened_tickets = list_tickets("opened")
    if name in opened_tickets:
        return "opened"
    closed_tickets = list_tickets("closed")
    if name in closed_tickets:
        return "closed"
    raise Exception("there is no ticket '{}'".format(name))
