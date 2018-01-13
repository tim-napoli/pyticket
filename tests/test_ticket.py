import unittest
import string

from pyticket import PyticketException
from pyticket.ticket import MetaTicket

from tests import generators
from tests.utils import repeat


class MetaTicketTest(unittest.TestCase):

    INVALID_CHARACTERS = list(
        set(string.printable) - set(MetaTicket.VALID_NAME_CHARSET)
    )

    def setUp(self):
        self.maxDiff = None

    @repeat(1000)
    def test_to_string(self):
        meta_ticket = generators.gen_meta_ticket()
        expected = "{name} {status} ({tags}) {mtime}".format(
            name=meta_ticket.name, status=meta_ticket.status,
            tags=",".join(meta_ticket.tags), mtime=meta_ticket.mtime
        )
        self.assertEqual(meta_ticket.to_string(), expected)

    @repeat(1000)
    def test_parse(self):
        name = generators.gen_ticket_name()
        status = generators.gen_status()
        tags = generators.gen_tags()
        mtime = generators.gen_time()
        line = "{} {} ({}) {}".format(name, status, ",".join(tags), mtime)
        meta_ticket = MetaTicket.parse_legacy(line)
        self.assertEqual(meta_ticket.name, name)
        self.assertEqual(meta_ticket.status, status)
        self.assertEqual(meta_ticket.tags, tags)
        self.assertEqual(meta_ticket.mtime, mtime)

    def test_parse_invalid_count(self):
        line = "invalid_name opened (x,y,z) 32"
        self.assertRaises(PyticketException, MetaTicket.parse_legacy, line)

    @repeat(1000)
    def test_parse_invalid_name(self):
        line = "inval{}id_name opened (x,y,z)".format(
            MetaTicketTest.INVALID_CHARACTERS
        )
        self.assertRaises(PyticketException, MetaTicket.parse_legacy, line)

    def test_parse_invalid_status(self):
        line = "a-ticket invalid-status (x,y,z)"
        self.assertRaises(PyticketException, MetaTicket.parse_legacy, line)

    @repeat(1000)
    def test_parse_invalid_tags(self):
        line = "a-ticket opened (x,{},z)".format(
            MetaTicketTest.INVALID_CHARACTERS
        )
        self.assertRaises(PyticketException, MetaTicket.parse_legacy, line)

    @repeat(1000)
    def test_parse_invalid_mtime(self):
        line = "a-ticket opened (x,y,z) blectre".format(
            MetaTicketTest.INVALID_CHARACTERS
        )
        self.assertRaises(PyticketException, MetaTicket.parse_legacy, line)


if __name__ == "__main__":
    unittest.main()
