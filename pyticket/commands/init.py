import os
import os.path
import getpass

from pyticket.utils import get_root_path, get_home_path, configuration

def init(argv, directory : "The pyticket repository directory"):
    if os.path.isdir(get_root_path(directory)):
        raise RuntimeError(
            "There already exists a pyticket repository in '{}'".format(
                directory
            )
        )

    os.mkdir("{}/".format(get_root_path(directory)))
    os.mkdir("{}/opened/".format(get_root_path(directory)))
    os.mkdir("{}/closed/".format(get_root_path(directory)))

    # Create default configuration file if needed.
    if not os.path.isdir(get_home_path()):
        os.mkdir(get_home_path())
        config = configuration({
            "editor": "nano"
        })
        config.save(get_home_path())

    print("Pyticket repository created")
