# PyTicket

PyTicket is a simple command-line tool allowing to manage development tickets.
PyTicket is *not* an online tool or anything like this. It is designed to be
used per developers for developers, and should be using with a versioning
system like git.

## Getting started

### Configuration

First, you should initialize a pyticket repository:

        $ cd your-repo
        $ pyticket init .

This command will create a default ```.pyticket``` directory.

Next, it is good to configure your pyticket, for exemple giving your name or
your editor:

        $ pyticket configure name tim
        $ pyticket configure editor vim

### Editing tickets

This done, you can create a first ticket:

        $ pyticket open-ticket a-first-ticket

This will open your editor and allows you to write your ticket content.
Here, "a-first-ticket" is the ticket name *and the ticket ID*. This means
that a ticket name must be unique. The ticket content is markdown.

You can update your ticket content using the following command:

        $ pyticket edit-ticket a-first-ticket

### Closing a ticket

When a development related to a ticket is done, you should close the ticket :

        $ pyticket close-ticket a-first-ticket

### Tags system

pyticket uses a tag system to filter tickets. To attach tags to a ticket,
simply add them on the last line of your ticket. This line should start with
the keyword "tags: ":

    This is a ticket content speaking about a super nice-feature.

    tags: feature, super-important

### Tickets search

Search for every opened ticket

        $ pyticket search --status open


You can use the search-tagged command to list every tickets with the given
tags (when multiples tags are given, it has the or semantic):

        $ pyticket search --status open --tags super-important

### Going further

Simply type ```pyticket help``` to get a list of every pyticket commands.

