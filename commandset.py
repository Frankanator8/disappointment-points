import database


class CommandSetManager:
    def __init__(self, client, phrases):
        self.client = client
        self.phrases = phrases

    def is_my_message(self, message):
        if len(message.content.split()) <= 1:
            return False

        if self.check_prefix(message) and message.content.split()[1] in self.phrases:
            return True

        else:
            return False

    def check_prefix(self, message):
        if len(message.content.split()) <= 0:
            return False

        if message.content.split()[0] in ["dis", database.prefixes.find_one(id=message.author.id)]:
            return True
        
        else:
            return False

    async def on_ready(self):
        self.server = self.client.get_guild(886651493556572220)

    async def on_message(self, message):
        pass

    async def on_message_delete(self, message):
        pass

    async def on_message_edit(self, message, newMessage):
        pass

    async def on_voice_state_update(self, member, before, after):
        pass

    async def on_tick(self, dt):
        pass