import requests

import database
from commandset import CommandSetManager


class MiscManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["prefix", "sync", "pfp"])

    async def on_message(self, message):
        if self.is_my_message(message):
            command = message.content.split()[1]
            if command in ["prefix"]:
                try:
                    pref = message.content.split()[2]
                    if database.prefixes.has_data(id=message.author.id):
                        database.prefixes.update_data("prefix", pref, id=message.author.id)

                    else:
                        database.prefixes.add_data({"id":message.author.id, "prefix":pref})

                    await message.channel.send(
                        f"Prefix set to `{pref}`. Note `dis` still works!")

                except IndexError:
                    await message.channel.send("No prefix provided")

            if command in ["sync"]:
                if message.author.id == 695290142721572935:
                    fmt = await self.client.tree.sync()
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
                    await self.server.edit(icon=img)

                await message.channel.send("Changed server icon!")
                return