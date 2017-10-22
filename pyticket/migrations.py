import os.path
from pyticket import utils as utils

def working_ticket_migration():
    print("Applying working ticket migration...")
    path = "{}/working".format(utils.get_root_path())
    open(path, "w+").close()

MIGRATIONS = [
    working_ticket_migration
]

def get_current_migration():
    path = "{}/migration".format(utils.get_root_path())
    if not os.path.exists(path):
        return 0
    with open(path, "r") as f:
        return int(f.read())

def update_current_migration(directory = "."):
    path = "{}/migration".format(utils.get_root_path(directory))
    with open(path, "w+") as f:
        f.write(str(len(MIGRATIONS)))

def apply_migrations():
    current_migration = get_current_migration()
    if current_migration >= len(MIGRATIONS):
        return
    for migration_func in MIGRATIONS[current_migration:]:
        migration_func()
    update_current_migration()
