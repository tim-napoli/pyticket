import unittest
import random

from pyticket import PyticketException
from pyticket.configuration import Configuration

from tests import generators
from tests.utils import repeat


class ConfigurationTest(unittest.TestCase):

    @repeat(1000)
    def test_invalid_new(self):
        name = generators.gen_string(1, 1000)
        if name in Configuration.ALLOWED_KEYS:
            return
        self.assertRaises(PyticketException, Configuration, {name: ""})

    @repeat(1000)
    def test_set_value(self):
        conf = Configuration()
        name = random.choice(Configuration.ALLOWED_KEYS)
        conf.set_value(name, "")

    @repeat(1000)
    def test_set_value_invalid(self):
        conf = Configuration()
        name = generators.gen_string(1, 1000)
        if name in Configuration.ALLOWED_KEYS:
            return
        self.assertRaises(PyticketException, conf.set_value, name, "")

    @repeat(1000)
    def test_save_load(self):
        conf = Configuration(generators.gen_configuration_values())
        conf.save("/tmp")
        loaded_conf = Configuration.load("/tmp")
        conf == loaded_conf


if __name__ == "__main__":
    unittest.main()
