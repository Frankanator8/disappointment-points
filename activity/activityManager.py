from commandset import CommandSetManager


class ActivityManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["lb", "leaderboard", "info", "p"])

    async def on_message(self, message):
        if self.is_my_message(message):
            await message.channel.send("hi!")