import os
import time

from pyticket import utils as utils

HEADER = ["Ticket", "Status", "Last update", "Tags"]

def get_terminal_width():
    width, height = os.popen("stty size", "r").read().split()
    return int(width)

def get_row_cols_min_size(row):
    sizes = []
    for field in row:
        sizes.append(len(field) + 3)
    return sizes

def get_table_cols_min_size(table):
    min_sizes = get_row_cols_min_size(table[0])
    for row in range(1, len(table)):
        sizes = get_row_cols_min_size(table[row])
        for col in range(0, len(sizes)):
            if sizes[col] > min_sizes[col]:
                min_sizes[col] = sizes[col]
    return min_sizes

def get_tickets_table(ticket_name, status, tags):
    table = []
    for stat in status:
        tickets = sorted(utils.list_tickets(stat))
        for ticket in tickets:
            if (ticket_name and not utils.is_child_of(ticket, ticket_name) and
                     ticket != ticket_name):
                continue
            content = utils.read_ticket(stat, ticket)
            ticket_tags = utils.get_ticket_tags(content)
            if not list(set(ticket_tags).intersection(tags)) == tags:
                continue
            mtime = utils.get_ticket_last_update_date(stat, ticket)
            table.append([ticket, stat, mtime, ticket_tags])
    return table

def print_row(row, sizes):
    line = ""
    for i in range(0, len(row)):
        line += " {}".format(row[i]).ljust(sizes[i])
    print(line)

def format_row(row):
    return [
        row[0], row[1],
        time.strftime("%m/%d/%Y %H:%M:%S",time.gmtime(row[2])),
        ", ".join(row[3])
    ]

def format_table(table):
    formatted_table = [HEADER]
    for i in range(0, len(table)):
        formatted_table.append(format_row(table[i]))
    return formatted_table

def table(options, ticket : "Show only this ticket tree" = None):
    sorted_field = 2
    sorted_reverse = True
    if "sorted-name" in options:
        sorted_field = 0
        sorted_reverse = False

    count = int(options.get("count", -1))

    status = ["opened", "closed"]
    if "opened" in options:
        status = ["opened"]
    elif "closed" in options:
        status = ["closed"]

    tags = []
    if "tags" in options:
        tags = options["tags"].split(",")

    table = sorted(get_tickets_table(ticket, status, tags),
                   key=lambda row: row[sorted_field], reverse=sorted_reverse)
    if count > 0:
        table = table[:count]

    formatted_table = format_table(table)
    sizes = get_table_cols_min_size(formatted_table)
    print("-" * sum(sizes))
    print_row(formatted_table[0], sizes)
    print("-" * sum(sizes))
    for i in range(1, len(formatted_table)):
        print_row(formatted_table[i], sizes)
    print("-" * sum(sizes))
