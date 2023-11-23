import math
import discord
from discord.utils import get
import database
from activity.buttons import WeeklyButton, FullButton
from activity.pointscalc import get_required_points


class Leaderboard(discord.ui.View):
    def __init__(self, server, client):
        super().__init__()
        self.page = 0
        self.full = False
        self.weekly = True
        self.message = None
        self.server = server
        self.client = client
        self.database = database.weekActivity
        self.userData = []

        self.add_item(WeeklyButton(self))
        self.add_item(FullButton(self))

    async def update(self):
        try:
            self.userData = []
            for i in self.database.find():
                self.userData.append((i["id"], i["activity"], i["progress"]))

            self.userData.sort(key=lambda x: x[1]+x[2]/get_required_points(x[1]), reverse=True)
            out = ""
            for index, item in enumerate(self.userData[self.page*12:(self.page+1)*12]):
                index += self.page*12
                if index + 1 == 1:
                    placeText = ":first_place:"

                elif index + 1 == 2:
                    placeText = ":second_place:"

                elif index + 1 == 3:
                    placeText = ":third_place:"

                elif index + 1 in [4, 5]:
                    placeText = ":medal:"

                elif index + 1 in [6, 7, 8, 9, 10]:
                    placeText = ":bouquet:"

                else:
                    placeText = f"{index+1}."

                user = get(self.server.members, id=item[0])
                if self.full:
                    if user is None:
                        user = await self.client.fetch_user(item[0])
                    userStr = str(user)

                else:
                    try:
                        userStr = user.display_name

                    except AttributeError:
                        user = await self.client.fetch_user(item[0])
                        userStr = str(user)

                if isinstance(user, discord.User):
                    res = f"> {placeText} *{userStr}* | `{item[1]}`+`{round(item[2], 2)}`/`{get_required_points(item[1])}`\n"

                else:
                    res = f"> {placeText} **{userStr}** | `{item[1]}`+`{round(item[2], 2)}`/`{get_required_points(item[1])}`\n"

                out = f"{out}{res}"

            if out.strip() == "":
                out = "Nothing yet!"


            await self.message.edit(content=out, view=self)

        except Exception as e:
            print(repr(e))

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def backward(self, interaction: discord.Interaction,
                       button: discord.ui.Button):

        self.page -= 1
        if self.page < 0:
            self.page = 0

        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def forward(self, interaction: discord.Interaction,
                      button: discord.ui.Button):

        self.page += 1
        if self.page >= math.ceil(self.database.len()/12):
            self.page -= 1

        await self.update()
        await interaction.response.defer()
