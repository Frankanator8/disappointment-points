import dateparser

async def process_message(message, db):
    command = message.content.split()[1]
    if command in ["birthday", "b"]:
        if len(message.mentions) > 0:
            person = message.mentions[0]
            if str(person.id) not in db["locked"].keys():
                db["locked"][person.id] = False
                db["reminded"][person.id] = False
            
            if not db["locked"][str(person.id)]:
                try:
                    birthday = dateparser.parse(" ".join(message.content.split()[3:]))
                    if birthday is None:
                        await message.channel.send("Bad date, try again")
                        return
                    else:
                        db["birthdays"][person.id] = (birthday.month, birthday.day)
                        await message.channel.send(f"Birthday set as {birthday.month}/{birthday.day}")

                except IndexError:
                    await message.channel.send("Bad date, try again.")
                    return

            else:
                await message.channel.send("This person has locked their birthday")
                return

        else:
            if str(message.author.id) not in db["locked"].keys():
                db["locked"][message.author.id] = False
                db["reminded"][message.author.id] = False
            try:
                birthday = dateparser.parse(" ".join(message.content.split()[2:]))
                if birthday is None:
                    await message.channel.send("Bad date, try again")
                    return
                else:
                    db["birthdays"][message.author.id] = (birthday.month, birthday.day)
                    await message.channel.send(f"Birthday set as {birthday.month}/{birthday.day}")

            except IndexError:
                await message.channel.send("Bad date, try again.")
                return

    if command in ["lock"]:
        if str(message.author.id) not in db["locked"].keys():
            db["locked"][message.author.id] = False
            db["reminded"][message.author.id] = False

        db["locked"][str(message.author.id)] = not db["locked"][str(message.author.id)] 
        await message.channel.send(f"Set birthday lock to `{db['locked'][str(message.author.id)] }`")

    
            
        