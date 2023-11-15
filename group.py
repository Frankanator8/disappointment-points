from discord import ChannelType, Thread

async def process_message(message, db, client):
    if message.content.split()[1] == "group":
        group_name = " ".join([x for x in message.content.split()[2:] if "<@" not in x])
        people = message.mentions

        if group_name != "":
            channel = client.get_channel(1078794964634439731)
            thread = await channel.create_thread(
    name=group_name,
    type=ChannelType.public_thread
)
            msg = await thread.send(f"If you're interested in the `{group_name}` group, type something here!\n\nPeople interested (need 5 to make official):\n1.{message.author.mention}")

            ping = "Possible people interested: "
            for user in people:
                ping = f"{ping}{user.mention}"

            await thread.send(ping)

            db["groups"][thread.id] = [[message.author.id], msg.id]

        else:
            await message.channel.send("Provide a group name")
            return

async def check_group(message, db, SERVER):
    if type(message.channel) == Thread:
        thread = message.channel
        if str(thread.id) in db["groups"].keys():
            if message.author.id not in db["groups"][str(thread.id)][0]:
                db["groups"][str(thread.id)][0].append(message.author.id)

            change = f"If you're interested in the `{thread.name}` group, type something here!\n\nPeople interested (need 5 to make official):\n"
            for index, i in enumerate(db["groups"][str(thread.id)][0]):
                change = f"{change}{index+1}. {SERVER.get_member(int(i)).mention}\n"

            msgChange = await thread.fetch_message(db["groups"][str(thread.id)][1])
            await msgChange.edit(content=change)


            if len(db["groups"][str(thread.id)][0]) >= 5:
                group_name = thread.name
                role = await thread.guild.create_role(name=group_name)
                for i in db["groups"][str(thread.id)][0]:
                    await SERVER.get_member(int(i)).add_roles(role)

                await role.edit(mentionable=True)

                react_msg = await SERVER.get_channel(1078809175024472135).send(f"**{group_name}** - If you are in this group, react below.")

                await SERVER.get_channel(956400571269664789).send(f"?rr add \\<#1078809175024472135> {react_msg.id} \\:white_check_mark: \\{role.mention}")
                await SERVER.get_channel(956400571269664789).send(f"<@&887131644140613662> <@&887100753255215124> Copy paste the above!")

                await thread.delete()

                del db["groups"][str(thread.id)]
                
            
        
        