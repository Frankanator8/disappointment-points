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

        if command in ["prefix", "pref", "setprefix", "setpref"]:
            try:
                db["prefixes"][author.id] = content.split()[2]
                await message.channel.send(
                    f"Prefix set to `{content.split()[2]}`")

            except IndexError:
                await message.channel.send("No prefix provided.")

        if command in ["sync"]:
            if author.id == 695290142721572935:
                fmt = await client.tree.sync()
                await message.channel.send(
                    f"Synced {len(fmt)} commands to the current server"
                )
            return


        if command in ["pfp"]:
            img = None
            for attachment in message.attachments:
                img = requests.get(attachment.url).content
                break

            if img is not None:
                await SERVER.edit(icon=img)
            return

        await birthday.process_message(message, db)


    else:
        pass


@client.tree.command(name="schedule", description="Show your current schedule, or set on the first turn")
async def sched(interaction: discord.Interaction):
    if str(interaction.user.id) not in db["schedules"].keys():
        embed=discord.Embed(title="Set Schedule",
                            color=0x0089D7,
                            description="The schedule setter is loading. If this message does not disappear after a few seconds, contact <@695290142721572935>")
        maker = schedule.ScheduleMaker(db)
        await interaction.response.send_message(embed=embed, view=maker, ephemeral=True)
        maker.interaction = interaction
        await maker.update()

    else:
        my_schedule = db["schedules"][str(interaction.user.id)]
        msg = f"{interaction.user.mention}'s schedule:\n"
        for index, period in enumerate(my_schedule):
            friends = []
            for key, value in db["schedules"].items():
                if key != str(interaction.user.id):
                    if value[index] == period:
                        try:
                            friends.append(get(SERVER.members, id=int(key)).display_name)

                        except AttributeError:
                            user = await client.fetch_user(int(key))
                            friends.append(str(user))

            msg = f"{msg}\n**{schedule.make_message(index, *period)}** *(shared with {'no one :( ' if len(friends) == 0 else ', '.join(friends)})*"

        await interaction.response.send_message(content=msg)




@client.tree.command(name="setschedule", description="Set your current schedule")
async def setsched(interaction: discord.Interaction):
    embed=discord.Embed(title="Set Schedule",
                        color=0x0089D7,
                        description="The schedule setter is loading. If this message does not disappear after a few seconds, contact <@695290142721572935>")
    maker = schedule.ScheduleMaker(db)
    await interaction.response.send_message(embed=embed, view=maker, ephemeral=True)
    maker.interaction = interaction
    await maker.update()


class ServerClock(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.discordTunnelMsgIds = set()

    @tasks.loop(seconds=15.0)
    async def set_server(self):
        global SERVER, MOD_ROLE
        SERVER = self.client.get_guild(886651493556572220)
        MOD_ROLE = get(SERVER.roles, name="Mod")

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

    @tasks.loop(seconds=15.0)
    async def birthday(self):
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.now().hour

        for key, value in db["birthdays"].items():
            if value[0] == month and value[1] == day and hour > 11: # 7 AM, +4 hrs because GMT
                if not db["reminded"][key]:
                    await get(SERVER.channels, id=901224829598969916).send(f"Happy birthday, {get(SERVER.members, id=int(key)).mention}!")
                    db["reminded"][key] = True

    @tasks.loop(seconds=2.0)
    async def discordTunnel(self):
        ch = await get(SERVER.members, id=612067775388581899).create_dm()

        for message in reversed([i async for i in ch.history(limit=100)]):
            if message.id not in self.discordTunnelMsgIds:
                print(f"({message.created_at}){str(message.author)}/{str(message.author.id)} - {str(message.content)}")
                self.discordTunnelMsgIds.add(message.id)

        next = input()
        if next != "":
            await ch.send(next)

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
