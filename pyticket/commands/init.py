import os
import os.path
import getpass

from pyticket import PyticketException
from pyticket.utils import (
    get_root_path, get_home_path, get_opened_tickets_path,
    get_closed_tickets_path, get_templates_path, configuration
)

DEFAULT_BUG_TEMPLATE = (
"""# Bug $ticket

## Description

## Reproduction

## Solution

tags: bug
""")

DEFAULT_FEATURE_TEMPLATE = (
"""# Feature $ticket

## Description

## Design

tags: feature
""")

def init(options, directory : "The pyticket repository directory"):
    if os.path.isdir(get_root_path(directory)):
        raise PyticketException(
            "there already exists a pyticket repository in '{}'".format(
                directory
            )
        )

    os.mkdir("{}/".format(get_root_path(directory)))
    os.mkdir(get_opened_tickets_path())
    os.mkdir(get_closed_tickets_path())
    os.mkdir(get_templates_path())

    with open(get_templates_path() + "/bug", "w+") as f:
        f.write(DEFAULT_BUG_TEMPLATE)
    with open(get_templates_path() + "/feature", "w+") as f:
        f.write(DEFAULT_FEATURE_TEMPLATE)

    # Create default configuration file if needed.
    if not os.path.isdir(get_home_path()):
        os.mkdir(get_home_path())
        config = configuration({
            "editor": "nano"
        })
        config.save(get_home_path())

    print("Pyticket repository created")
