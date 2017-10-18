import json
import os.path

def get_root_path(directory = "."):
    return "{}/.pyticket".format(directory)

def get_home_path():
    return os.path.expanduser("~/.pyticket")

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

