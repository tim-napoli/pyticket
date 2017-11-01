import unittest
from unittest import mock

from pyticket import PyticketException
from pyticket.commands import (
    create_ticket, edit_ticket, show_ticket, list_tickets, close_ticket,
    reopen_ticket, delete_ticket, rename_ticket, works_on, release, configure,
    init
)


@mock.patch('pyticket.commands.Repository')
class CommandsTest(unittest.TestCase):

    @mock.patch('subprocess.call')
    def test_create_ticket(self, call_mock, repo_mock):
        create_ticket({}, "blectre", "debug")
        repo_mock.assert_called_with(".")
        repo_mock().create_ticket.assert_called_with(
            "blectre", "opened", []
        )
        repo_mock().write_ticket_content.assert_called
        call_mock.assert_called()

    @mock.patch('subprocess.call')
    def test_edit_ticket(self, call_mock, repo_mock):
        edit_ticket({}, "blectre")
        call_mock.assert_called()

    @mock.patch('subprocess.call')
    def test_create_ticket_no_edit(self, call_mock, repo_mock):
        create_ticket({"no-edit": None}, "blectre", "debug")
        call_mock.assert_not_called()

    @mock.patch('pyticket.commands.vmd')
    def test_show_ticket(self, vmd_mock, repo_mock):
        show_ticket({}, "blectre")
        repo_mock.assert_called_with(".")
        repo_mock().read_ticket_content.assert_called_with("blectre")

    @mock.patch('pyticket.commands.vmd')
    def test_show_ticket_no_content(self, vmd_mock, repo_mock):
        repo_mock().has_ticket_content.return_value = False
        self.assertRaises(PyticketException, show_ticket, {}, "blectre")

    def test_list_tickets(self, repo_mock):
        list_tickets({"opened": None, "tags": "x,y"}, "blectre")
        repo_mock().list_tickets.assert_called_with(
            root="blectre", status="opened", tags=["x", "y"]
        )

    def test_close_ticket(self, repo_mock):
        close_ticket({}, "blectre")
        repo_mock().switch_ticket_status.assert_called_with(
            "blectre", "closed"
        )

    def test_reopen_ticket(self, repo_mock):
        reopen_ticket({}, "blectre")
        repo_mock().switch_ticket_status.called_with(
            "blectre", "opened"
        )

    def test_delete_ticket(self, repo_mock):
        delete_ticket({"force": None}, "blectre")
        repo_mock().delete_ticket.assert_called_with(
            "blectre"
        )

    def test_rename_ticket(self, repo_mock):
        rename_ticket({}, "blectre", "new-blectre")
        repo_mock().rename_ticket.assert_called_with(
            "blectre", "new-blectre"
        )

    def test_works_on(self, repo_mock):
        works_on({}, "blectre")
        repo_mock().set_working_ticket.assert_called_with(
            "blectre"
        )

    def test_release(self, repo_mock):
        release({})
        repo_mock().set_working_ticket.assert_called()

    @mock.patch('pyticket.commands.Configuration')
    @mock.patch('pyticket.utils.get_home_path')
    def test_configure(self, home_mock, config_mock, repo_mock):
        home_mock.return_value = "home_dir"
        configure({}, "a key", "a value")
        config_mock.load.assert_called_with("home_dir")
        config_mock.load().set_value.assert_called_with("a key", "a value")
        config_mock.load().save.assert_called_with("home_dir")

    def test_init(self, repo_mock):
        init({}, "blectre")
        repo_mock.assert_called_with("blectre", create=True)


if __name__ == "__main__":
    unittest.main()
