import time

import discord
import requests

import database
from aprilfools.lbview import Leaderboard
from commandset import CommandSetManager
from aprilfools import pingFilter, longterm


class AprilFoolsManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["apr", "aprilfools", "a1"])

    async def on_message(self, message):
        if self.is_my_message(message):
            command = message.content.split()[2]
            if command in ["imp", "impersonate", "i"]:
                can = longterm.can_impersonate(message.author.id)
                if not can[0]:
                    time_format = f"<t:{round(can[1]+time.time())}:R>"
                    await message.channel.send(f"You can impersonate again {time_format}")
                    return
                ping = None
                if len(message.mentions) == 0:
                    person = " ".join(message.content.split()[3:])
                    for member in self.server.members:
                        if member.display_name == person or str(member) == person:
                            ping = member

                else:
                    ping = message.mentions[0]

                if ping is None:
                    if database.aprilfools.has_data(id=message.author.id):
                        pts = database.aprilfools.find_one(id=message.author.id)["msgs"]
                        database.aprilfools.delete_data(id=message.author.id)
                        await message.channel.send(f"You stopped, and earned {pts} points!")
                        longterm.add_points(message.author.id, pts)
                        longterm.restrict_time(message.author.id)

                    else:
                        await message.channel.send("Provide a valid ping or spell out their discord tag or display name")

                else:
                    if database.aprilfools.has_data(id=message.author.id):
                        database.aprilfools.update_data("to_id", ping.id, id=message.author.id)

                    else:
                        database.aprilfools.add_data({"id":message.author.id, "to_id":ping.id, "msgs":0})

                    await message.delete()

            elif command in ["catch", "c"]:
                if len(message.mentions) != 2:
                    await message.channel.send("You must mention 2 people - the first being the impersonator, the second being the impersonated")

                else:
                    impersonator = message.mentions[0]
                    impersonated = message.mentions[1]
                    if impersonator.id == message.author.id:
                        await message.channel.send("No self reporting")
                        return
                    if database.aprilfools.has_data(id=impersonator.id):
                        if database.aprilfools.find_one(id=impersonator.id)["to_id"] == impersonated.id:
                            pts = database.aprilfools.find_one(id=impersonator.id)["msgs"]
                            database.aprilfools.delete_data(id=impersonator.id)
                            await message.channel.send(f"You were correct! You stole {pts} points!")
                            longterm.add_points(message.author.id, pts)
                            longterm.restrict_time(impersonator.id)

                        else:
                            await message.channel.send("Incorrect. -15 points.")
                            longterm.add_points(message.author.id, -15)

                    else:
                        await message.channel.send("Incorrect. -15 points.")
                        longterm.add_points(message.author.id, -15)

            elif command in ["leaderboard", "lb"]:
                lb = Leaderboard(self.server, self.client)
                msg = await message.channel.send("Loading...", view=lb)
                lb.message = msg
                await lb.update()



        else:
            if database.aprilfools.has_data(id=message.author.id):
                await message.delete()
                content = pingFilter.filter_content(message.content)
                channel = message.channel

                database.aprilfools.update_inc("msgs", 1, id=message.author.id)
                author = self.server.get_member(database.aprilfools.find_one(id=message.author.id)["to_id"])

                avatar = requests.get(author.avatar).content
                try:
                    webhook = await channel.create_webhook(name=author.display_name,
                                                       avatar=avatar,
                                                       reason="snipe message")

                except discord.errors.HTTPException:
                    hooks = await self.server.webhooks()
                    for hook in hooks:
                        if hook.user.id == 896123313389178921:
                            await hook.delete()

                    webhook = await channel.create_webhook(name=author.display_name, avatar=avatar, reason="snipe message")

                if content == "":
                    await webhook.send("*seems to be an image*")

                else:
                    await webhook.send(content)
                await webhook.delete()
