import unittest

from pyticket.ticket import MetaTicket

from tests import generators
from tests.utils import repeat


class TestGenerators(unittest.TestCase):

    @repeat(1000)
    def test_gen_ticket_name(self):
        name = generators.gen_ticket_name()
        self.assertTrue(MetaTicket.is_valid_name(name))

    @repeat(1000)
    def test_gen_tag_name(self):
        name = generators.gen_tag_name()
        self.assertTrue(MetaTicket.is_valid_tag_name(name))

    @repeat(1000)
    def test_gen_tags(self):
        tags = generators.gen_tags()
        for tag in tags:
            self.assertTrue(MetaTicket.is_valid_tag_name(tag))


if __name__ == "__main__":
    unittest.main()
