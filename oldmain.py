import discord
import discord.ext.commands
import os
from discord.utils import get
from discord.ext import tasks, commands
import time
import activity
import snipe
import asyncio
import datetime
from archive import group, schedule, vote
import birthday
import requests

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.ext.commands.Bot("", intents=intents)


PREFIX = "dis"

@client.event
async def on_ready():
    global STARTED
    STARTED = True
    print("hi")
@client.event
async def on_message(message):
    # set ignore cases
    if isinstance(message.channel, discord.DMChannel) or message.author.bot or len(message.content) == 0:
        return


    # activity system
    activity.process_message(message, db)


    # check if its a command or not
    if content.split()[0] in [prefix, PREFIX]:
        if len(content.split()) == 1:
            return
        command = content.split()[1]
        await activity.activity_command_check(message, db, client, SERVER)

        if command in ["request", "announce", "announcement", "req"]:
            try:
                if time.time() - db["announcement_cooldown"][str(
                        message.author.id)] >= 28800:
                    db["announcement_duration"][message.author.id] = 45
                    await message.author.add_roles(
                        get(SERVER.roles, name="i can talk in announcements"))
                    await message.channel.send(
                        "You can now post in announcements for 45 seconds.")

                else:
                    await message.channel.send(
                        "You are still on cooldown for announcements.")

            except KeyError:
                db["announcement_duration"][message.author.id] = 45
                await message.author.add_roles(
                    get(SERVER.roles, name="i can talk in announcements"))
                await message.channel.send(
                    "You can now post in announcements for 45 seconds.")



class ServerClock(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.discordTunnelMsgIds = set()


    @tasks.loop(seconds=1.0)
    async def announce_duration(self):
        announcement_role = get(SERVER.roles,
                                name="i can talk in announcements")
        for key, value in db["announcement_duration"].items():
            db["announcement_duration"][key] = value - 1
            if value - 1 <= 0:
                await get(SERVER.members,
                          id=int(key)).remove_roles(announcement_role)
                del db["announcement_duration"][key]
                db["announcement_cooldown"][key] = time.time()



    @set_server.before_loop
    async def before_tick(self):
        await self.client.wait_until_ready()

    @announce_duration.before_loop
    async def before_announce(self):
        await self.client.wait_until_ready()

    @birthday.before_loop
    async def before_birthday(self):
        await self.client.wait_until_ready()

    @discordTunnel.before_loop
    async def before_tunnel(self):
        await self.client.wait_until_ready()


async def main():
    clock = ServerClock(client)
    clock.set_server.start()
    clock.announce_duration.start()
    clock.birthday.start()
    # clock.discordTunnel.start()
    try:
        await client.start(os.getenv('token'))

    except discord.errors.HTTPException:
        print("We got ratelimited")


asyncio.get_event_loop().run_until_complete(main())
