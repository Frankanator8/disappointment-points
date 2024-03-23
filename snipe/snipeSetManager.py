from io import BytesIO

import discord
import requests

import database
from commandset import CommandSetManager
from snipe import pingFilter


class SnipeManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["snipe"])

    async def on_message_delete(self, message):
        attachments = []
        for attachment in message.attachments:
            try:
                attachments.append([await attachment.read(use_cached=True), attachment.filename])
            except (discord.HTTPException, discord.Forbidden, discord.NotFound):
                pass

        msg = {"author":message.author.id,
               "content":pingFilter.filter_content(message.content, self.server),
               "attachments":attachments}

        if not database.snipe.has_data(channel=message.channel.id):
            database.snipe.add_data({"channel":message.channel.id, "msgs":[]})

        database.snipe.add_list("msgs", msg, channel=message.channel.id)
        if len(database.snipe.find_one(channel=message.channel.id)["msgs"]) > 10:
            database.snipe.pop_list("msgs", channel=message.channel.id)

    async def on_message_edit(self, message, newMessage):
        attachments = []
        for attachment in message.attachments:
            try:
                attachments.append([await attachment.read(use_cached=True), attachment.filename])
            except (discord.HTTPException, discord.Forbidden, discord.NotFound):
                pass

        msg = {"author":message.author.id,
               "content":pingFilter.filter_content(message.content, self.server),
               "attachments":attachments}

        if not database.snipe.has_data(channel=message.channel.id):
            database.snipe.add_data({"channel":message.channel.id, "msgs":[]})

        database.snipe.add_list("msgs", msg, channel=message.channel.id)
        if len(database.snipe.find_one(channel=message.channel.id)["msgs"]) > 10:
            database.snipe.pop_list("msgs", channel=message.channel.id)


    async def on_message(self, message):
        if self.is_my_message(message):
            await message.channel.send("`snipe` has been disabled for the Spring Break event.")
            return
            if not database.snipe.has_data(channel=message.channel.id):
                await message.channel.send("This channel has no snipe messages")
                return

            list = False
            try:
                hist = int(message.content.split()[2])-1

            except IndexError:
                hist = 0

            except ValueError:
                if message.content.split()[2] == "list":
                    list = True

                else:
                    hist = 0

            if not list:
                if hist >= len(database.snipe.find_one(channel=message.channel.id)["msgs"]):
                    await message.channel.send("Not that many snipe messages")
                    return

                thisChannel = database.snipe.find_one(channel=message.channel.id)["msgs"]
                dat = thisChannel[len(thisChannel)-1-hist]
                author = dat["author"]
                content = dat["content"]
                channel = message.channel
                author = self.server.get_member(int(author))

                files = []
                for file, name in dat["attachments"]:
                    arr = BytesIO(file)
                    arr.seek(0)
                    files.append(discord.File(arr, name))

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
                    if len(files) == 0:
                        await webhook.send("*seems to be an embed message*")

                    else:
                        await webhook.send("", files=files)

                else:
                    await webhook.send(content, files=files)
                await webhook.delete()

            else:
                thisChannel = database.snipe.find_one(channel=message.channel.id)["msgs"]
                if len(thisChannel) == 0:
                    msg = "There are no snipe messages in this channel"
                else:
                    msg = "From most recent to least recent:\n"

                files = []

                for index, msgData in enumerate(reversed(thisChannel)):
                    author = msgData["author"]
                    content = msgData["content"]
                    for file, name in msgData["attachments"]:
                        arr = BytesIO(file)
                        arr.seek(0)
                        files.append(discord.File(arr, name))
                    msg = f"{msg}\n{index+1}. **{self.server.get_member(int(author)).display_name}**: {content if content!='' else '*message content empty*'}{'*+file attachment*' if len(msgData['attachments']) > 0 else ''}"
                await message.channel.send(msg, files=files)

