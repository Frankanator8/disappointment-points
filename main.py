import discord
import discord.ext.commands
import os
from discord.ext import tasks, commands
import asyncio

from activity.activityManager import ActivityManager
from announcements.announcementSetManager import AnnouncementManager
from birthday.birthdaySetManager import BirthdayManager
from misc.miscSetManager import MiscManager
from snipe.snipeSetManager import SnipeManager

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.ext.commands.Bot("", intents=intents)

commandManagers = [ActivityManager(client), SnipeManager(client), BirthdayManager(client), MiscManager(client),
                   AnnouncementManager(client)]

@client.event
async def on_ready():
    print("hi")
    for commandSetManager in commandManagers:
        await commandSetManager.on_ready()

@client.event
async def on_message_delete(message):
    if message.author.bot:
        return

    for commandSetManager in commandManagers:
        await commandSetManager.on_message_delete(message)

@client.event
async def on_message_edit(message, message_after):
    if message.author.bot:
        return

    for commandSetManager in commandManagers:
        await commandSetManager.on_message_edit(message, message_after)

@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    for commandSetManager in commandManagers:
        await commandSetManager.on_voice_state_update(member, before, after)


@client.event
async def on_message(message):
    # set ignore cases
    if isinstance(message.channel, discord.DMChannel) or message.author.bot or len(message.content) == 0:
        return

    for commandSetManager in commandManagers:
        await commandSetManager.on_message(message)

# @client.tree.command(name="schedule", description="Show your current schedule, or set on the first turn")
# async def sched(interaction: discord.Interaction):
#     if str(interaction.user.id) not in db["schedules"].keys():
#         embed=discord.Embed(title="Set Schedule",
#                             color=0x0089D7,
#                             description="The schedule setter is loading. If this message does not disappear after a few seconds, contact <@695290142721572935>")
#         maker = schedule.ScheduleMaker(db)
#         await interaction.response.send_message(embed=embed, view=maker, ephemeral=True)
#         maker.interaction = interaction
#         await maker.update()
#
#     else:
#         my_schedule = db["schedules"][str(interaction.user.id)]
#         msg = f"{interaction.user.mention}'s schedule:\n"
#         for index, period in enumerate(my_schedule):
#             friends = []
#             for key, value in db["schedules"].items():
#                 if key != str(interaction.user.id):
#                     if value[index] == period:
#                         try:
#                             friends.append(get(SERVER.members, id=int(key)).display_name)
#
#                         except AttributeError:
#                             user = await client.fetch_user(int(key))
#                             friends.append(str(user))
#
#             msg = f"{msg}\n**{schedule.make_message(index, *period)}** *(shared with {'no one :( ' if len(friends)==0 else ', '.join(friends)})*"
#
#         await interaction.response.send_message(content=msg)




# @client.tree.command(name="setschedule", description="Set your current schedule")
# async def setsched(interaction: discord.Interaction):
#     embed=discord.Embed(title="Set Schedule",
#                         color=0x0089D7,
#                         description="The schedule setter is loading. If this message does not disappear after a few seconds, contact <@695290142721572935>")
#     maker = schedule.ScheduleMaker(db)
#     await interaction.response.send_message(embed=embed, view=maker, ephemeral=True)
#     maker.interaction = interaction
#     await maker.update()


class ServerClock(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.discordTunnelMsgIds = set()
    
    @tasks.loop(seconds=1.0)
    async def tick(self):
        for commandSetManager in commandManagers:
            await commandSetManager.on_tick(1.0)


    @tick.before_loop
    async def before_tick(self):
        await self.client.wait_until_ready()


async def main():
    clock = ServerClock(client)
    clock.tick.start()
    try:
        await client.start(os.getenv('TOKEN'))

    except discord.errors.HTTPException:
        print("We got ratelimited")


asyncio.get_event_loop().run_until_complete(main())
