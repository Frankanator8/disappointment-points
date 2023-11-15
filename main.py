import subprocess
import importlib.util
packages = ["discord.py==2.3.2", "flask", "waitress", "dateparser", "replit"]
for package in packages:
    install = True
    if package != "discord.py==2.3.2":
        spec = importlib.util.find_spec(package)
        if spec is not None:
            install = False

    if install:
        result = subprocess.run(["pip3", "install", package],
                                capture_output=True)
        print(f"Installed package: {package}")

    else:
        print(f"Package {package} already installed")

import discord
import discord.ext.commands
import os
from replit import db
from website import keep_alive
import copy
from discord.utils import get
from discord.ext import tasks, commands
import math
import time
from dbsave import db_as_dict, save_dict, load_save, clean_up
import activity
import snipe
import asyncio
import string
import datetime
import group
import birthday
import vote
import schedule
import requests

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.ext.commands.Bot("", intents=intents)


PREFIX = "dis"

SERVER = None
MOD_ROLE = None
STARTED = False

BAD_CHARS = []
with open("e.txt") as f:
    for line in f.readlines():
        BAD_CHARS.extend(line.split())


def add_db_category(db, name, backup, errorValue, clean):
    if clean:
        db[name] = copy.deepcopy(errorValue)

    else:
        try:
            db[name] = backup[name]

        except KeyError:
            db[name] = copy.deepcopy(errorValue)


def set_up_db(clean):
    backup = {}
    for key, item in db.items():
        backup[key] = copy.deepcopy(item)

    clean_up()
    save_dict(db_as_dict(db))
    
    for key in db.keys():
        del db[key]

    

    add_db_category(db, "mod_strikes", backup, {}, clean)
    add_db_category(db, "activity_points", backup, {}, clean)
    add_db_category(db, "progress_to_point", backup, {}, clean)
    add_db_category(db, "messages_since_wipe", backup, 0, clean)
    add_db_category(db, "messaged_already", backup, [], clean)
    add_db_category(db, "announcement_duration", backup, {}, clean)
    add_db_category(db, "announcement_cooldown", backup, {}, clean)
    add_db_category(db, "messages", backup, [], clean)
    add_db_category(db, "message_amount", backup, {}, clean)
    add_db_category(db, "emoji", backup, {}, clean)
    add_db_category(db, "announced", backup, [], clean)
    add_db_category(db, "prefixes", backup, {}, clean)
    add_db_category(db, "snipe", backup, {}, clean)
    add_db_category(db, "birthdays", backup, {}, clean)
    add_db_category(db, "locked", backup, {}, clean)
    add_db_category(db, "reminded", backup, {}, clean)
    add_db_category(db, "groups", backup, {}, clean)
    add_db_category(db, "votes", backup, {}, clean)
    add_db_category(db, "schedules", backup, {}, clean)
    add_db_category(db, "ap_w", backup, {}, clean)
    add_db_category(db, "ptp_w", backup, {}, clean)
    add_db_category(db, "lastWeek", backup, {"time":time.time()}, clean)
    
    # add_db_category(db, "groupCheck", backup, {}, clean)
    # load_save("db_backups/backup_08.03.2023 22.38.23", db)

@client.event
async def on_ready():
    global STARTED
    STARTED = True
    print("hi")
    # await asyncio.sleep(1)
    # dylan = get(SERVER.members, id=612067775388581899)
    # print(dylan.status)
    # dm = await dylan.create_dm()
    # async for message in dm.history(limit=10):
    #     print(f"({message.created_at}){str(message.author)} - {str(message.content)}")



@client.event
async def on_message_delete(message):
    if message.author.bot:
        return

    if str(message.channel.id) not in db["snipe"].keys():
        db["snipe"][message.channel.id] = []
    db["snipe"][str(message.channel.id)].insert(0, (message.author.id,
                                       snipe.filter_content(
                                           message.content, SERVER)))
    if (len(db["snipe"][str(message.channel.id)]) > 15):
        db["snipe"][str(message.channel.id)].pop(15)

@client.event
async def on_message_edit(message, message_after):
    if message.author.bot:
        return
    if str(message.channel.id) not in db["snipe"].keys():
        db["snipe"][message.channel.id] = []
    db["snipe"][str(message.channel.id)].insert(0, (message.author.id,
                                       snipe.filter_content(
                                           message.content, SERVER)))
    if (len(db["snipe"][str(message.channel.id)]) > 15):
        db["snipe"][str(message.channel.id)].pop(15)
    
    


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        await member.add_roles(get(SERVER.roles, id=994267761343741992))

    elif before.channel is not None and after.channel is None:
        await member.remove_roles(get(SERVER.roles, id=994267761343741992))


@client.event
async def on_message(message):
    global SERVER, MOD_ROLE, BLACKLISTED_CHANNELS

    # ignore dms (in most cases)
    if isinstance(message.channel, discord.DMChannel):
        return

    # we don't want bots to influence
    if message.author.bot:
        return

    author = message.author
    content = message.content

    await group.check_group(message, db, SERVER)

    # activity system
    activity.process_message(message, db)


    if len(content.split()) == 0:
        return

    if str(author.id) in db["prefixes"].keys():
        prefix = db["prefixes"][str(author.id)]

    else:
        prefix = PREFIX

    for user in message.mentions:
        if user.id == 896123313389178921:
            await message.reply(f"Your prefix is `{prefix}`")

    # check if its a command or not
    if content.split()[0] == prefix:
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

        if command in ["snipe", "ld", "delete"]:
            await snipe.snipeCommand(message, db, SERVER)

        if command in ["sync"]:
            if author.id == 695290142721572935:
                fmt = await client.tree.sync()
                await message.channel.send(
    f"Synced {len(fmt)} commands to the current server"
  )
            return

        if command in ["reverse"]:
            if message.author.id == 695290142721572935:
                for server in client.guilds:
                    if server.id == 886651493556572220:
                        msg = await message.channel.send("0% done")
                        for index, channel in enumerate(server.channels):
                            if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel) or isinstance(channel, discord.CategoryChannel):
                                print(channel.name)
                                await channel.edit(name=channel.name[::-1])
                                await msg.edit(content=f"{round((index+1)/len(server.channels), 2)}% done")

        if command in ["pfp"]:
            img = None
            for attachment in message.attachments:
                img = requests.get(attachment.url).content
                break
                
            if img is not None:
                await SERVER.edit(icon=img)
            return

        await birthday.process_message(message, db)
        await group.process_message(message, db, client)
        await vote.process_command(message, db)
        

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
            
            msg = f"{msg}\n**{schedule.make_message(index, *period)}** *(shared with {'no one :( ' if len(friends)==0 else ', '.join(friends)})*"

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
    set_up_db(False)
    keep_alive()
    clock.set_server.start()
    clock.announce_duration.start()
    clock.birthday.start()
    # clock.discordTunnel.start()
    try:
        await client.start(os.getenv('TOKEN'))

    except discord.errors.HTTPException:
        print("We got ratelimited")


asyncio.get_event_loop().run_until_complete(main())
