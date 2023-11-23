import time

from discord.utils import get

import database
from commandset import CommandSetManager


class AnnouncementManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["req", "request", "permit"])
        self.waitTime = 0

    async def on_message(self, message):
        if self.is_my_message(message):
            command = message.content.split()[1]
            cTime = round(time.time())
            if command in ["request", "req"]:
                if database.announcement.has_data(id=message.author.id):
                    if cTime - database.announcement.find_one(id=message.author.id)["time"] >= 28800:
                        await message.author.add_roles(
                            get(self.server.roles, id=972641035358462073))
                        await message.channel.send(
                            f"You can now post in announcements for 1 minute. Time elapsed: <t:{cTime}:R>")
                        database.announcement.update_data(time, cTime, id=message.author.id)

                    else:
                        await message.channel.send(
                            f"You will be able to use `dis req` again <t:{database.announcement.find_one(id=message.author.id)['time']+28800}:R>.")

                else:
                    await message.author.add_roles(
                        get(self.server.roles, id=972641035358462073))
                    await message.channel.send(
                        f"You can now post in announcements for 1 minute. Time elapsed: <t:{cTime}:R>")
                    database.announcement.add_data({"id":message.author.id, "time":cTime})

            elif command in ["permit"]:
                if message.channel.permissions_for(message.author).manage_guild:
                    try:
                        person = message.mentions[0]
                        database.announcement.delete_data(id=person.id)
                        await message.channel.send(f"{person.mention} can talk in announcements again")

                    except IndexError:
                        await message.channel.send("Specify a person to remove announcement timeout")

                else:
                    await message.channel.send("You must have `Manage Server` permissions to do this")

    async def on_tick(self, dt):
        self.waitTime += dt
        if self.waitTime > 2:
            self.waitTime = 0
            for i in database.announcement.find():
                if time.time() - i["time"] > 60:
                    await get(self.server.members,
                              id=i["id"]).remove_roles(get(self.server.roles, id=972641035358462073))
