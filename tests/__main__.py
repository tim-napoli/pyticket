import unittest
import sys
import os

from tests import (
    test_configuration, test_generators, test_migrations, test_repository,
    test_ticket, test_command_tickets
)


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(test_configuration))
    suite.addTests(loader.loadTestsFromModule(test_generators))
    suite.addTests(loader.loadTestsFromModule(test_migrations))
    suite.addTests(loader.loadTestsFromModule(test_repository))
    suite.addTests(loader.loadTestsFromModule(test_ticket))
    suite.addTests(loader.loadTestsFromModule(test_ticket))
    suite.addTests(loader.loadTestsFromModule(test_command_tickets))
    return suite


if __name__ == "__main__":
    sys.stdout = open(os.devnull, 'w')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
