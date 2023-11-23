from activity.lbview import Leaderboard
from activity.process import process_message
from commandset import CommandSetManager


class ActivityManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["lb", "leaderboard", "info", "p"])

    async def on_message(self, message):
        process_message(message)
        if self.is_my_message(message):
            command = message.content.split()[1]
            if command in ["leaderboard", "lb"]:
                lb = Leaderboard(self.server, self.client)
                msg = await message.channel.send("Loading...", view=lb)
                lb.message = msg
                await lb.update()