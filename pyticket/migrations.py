import json
import os.path
import shutil
import time

from pyticket.ticket import MetaTicket


def working_ticket_migration(directory):
    print("Applying working ticket migration...")
    path = "{}/working".format(directory)
    open(path, "w+").close()


def tickets_meta_files_migration(directory):
    def read_ticket_tags(ticket_path):
        """Returns tickets tags."""
        with open(ticket_path, "r") as f:
            content = f.read()
            lines = content.splitlines()
            if not lines:
                return []
            tag_line = lines[-1]
            if tag_line.startswith("tags:"):
                return tag_line.split()[1:]
            return []

    print("Applying tickets meta file migration...")
    # Creating the contents directory
    os.mkdir(directory + "/contents")

    # Scanning tickets & moving them in the "contents" directory
    meta_tickets = []
    for status in ["opened", "closed"]:
        tickets = os.listdir(directory + "/" + status)
        for ticket in tickets:
            tags = read_ticket_tags(
                "{}/{}/{}".format(directory, status, ticket)
            )
            meta_tickets.append(MetaTicket(ticket, status, tags))
            shutil.move(
                "{}/{}/{}".format(directory, status, ticket),
                "{}/{}/{}".format(directory, "contents", ticket)
            )
        shutil.rmtree("{}/{}".format(directory, status))

    # Creating the tickets file
    with open(directory + "/tickets", "w+") as f:
        for meta_ticket in meta_tickets:
            f.write(meta_ticket.to_string() + "\n")


def tickets_mtime_migration(directory):
    print("Applying mtime migration...")
    lines = []
    with open(directory + "/tickets", "r") as f:
        lines = f.read().splitlines()
    new_lines = []
    for line in lines:
        split = line.split()
        name = split[0]
        content_path = "{}/contents/{}".format(directory, name)
        mtime = time.time()
        if os.path.isfile(content_path):
            mtime = os.path.getmtime(content_path)
        new_lines.append("{} {}".format(line, mtime))
    with open(directory + "/tickets", "w+") as f:
        for line in new_lines:
            f.write("{}\n".format(line))


def tickets_json_migration(directory):
    print("Applying json migration...")
    tickets = []
    with open("{}/tickets".format(directory), "r") as f:
        for line in f.readlines():
            tickets.append(MetaTicket.parse_legacy(line))
    with open("{}/tickets".format(directory), "w+") as f:
        json_data = [t.to_json() for t in tickets]
        f.write(json.dumps(json_data))


MIGRATIONS = [
    working_ticket_migration,
    tickets_meta_files_migration,
    tickets_mtime_migration,
    tickets_json_migration
]


def get_current_migration(directory):
    path = "{}/migration".format(directory)
    if not os.path.exists(path):
        return 0
    with open(path, "r") as f:
        return int(f.read())


def update_current_migration(directory):
    path = "{}/migration".format(directory)
    with open(path, "w+") as f:
        f.write(str(len(MIGRATIONS)))


def apply_migrations(directory):
    current_migration = get_current_migration(directory)
    if current_migration >= len(MIGRATIONS):
        return
    for migration_func in MIGRATIONS[current_migration:]:
        migration_func(directory)
    update_current_migration(directory)
