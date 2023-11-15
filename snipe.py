import requests
from discord.utils import get
import discord


def filter_content(content, SERVER):
    content = list(content)

    id = ""
    inPing = False
    startingIndex = -1
    indexStartDeletions = []
    indexEndDeletions = []
    ids = []

    for index, i in enumerate(content):
        try:
            if f"{i}{content[index + 1]}" == "<@":
                inPing = True
                id = ""
                startingIndex = index

        except IndexError:
            pass

        if i == ">":
            if inPing:
                inPing = False
                try:
                    indexStartDeletions.append(startingIndex)
                    indexEndDeletions.append(index)
                    ids.append(id)

                except ValueError:
                    pass

                id = ""
                startingIndex = -1

        else:
            if inPing:
                if i != "@" and i != "<":
                    id = f"{id}{i}"

    filteredContent = ""
    for index, i in enumerate(content):
        if index in indexStartDeletions:
            if ids[indexStartDeletions.index(index)][0] == "&":
                filteredContent = f"{filteredContent}<@{get(SERVER.roles, id=int(ids[indexStartDeletions.index(index)][1:])).name}>"

            else:
                filteredContent = f"{filteredContent}<@{get(SERVER.members, id=int(ids[indexStartDeletions.index(index)])).display_name}>"

        else:
            if len(indexStartDeletions) > 0:
                for index2, start in enumerate(indexStartDeletions):
                    if index > start and index <= indexEndDeletions[index2]:
                        pass

                    else:
                        filteredContent = f"{filteredContent}{i}"

            else:
                filteredContent = f"{filteredContent}{i}"

    filteredContent = filteredContent.replace("@everyone", "(everyone ping)")
    filteredContent = filteredContent.replace("@here", "(here ping)")

    return filteredContent


async def snipeCommand(message, db, SERVER):
    if message.channel.id == 936716274833162322:
        return
    try:
        list = False
        try:
            hist = int(message.content.split()[2])-1

        except IndexError:
            hist = 0

        except ValueError:
            if message.content.split()[2] == "list":
                list=True

            else:
                hist = 0

        if not list:
            if hist >= len(db["snipe"][str(message.channel.id)]):
                await message.channel.send("Not that many snipe messages")
                return
    
            author, content = db["snipe"][str(message.channel.id)][hist]
            channel = message.channel
            author = SERVER.get_member(int(author))
    
            avatar = requests.get(author.avatar).content
    
            try:
                webhook = await channel.create_webhook(name=author.display_name,
                                                       avatar=avatar,
                                                       reason="snipe message")
    
            except discord.errors.HTTPException:
                hooks = await SERVER.webhooks()
                for hook in hooks:
                    if hook.user.id == 896123313389178921:
                        await hook.delete()
    
                webhook = await channel.create_webhook(name=author.display_name, avatar=avatar, reason="snipe message")
    
            if content == "":
                await webhook.send("*message content empty. perhaps it was an image*")
    
            else:
                await webhook.send(content)
            await webhook.delete()

        else:
            if len(db["snipe"][str(message.channel.id)]) == 0:
                msg = "There are no snipe messages in this channel"
            else:
                msg = "From most recent to least recent:\n"
            for index, msgData in enumerate(db["snipe"][str(message.channel.id)]):
                author, content = msgData
                msg = f"{msg}\n{index+1}. **{SERVER.get_member(int(author)).display_name}**: {content if content!='' else '*message content empty. perhaps it was an image*'}"
            await message.channel.send(msg)

    except KeyError:
        pass
