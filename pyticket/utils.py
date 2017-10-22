import json
import os
import os.path

from string import Template
from pyticket import PyticketException

def get_root_path(directory = "."):
    """Returns the pyticket path of the given directory."""
    return "{}/.pyticket".format(directory)

def get_home_path():
    """Returns the user's home pyticket directory."""
    return os.path.expanduser("~/.pyticket")

def get_opened_tickets_path(directory = "."):
    return "{}/opened".format(get_root_path(directory))

def get_closed_tickets_path(directory = "."):
    return "{}/closed".format(get_root_path(directory))

def get_templates_path(directory = "."):
    return "{}/templates".format(get_root_path(directory))

class configuration:
    """The pyticket's configuration class."""
    ALLOWED_VALUES = ["editor"]

    def __init__(self, values):
        self.values = values

    def set_value(self, name, value):
        if name not in configuration.ALLOWED_VALUES:
            raise PyticketException(
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
    """Expand a template file using the given values dictionary."""
    path = "{}/{}".format(get_templates_path(), template_name)
    if not os.path.isfile(path):
        raise PyticketException(
            "template '{}' doesn't exist".format(template_name)
        )
    with open(path, 'r') as f:
        content = Template(f.read())
        return content.safe_substitute(**values)

def read_ticket(directory, ticket_name):
    """Returns the ticket content."""
    path = "{}/{}/{}".format(get_root_path(), directory, ticket_name)
    with open(path, "r") as f:
        return f.read()

def read_opened_ticket(ticket_name):
    return read_ticket("opened", ticket_name)

def read_closed_ticket(ticket_name):
    return read_ticket("closed", ticket_name)

def list_tickets(directory):
    """List every tickets of the given directory."""
    path = "{}/{}".format(get_root_path(), directory)
    tickets = os.listdir(path)
    return tickets

def get_ticket_tags(ticket_content):
    """Returns tickets tags."""
    lines = ticket_content.splitlines()
    if not lines:
        return []
    tag_line = lines[-1]
    if tag_line.startswith("tags:"):
        return tag_line.split()[1:]
    return []

def find_ticket_directory(name):
    """Find what is the ticket's directory."""
    opened_tickets = list_tickets("opened")
    if name in opened_tickets:
        return "opened"
    closed_tickets = list_tickets("closed")
    if name in closed_tickets:
        return "closed"
    raise PyticketException("there is no ticket '{}'".format(name))

def get_ticket_parent(name):
    """Returns the ticket's parent name."""
    path = name.split(".")
    if len(path) > 1:
        return ".".join(path[0:-1])
    return None

def is_ticket(name):
    """Checks the given ticket exist."""
    opened_tickets = list_tickets("opened")
    closed_tickets = list_tickets("closed")
    if name in opened_tickets or name in closed_tickets:
        return True
    return False

def is_child_of(child, parent):
    """Checks 'child' is a child of 'parent'."""
    if child.startswith(parent + "."):
        split_child = child.split(".")
        split_parent = parent.split(".")
        return len(split_child) > len(split_parent)
    return False

def find_tickets_childs(directory, name):
    """Find every tickets direct childs."""
    childs = []
    tickets = list_tickets(directory)
    for ticket in tickets:
        if is_child_of(ticket, name):
            childs.append(ticket)
    return childs

def find_tickets_childs_deep(directory, name):
    """Find every tickets childs and 'sub-childs'."""
    childs = find_tickets_childs(directory, name)
    deep = []
    for child in childs:
        deep += find_tickets_childs_deep(directory, child)
    return childs + deep

def is_closed_ticket(name):
    """Check the given ticket is closed."""
    return name in list_tickets("closed")

def write_ticket(directory, name, new_content):
    """Write the given ticket content."""
    path = "{}/{}/{}".format(get_root_path(), directory, name)
    with open(path, "w+") as f:
        f.write(new_content)

def is_pyticket_repository(directory = "."):
    return os.path.isdir(directory + "/.pyticket/")
