import os
import os.path

from pyticket.utils import get_root_path

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

    print("Pyticket repository created")
