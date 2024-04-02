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
            await message.channel.send("The event has ended! The leaderboard is as follows:")
            lb = Leaderboard(self.server, self.client)
            msg = await message.channel.send("Loading...", view=lb)
            lb.message = msg
            await lb.update()
            return
            command = message.content.split()[2]
            if command in ["help"]:
                await message.channel.send("Welcome to the Spring Break event! This game's a detective game, and the winner will get $5.")
                await message.channel.send("Essentially, you can try and impersonate someone  - this means that every single one of your messages will show up as 'theirs'. Do `dis apr i [someone]` to do this. Note, this [someone] doesn't have to be a ping! It can either be their nickname or discord tag")
                await message.channel.send("Try and impersonate them as close as possible. For every message you send as the impersonator, you earn an extra point that you can redeem later by reverting to your original self by just typing `dis apr i` again. However, once you revert, you have to wait 30 minutes to impersonate again.")
                await message.channel.send("However, someone can steal your points! If you do `dis apr c [impersonator] [impersonated]` (these must be pings) on someone else and you are right, you get all the points the other has gotten so far. However, if you are wrong, you lose 7 points!")
                await message.channel.send("do `dis apr lb` to check the current leaderboard. Note that during this time, `dis lb` and `dis snipe` will be disabled.")
            elif command in ["imp", "impersonate", "i"]:
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
                    if ping.id == message.author.id:
                        await message.channel.send("You can't impersonate yourself")
                        return

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
                            await message.channel.send("Incorrect. -7 points.")
                            longterm.add_points(message.author.id, -7)

                    else:
                        await message.channel.send("Incorrect. -7 points.")
                        longterm.add_points(message.author.id, -7)

            elif command in ["leaderboard", "lb"]:
                lb = Leaderboard(self.server, self.client)
                msg = await message.channel.send("Loading...", view=lb)
                lb.message = msg
                await lb.update()



        else:
            return
            if database.aprilfools.has_data(id=message.author.id):
                await message.delete()
                content = pingFilter.filter_content(message.content)
                channel = message.channel
                if message.channel.id not in [936716274833162322, 975925480882585610]:
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
