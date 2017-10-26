"""Various generators to do random testing on pyticket."""
import random
import string

from pyticket.ticket import MetaTicket
from pyticket.configuration import Configuration


def gen_ticket_name():
    """Generate a valid ticket name."""
    count = random.randrange(1, 20)
    name = "".join([random.choice(MetaTicket.VALID_NAME_CHARSET)
                   for _ in range(count)])
    if name == "." or name == "..":
        return gen_ticket_name()
    return name


def gen_tag_name():
    """Generate a valid tag name."""
    return gen_ticket_name()


def gen_tags():
    """Generate a valid tag list."""
    count = random.randrange(0, 100)
    return [gen_tag_name() for _ in range(count)]


def gen_status():
    """Generate a valid status."""
    return random.choice(MetaTicket.VALID_STATUS)


def gen_meta_ticket():
    """Generate a valid MetaTicket."""
    name = gen_ticket_name()
    status = gen_status()
    tags = gen_tags()
    return MetaTicket(name, status, tags)


def gen_ticket_content():
    """Generate a valid ticket content."""
    count = random.randrange(1, 10000)
    content = "".join([random.choice(string.printable)
                       for _ in range(count)]).replace('\r', '\n')
    return content


def gen_configuration_values():
    """Generates a pyticket.Configuration valid values set."""
    k = random.randrange(len(Configuration.ALLOWED_KEYS))
    keys = []
    while k > 0:
        key = random.choice(Configuration.ALLOWED_KEYS)
        if key in keys:
            continue
        keys.append(key)
        k = k - 1
    values = {}
    for key in keys:
        values.update({key: gen_string(0, 10)})
    return values


def gen_string(min_size, max_size, charset=string.printable):
    """Generates a string using the given charset and size range.

    :param min_size: minimum generated string size.
    :param max_size: maximum generated string size.
    :param charset: generated string charset.
    :return: the generated string.
    """
    return "".join(
        [random.choice(charset) for _ in range(min_size, max_size+1)]
    )
