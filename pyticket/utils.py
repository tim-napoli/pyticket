import json
import os.path

def get_root_path(directory = "."):
    return "{}/.pyticket".format(directory)

def get_home_path():
    return os.path.expanduser("~/.pyticket")

