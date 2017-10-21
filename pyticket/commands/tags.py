import pyticket.utils as utils

def add_tag(options, ticket : "The ticket to modify",
            tag : "The tag to add to the ticket"):
    directory = utils.find_ticket_directory(ticket)
    content = utils.read_ticket(directory, ticket)
    tags = utils.get_ticket_tags(content)
    if tag in tags:
        return
    tags.append(tag)

    lines = content.splitlines()
    tag_line = "tags: {}".format(" ".join(tags))
    if len(lines) > 0 and lines[-1].startswith("tags:"):
        lines[-1] = tag_line
    else:
        lines.append(tag_line)

    new_content = "\n".join(lines)
    utils.write_ticket(directory, ticket, new_content)

def remove_tag(options, ticket : "The ticket to modify",
               tag : "The tag to remove from the ticket"):
    directory = utils.find_ticket_directory(ticket)
    content = utils.read_ticket(directory, ticket)
    tags = utils.get_ticket_tags(content)
    if not tag in tags:
        return
    tags.remove(tag)

    lines = content.splitlines()
    tag_line = "tags: {}".format(" ".join(tags))
    lines[-1] = tag_line

    new_content = "\n".join(lines)
    utils.write_ticket(directory, ticket, new_content)
