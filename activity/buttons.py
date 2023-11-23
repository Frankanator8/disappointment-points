import discord
import database
class WeeklyButton(discord.ui.Button):
    def __init__(self, lb):
        super().__init__(label=f"{'Weekly' if lb.weekly else 'Lifetime'} (click to toggle)", style=discord.ButtonStyle.success)
        self.lb = lb

    async def callback(self, interaction):
        lb = self.lb
        await interaction.response.defer()
        lb.weekly = not lb.weekly

        lb.database = database.weekActivity if lb.weekly else database.activity
        lb.page = 0
        self.label = f"{'Weekly' if lb.weekly else 'Lifetime'} (click to toggle)"

        await lb.update()


class FullButton(discord.ui.Button):
    def __init__(self, lb):
        super().__init__(label=f"{'Full username' if lb.full else 'Nicknames'} (click to toggle)", style=discord.ButtonStyle.success)
        self.lb = lb

    async def callback(self, interaction):
        await interaction.response.defer()
        lb = self.lb
        lb.full = not lb.full
        self.label = f"{'Full username' if lb.full else 'Nicknames'} (click to toggle)"
        await lb.update()