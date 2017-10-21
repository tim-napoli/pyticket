# PyTicket

PyTicket is a simple command-line tool allowing to manage development tickets.
PyTicket is *not* an online tool or anything like this. It is designed to be
used per developers for developers, and should be using with a versioning
system like git.

## Installation

Simply use the ```setup.py``` script of this repository :

        $ setup.py install --user

Notates that a bash_completion script will be installed in your
```~/.bash_completion.d``` directory this directory exist (user installation),
or in ```/etc/bash_completion.d``` for a root installation.

## Getting started

### Configuration

First, you should initialize a pyticket repository:

        $ cd your-repo
        $ pyticket init .

This command will create a default ```.pyticket``` directory.

Next, it is good to configure your pyticket, for exemple giving your name or
your editor:

        $ pyticket configure editor vim

Tickets may be written using the markdown format.

### Editing tickets

This done, you can create a first feature ticket:

        $ pyticket create a-first-ticket feature

This will open your editor and allows you to write your ticket content.
The ticket uses the "feature" template.
Here, "a-first-ticket" is the ticket name *and the ticket ID*. This means
that a ticket name must be unique. The ticket content is markdown.

You can update your ticket content using the following command:

        $ pyticket edit a-first-ticket

### Closing a ticket

When a development related to a ticket is done, you can close the ticket :

        $ pyticket close a-first-ticket

You can also reopen a ticket:

        $ pyticket reopen a-first-ticket

### Deleting a ticket

If you want to remove a ticket, use the delete command :

        $ pyticket delete a-ticket-to-delete

### Renaming tickets

You can rename tickets:

        $ pyticket rename a-ticket its-new-name

### Tags system

pyticket uses a tag system to filter tickets. To attach tags to a ticket,
simply add them on the last line of your ticket. This line should start with
the keyword "tags: ":

    This is a ticket content speaking about a super nice-feature.

    tags: feature super-important

You can use the ```add-tag``` and ```remove-tag``` commands to add or remove
tags to tickets:

        $ pyticket add-tag test-ticket some-tag
        $ pyticket remove-tag test-ticket some-tag

### Tickets listing

The ```list``` command of pyticket allows you to list opened and closed
tickets, and to filter them using tags :

        # List every opened features
        $ pyticket list --opened --tags feature

        # List every closed features that have "x" and "y" tags:
        $ pyticket list --closed --tags x,y

### Tickets hierarchy

If you want to create a sub-ticket of an existing ticket, you just need
to prefix the name of the newly created ticket with the name of its parent
followed with a '.'.

        $ pyticket create root --no-edit
        $ pyticket create root.child --no-edit
        $ pyticket create root.another_child --no-edit
        $ pyticket create root.child.child --no-edit
        # Show the root ticket and its childs :
        $ pyticket list root

### Going further

Simply type ```pyticket help``` to get a list of every pyticket commands.

