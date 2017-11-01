import os
import os.path


def get_home_path():
    """Returns the user's home pyticket directory."""
    return os.path.expanduser("~/.pyticket")


def get_ticket_parent_name(name):
    """Returns the ticket's parent name.

    :return: if the name doesn't contain any '.', returns None, else returns
             the ticket's parent's name.
    """
    path = name.split(".")
    if len(path) > 1:
        return ".".join(path[0:-1])
    return None


def get_ticket_basename(name):
    """Returns the basename (the name of the ticket minus the name of its
    parent) of the given ticket name.

    :param name: the ticket name.
    :return: the ticket's basename.
    """
    parent_name = get_ticket_parent_name(name)
    if parent_name:
        return name[len(parent_name)+1:]
    return name
