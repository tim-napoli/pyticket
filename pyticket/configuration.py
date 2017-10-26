import json

from pyticket import PyticketException


class Configuration:
    """The pyticket's configuration class.

    :param values: if not ```None```, represents every configuration's values.
    :raises PyticketException: one of the value's name in ```values``` is not
                               allowed.
    """

    ALLOWED_KEYS = ["editor"]

    def __init__(self, values=None):
        if not values:
            values = {}
        for name, value in values.items():
            if name not in Configuration.ALLOWED_KEYS:
                raise PyticketException(
                    "'{}' is not a valid configuration key".format(name)
                )
        self.values = values

    def set_value(self, name, value):
        """Set a configuration value.

        :param name: the value's name.
        :param value: the value's value.
        :raises PyticketException: the value name is not an allowed one.
        """
        if name not in Configuration.ALLOWED_KEYS:
            raise PyticketException(
                "'{}' is not a valid configuration key".format(name)
            )
        self.values[name] = value

    def to_json(self):
        return self.values

    def save(self, directory):
        """Save the configuration as 'config.json' in the given directory.

        :param directory: the directory in which saving the configuration.
        """
        path = "{}/config.json".format(directory)
        with open(path, "w+") as f:
            f.write(json.dumps(self.to_json(), indent=4))

    def __eq__(self, other):
        return self.values == other.values

    @staticmethod
    def load(directory):
        """Load the 'config.json' from the given directory.

        :param directory: the directory from which loading the configuration.
        :raises PyticketException: the configuration file is invalid.
        """
        path = "{}/config.json".format(directory)
        with open(path, "r") as f:
            content = json.loads(f.read())
            return Configuration(content)
