import unittest
from unittest import mock

from pyticket import PyticketException
from pyticket.commands.tickets import (
    create_ticket, edit_ticket, show_ticket, list_tickets, close_ticket,
    reopen_ticket, delete_ticket, rename_ticket, works_on, release
)


@mock.patch('pyticket.commands.tickets.Repository')
class TicketCommandsTest(unittest.TestCase):

    @mock.patch('subprocess.call')
    def test_create_ticket(self, call_mock, repo_mock):
        create_ticket({}, "blectre", "debug")
        assert repo_mock.called_with(root=".")
        assert repo_mock().create_ticket.called_with(
            ticket_name="blectre",
            template="debug"
        )
        assert repo_mock().write_ticket_content.called_with(
            ticket_name="blectre"
        )
        assert call_mock.called

    @mock.patch('subprocess.call')
    def test_edit_ticket(self, call_mock, repo_mock):
        edit_ticket({}, "blectre")
        assert call_mock.called

    @mock.patch('subprocess.call')
    def test_create_ticket_no_edit(self, call_mock, repo_mock):
        create_ticket({"no-edit": None}, "blectre", "debug")
        assert not call_mock.called

    @mock.patch('pyticket.commands.tickets.vmd')
    def test_show_ticket(self, vmd_mock, repo_mock):
        show_ticket({}, "blectre")
        assert repo_mock.called_with(root=".")
        assert repo_mock().read_ticket_content("blectre")

    @mock.patch('pyticket.commands.tickets.vmd')
    def test_show_ticket_no_content(self, vmd_mock, repo_mock):
        repo_mock().has_ticket_content.return_value = False
        self.assertRaises(PyticketException, show_ticket, {}, "blectre")

    def test_list_tickets(self, repo_mock):
        list_tickets({"opened": None, "tags": "x,y"}, "blectre")
        assert repo_mock().list_tickets.called_with(
            root="blectre", status="opened", tags=["x", "y"]
        )

    def test_close_ticket(self, repo_mock):
        close_ticket({}, "blectre")
        assert repo_mock().switch_ticket_status.called_with(
            name="blectre", status="closed"
        )

    def test_reopen_ticket(self, repo_mock):
        reopen_ticket({}, "blectre")
        assert repo_mock().switch_ticket_status.called_with(
            name="blectre", status="opened"
        )

    def test_delete_ticket(self, repo_mock):
        delete_ticket({"force": None}, "blectre")
        assert repo_mock().delete_ticket.called_with(
            name="blectre"
        )

    def test_rename_ticket(self, repo_mock):
        rename_ticket({}, "blectre", "new-blectre")
        assert repo_mock().rename_ticket.called_with(
            name="blectre", new_name="new-blectre"
        )

    def test_works_on(self, repo_mock):
        works_on({}, "blectre")
        assert repo_mock().set_working_ticket.called_with(
            name="blectre"
        )

    def test_release(self, repo_mock):
        release({})
        assert repo_mock().set_working_ticket.called


if __name__ == "__main__":
    unittest.main()
