import string
import inspect
import re

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

    def __eq__(self, other):
        return (self.name == other.name and
                self.status == other.status and
                self.tags == other.tags)

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

        NAME_PATTERN = r"(?P<name>[{}]+)".format(MetaTicket.VALID_NAME_CHARSET)
        STATUS_PATTERN = r"(?P<status>(?:opened)|(?:closed))".format(
            "|".join(
                ["(?:{})".format(status) for status in MetaTicket.VALID_STATUS]
            )
        )
        TAGS_PATTERN = r"\((?P<tags>[{name},]*)\)".format(
            name=MetaTicket.VALID_NAME_CHARSET
        )

        if not re.match(NAME_PATTERN, split[0]):
            raise PyticketException(
                "'{}' is not a valid ticket name".format(split[0])
            )
        if not re.match(STATUS_PATTERN, split[1]):
            raise PyticketException(
                "'{}' is not a valid status name".format(split[1])
            )
        if not re.match(TAGS_PATTERN, split[2]):
            raise PyticketException(
                "'{}' is not a valid tags string".format(split[2])
            )

        PATTERN = "{} {} {}".format(NAME_PATTERN, STATUS_PATTERN, TAGS_PATTERN)
        matches = re.match(PATTERN, line)
        if not matches:
            raise PyticketException(
                "'{}' is not a valid meta-ticket line".format(line)
            )

        name = matches.group("name")
        status = matches.group("status")
        tags_str = matches.group("tags")
        tags = tags_str.split(",") if tags_str else []
        for tag in tags:
            if not MetaTicket.is_valid_tag_name(tag):
                raise PyticketException(
                    "'{}' is not a valid tag name".format(tag)
                )

        return MetaTicket(name, status, tags)

    @staticmethod
    def is_valid_name(name):
        if not name:
            return False
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
