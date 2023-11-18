import datetime

import dateparser
from discord.utils import get

import database
from commandset import CommandSetManager


class BirthdayManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["birthday", "b", "lock"])
        self.waitTime = 0

    async def on_message(self, message):
        if self.is_my_message(message):
            command = message.content.split()[1]
            if command in ["birthday", "b"]:
                if len(message.mentions) > 0:
                    person = message.mentions[0]
                    if not database.birthday.has_data(id=person.id) or not database.birthday.find_one(id=person.id)["locked"]:
                        try:
                            birthday = dateparser.parse(" ".join(message.content.split()[3:]))
                            if birthday is None:
                                if database.birthday.has_data(id=person.id):
                                    bday = database.birthday.find_one(id=person.id)
                                    await message.channel.send(f"{person.mention}'s birthday is {bday['month']}/{bday['day']}")

                                else:
                                    await message.channel.send(f"{person.mention}'s birthday hasn't been set! Do `dis birthday @[{person.display_name}] [date]` to set it for them!")

                                return
                            else:
                                if database.birthday.has_data(id=person.id):
                                    database.birthday.update_data("month", birthday.month, id=person.id)
                                    database.birthday.update_data("day", birthday.day, id=person.id)

                                else:
                                    database.birthday.add_data({"id":person.id, "month":birthday.month, "day":birthday.day, "locked":False, "reminded":False})

                                await message.channel.send(f"{person.mention}'s birthday set as {birthday.month}/{birthday.day}")

                        except IndexError:
                            if database.birthday.has_data(id=person.id):
                                bday = database.birthday.find_one(id=person.id)
                                await message.channel.send(f"{person.mention}'s birthday is {bday['month']}/{bday['day']}")

                            else:
                                await message.channel.send(f"{person.mention}'s birthday hasn't been set! Do `dis birthday @{person.display_name} [date]` to set it for them!")
                            return

                    else:
                        await message.channel.send("This person has locked their birthday")
                        return

                else:
                    try:
                        birthday = dateparser.parse(" ".join(message.content.split()[2:]))
                        if birthday is None:
                            await message.channel.send("Bad date, try again")
                            return
                        else:
                            if database.birthday.has_data(id=message.author.id):
                                database.birthday.update_data("month", birthday.month, id=message.author.id)
                                database.birthday.update_data("day", birthday.day, id=message.author.id)

                            else:
                                database.birthday.add_data({"id":message.author.id, "month":birthday.month, "day":birthday.day, "locked":False, "reminded":False})

                            await message.channel.send(f"Birthday set as {birthday.month}/{birthday.day}")

                    except IndexError:
                        await message.channel.send("Bad date, try again.")
                        return

            if command in ["lock"]:
                if database.birthday.has_data(id=message.author.id):
                    currentLock = database.birthday.find_one(id=message.author.id)["locked"]
                    database.birthday.update_data("locked", not currentLock, id=message.author.id)
                    await message.channel.send(f"Set birthday lock to `{not currentLock}`")

                else:
                    await message.channel.send("Your birthday is not registered! Do `dis birthday [date]` to set it, then lock it!")

    async def on_tick(self, dt):
        self.waitTime += dt
        if self.waitTime > 15:
            try:
                self.waitTime = 0
                month = datetime.datetime.now().month
                day = datetime.datetime.now().day
                hour = datetime.datetime.now().hour

                for person in database.birthday.find():
                    if person["month"] == month and person["day"] == day and hour > 11: # 7 AM, +4 hrs because GMT
                        if not person["reminded"]:
                            await get(self.server.channels, id=901224829598969916).send(f"Happy birthday, {get(self.server.members, id=person['id']).mention}!")
                            database.birthday.update_data("reminded", True, id=person["id"])

            except Exception as e:
                print(repr(e))