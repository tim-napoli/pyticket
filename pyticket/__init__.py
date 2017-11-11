import os


class PyticketException(Exception):
    pass


_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_extra(path):
    """Returns the path of an extra file."""
    return os.path.join(_ROOT, "extras", path)
