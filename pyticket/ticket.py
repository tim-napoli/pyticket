import string
import inspect

from pyticket import PyticketException


class MetaTicket:
    """Ticket meta-information."""

    VALID_NAME_CHARSET = "-_@." + string.ascii_letters + string.digits

    VALID_STATUS = ["opened", "closed"]

    def __init__(self, name, status, tags):
        self.name = name
        self.status = status
        self.tags = tags

    def to_string(self):
        """Return the ticket string as found in the meta-tickets file."""
        return "{name} {status} ({tags})".format(
            name=self.name, status=self.status, tags=",".join(self.tags)
        )

    @staticmethod
    def parse(line):
        """Parse a pyticket line."""
        s = inspect.signature(MetaTicket.__init__)
        nargs = len(s.parameters) - 1
        split = line.split(" ")
        if len(split) != nargs:
            raise PyticketException(
                "a pyticket line must contain {} entries, but found {}".format(
                    nargs, len(split)
                )
            )

        name = split[0]
        status = split[1]
        tags = split[2].split(",")
        if not MetaTicket.is_valid_name(name):
            raise PyticketException("'{}' is not a valid name".format(name))
        if status not in ["opened", "closed"]:
            raise PyticketException(
                "'{}' is not a valid status".format(status)
            )
        for tag in tags:
            if not MetaTicket.is_valid_tag_name(tag):
                raise PyticketException(
                    "'{}' is not a valid tag name".format(tag)
                )

        return MetaTicket(name, status, tags)

    @staticmethod
    def is_valid_name(name):
        for letter in name:
            if letter not in MetaTicket.VALID_NAME_CHARSET:
                return False
        return True

    @staticmethod
    def is_valid_tag_name(name):
        return MetaTicket.is_valid_name(name)

    @staticmethod
    def is_valid_status(status):
        return status in MetaTicket.VALID_STATUS
