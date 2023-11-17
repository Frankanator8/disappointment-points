import discord

def make_message(period, level, course, teacher):
    return f"Per {period+1}. {'' if level == 'N/A' else level} {course} {'' if level == 'N/A' else f'(teacher initial {teacher})'}"
    

class PeriodSelector(discord.ui.Select):
    def __init__(self, maker):
        super().__init__(placeholder=f"Changing period {maker.period+1}", options=[discord.SelectOption(label=str(i)) for i in range(1, 9)])
        self.maker = maker

    async def callback(self, interaction):
        await interaction.response.defer()
        self.maker.set_period(int(self.values[0])-1)
        await self.maker.update()
        


class LevelSelector(discord.ui.Select):
    def __init__(self, maker):
        super().__init__(placeholder="Level", options=[discord.SelectOption(label="AP/H*", default="AP/H*"==maker.level), discord.SelectOption(label="H", default="H"==maker.level), discord.SelectOption(label="X", default="X"==maker.level), discord.SelectOption(label="A", default="A"==maker.level), discord.SelectOption(label="N/A", default="N/A"==maker.level)])
        self.maker = maker

    async def callback(self, interaction):
        self.maker.level = self.values[0]
        await interaction.response.defer()
        await self.maker.update()

class CourseSelector(discord.ui.Select):
    def __init__(self, maker):
        super().__init__(placeholder="Course", options=[discord.SelectOption(label=i, default=maker.course==i) for i in maker.classes[:25]])
        self.maker = maker

    async def callback(self, interaction):
        await interaction.response.defer()
        self.maker.course = self.values[0]
        await self.maker.update()
                

class InitialSelector(discord.ui.Select):
    def __init__(self, maker):
        super().__init__(placeholder="Teacher's Last Initial (leave blank for A)", options=[discord.SelectOption(label=chr(i), default=maker.initial==chr(i)) for i in range(66, 91)], min_values=0)
        self.maker = maker

    async def callback(self, interaction):
        await interaction.response.defer()
        try:
            self.maker.initial = self.values[0]

        except IndexError:
            self.maker.initial = "A"
        
        await self.maker.update()


class PeriodFinalizer(discord.ui.Button):
    def __init__(self, maker):
        super().__init__(label="Done", emoji="✔️", style=discord.ButtonStyle.danger if maker.level == "()" or maker.course == "()" else discord.ButtonStyle.success, disabled=maker.level == "()" or maker.course == "()")
        self.maker = maker

    async def callback(self, interaction):
        await interaction.response.defer()
        self.maker.periods[self.maker.period] = (self.maker.level, self.maker.course, self.maker.initial)
        for index, period in enumerate(self.maker.periods):
            if period == ("()", "()", "A"):
                self.maker.set_period(index)
                await self.maker.update()
                return

        self.maker.set_period(0)
        await self.maker.update()

class Finalizer(discord.ui.Button):
    def __init__(self, maker):
        super().__init__(label="Finish Schedule", emoji="✅", style=discord.ButtonStyle.danger if any([i==("()", "()", "A") for i in maker.periods]) else discord.ButtonStyle.success, disabled=any([i==("()", "()", "A") for i in maker.periods]))
        self.maker = maker

    async def callback(self, interaction):
        await interaction.response.defer()
        self.maker.db["schedules"][interaction.user.id] = self.maker.periods
        self.maker.done = True
        await self.maker.update()

        

class ScheduleMaker(discord.ui.View):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.interaction = None

        self.periods = [("()", "()", "A")] * 8
        self.classes = [
            "Free Period",
            "English/Lang",
            "Spanish",
            "French",
            "German",
            "Latin",
            "Italian",
            "Research",
            "Government",
            "Comparative Government",
            "Psychology",
            "Chem 2",
            "Envi Sci",
            "Anat and Phys",
            "Physics",
            "CS A",
            "CS P",
            "Statistics",
            "Econ",
            "Multivariable Calculus",
            "Calculus",
            "Math Analysis",
            "Music Theory",
            "Music Course (Symphony Orchestra, Wind Ensemble, Concert Band, String Ensemble)",
            "Other Elective"
        ]

        self.period = 0
        self.level = "()"
        self.course = "()"
        self.initial = "A"
        self.done = False

    def set_period(self, period):
        self.period = period
        self.level = self.periods[self.period][0]
        self.course = self.periods[self.period][1]
        self.initial = self.periods[self.period][2]

    def make_message(self):
        if not self.done:
            msg = """
    Welcome to the Stoga Juniors Schedule Maker! Here, you can set your schedule so you can see who else shares it with you.
    
    Use the dropdown boxes below to choose the Period you'll be editing, the level of the course (N/A if inapplicable), the course itself (other elective if not available), and the teacher's last initial.
    
    Your current set schedule is:
    
            """
            for index, i in enumerate(self.periods):
                msg = f"{msg}\n{make_message(index, *i)}"
    
            msg = f"{msg}\n\nYour currently editing the following period:\n"
            msg = f"{msg}{make_message(self.period, self.level, self.course, self.initial)}"

        else:
            msg = "Thanks for setting your schedule! To see your schedule and how it compares to others, do the /schedule command again. If you'd like to change your schedule, do the /setschedule command."

        return msg


    async def update(self):
        self.clear_items()
        if not self.done:
            self.add_item(PeriodSelector(self))
            self.add_item(LevelSelector(self))
            self.add_item(CourseSelector(self))
            self.add_item(InitialSelector(self))
            
    
            self.add_item(PeriodFinalizer(self))
            self.add_item(Finalizer(self))

        embed=discord.Embed(title="Set Schedule",
                       color=0x0089D7,
                       description=self.make_message())
        
        await self.interaction.edit_original_response(view=self, embed=embed)
