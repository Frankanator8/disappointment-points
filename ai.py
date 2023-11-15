def process_command(message, db):
    if message.channel.id == 1151283797661319199:
        if message.content.split()[1] == "chatbot":
            if message.content.split()[2] == "status":
                pass