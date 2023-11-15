import discord
import time
from discord.utils import get


class CandidateButton(discord.ui.Button):
    def __init__(self, candidate, voting, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.candidate = candidate
        self.voting = voting

    async def callback(self, interaction):
        self.voting.vote.append(self.candidate)

        await self.voting.update()
        await interaction.response.defer()

class Voting(discord.ui.View):
    def __init__(self, authorId, message, db):
        super().__init__()
        self.message = message
        self.db = db
        self.authorID = authorId
        self.agreed_to_TOS = False
        self.page = 0
        self.lastViewed = 0
        self.vote = []
        self.candidates = ['Asish', 'Declan', 'Dylan', 'Ethan G', 'Gavin', 'Jeffrey W', 'Juliana', 'Kevin', 'Matthew F', 'Oliver', 'Vaish']

        self.statements = {
            "Asish":"Asish for Discord Supreme! 🌟 Longtime server maestro, always active. Elevate your Discord experience with Asish's expertise. Vote for stability, vote for Asish!",
            "Declan":"Declan for Discord Justice! ⚖️ A stalwart guardian of fairness, active and vigilant. Empower your server with Declan's commitment to justice. Vote Declan for harmony!",
            "Dylan":"Dylan for Discord Brilliance! 🧠 Sharp mind, active presence. Transform your server with Dylan's intelligence. Vote for innovation, vote for Dylan – where smarts meet synergy!",
            "Ethan G":"Ethan G for Discord Comedy King! 😂 Unleash the laughter, active wit guaranteed. Elevate your server with Ethan G's humor. Vote joy, vote Ethan G – where fun reigns!",
            "Gavin":"Gavin for Discord Gaming Guru! 🎮 Level up your server with Gavin's gaming prowess. Active, strategic, and fun. Vote Gavin for the ultimate gaming experience! #GavinGamingMaster",
            "Jeffrey W":"Jeffrey for Discord Genius in 11th Grade! 📚 Elevate your server with Jeffrey's academic flair. Active, insightful, and always in the know. Vote Jeffrey for scholarly vibes!",
            "Juliana":"Juliana, Fresh and Ready! 🌟 New to the server but bringing positive vibes. Embrace the energy of a new beginning. Vote Juliana for a vibrant community!",
            "Kevin":"Kevin, Discord Conservator! 🌐 Advocating tradition and stability. Active voice for conservative values. Choose Kevin for a server rooted in principles. #KevinForConservativeUnity",
            "Matthew F":"Matthew Fang, the Musical Maestro of Discord! 🎶 Let the notes of brilliance resonate. Active, harmonious, and ready to elevate your server. Vote Matthew for a symphony of excellence!",
            "Oliver":"Oliver, the British Charm on Discord! 🎩 Active and adding a touch of UK flair. Elevate your server with Oliver's wit and sophistication. Vote British, vote Oliver!",
            "Vaish":"Vaish – The Epitome of Cool on Discord! 😎 Always active, forever cool. Elevate your server's vibes with Vaish. Vote for the ultimate cool factor!"
        }

        for candidate in self.candidates:
            self.add_item(CandidateButton(candidate, self, label=candidate, style=discord.ButtonStyle.green))

    async def update(self):
        action_button = None
        for child in self.children:
            if child.label == ":)":
                child.label = ":)"
                child.style = discord.ButtonStyle.secondary

                action_button = child

            elif child.label == "X":
                action_button = child

            elif child.label == "✓":
                action_button = child

        new_embed = self.message.embeds[0]
        if self.page == 0:
            msg = "Welcome to the Stoga Sophomores Co-Founder Election. Please click the >` button to continue."
            for child in self.children:
                if child.label != ">":
                    if not self.agreed_to_TOS:
                        child.disabled = True

                    else:
                        if child.label in self.vote:
                            child.disabled = True

                        else:
                            child.disabled = False

            new_embed.description = msg
            action_button.label = ":)"
            action_button.style = discord.ButtonStyle.primary

        elif self.page == 1:
            msg = """By continuing in the vote, you agree to the following:

    Frank Liu (I) can revoke your vote at any moment
    I can question the integrity of your vote at any time
    You will not attempt to illegally influence the vote
    You have not influenced others to sacrifice the integrity of the vote
    You affirm that your vote is your vote, and nobody else's
    You agree that I can change these rules at my discretion given the circumstances"""
            for child in self.children:
                if child.label not in [">", "<"]:
                    if not self.agreed_to_TOS:
                        child.disabled = True

                    else:
                        if child.label in self.vote:
                            child.disabled = True
    
                        else:
                            child.disabled = False

                else:
                    child.disabled = False

            new_embed.description = msg
            action_button.label = ":)"
            action_button.style = discord.ButtonStyle.primary

        elif self.page == 2:
            msg = """Controls:
            `<<` - Back to candidate statement you left off on
            `<` - Last page
            `:)` or `X` or `✓` - Action button. Can either do nothing, clear vote, or submit vote, respectively
            `>` - Next page
            `>>` - Go to the voting page
            """
            new_embed.description = msg
            action_button.label = ":)"
            action_button.style = discord.ButtonStyle.primary
            for child in self.children:
                if not self.agreed_to_TOS:
                    child.disable = True

                else:
                    if child.label in self.vote:
                        child.disabled = True

                    else:
                        child.disabled = False

        elif self.page >= 3 and self.page < 3+len(self.candidates):
            msg = f"**{self.candidates[self.page-3]}'s Candidate Statement**\n\n"
            try:
                statement = self.statements[self.candidates[self.page-3]]
            except KeyError:
                statement = "TBD"
            msg = f"{msg}{statement}"
            new_embed.description = msg
            action_button.label = ":)"
            action_button.style = discord.ButtonStyle.primary

            for child in self.children:
                if not self.agreed_to_TOS:
                    child.disabled = True

                else:
                    if child.label in self.vote:
                        child.disabled = True

                    else:
                        child.disabled = False

        elif self.page == 3+len(self.candidates):
            msg = """
            Welcome to the voting page. Here is how voting works:
            This is a ranked voting system, means you will sorta vote for everyone. However, how many points you give them differ.

            In the order of your most favorite to your least, press the buttons of your choices.

            If you want to clear your selection, press the `X` button.

            Once you are done, press `>`

            Current vote:
            """
            for index, vote in enumerate(self.vote):
                msg = f"{msg}\n{index+1}. {vote}"
            
            action_button.label = "X"
            action_button.style = discord.ButtonStyle.danger
            new_embed.description = msg
            for child in self.children:
                if not self.agreed_to_TOS:
                    child.disabled = True

                else:
                    if child.label in self.vote:
                        child.disabled = True

                    else:
                        child.disabled = False

        elif self.page == 3+len(self.candidates)+1:
            msg = """
            If you are happy with your ranking, press the check mark to submit and finish your vote. You cannot return after this page. Your current vote:
            """
            for index, vote in enumerate(self.vote):
                msg = f"{msg}\n{index+1}. {vote}"

            action_button.label = "✓"
            action_button.style = discord.ButtonStyle.danger
            new_embed.description = msg
            for child in self.children:
                if not self.agreed_to_TOS:
                    child.disabled = True

                else:
                    if child.label in self.vote:
                        child.disabled = True

                    else:
                        if child.label != ">":
                            child.disabled = False

                        else:
                            child.disabled = True

        elif self.page ==3+len(self.candidates)+2:
            msg = """
            Thank you for voting! If at any point you want to see your vote, do `dis vote` (or your prefix) again!
            """
            action_button.label = ":)"
            action_button.style = discord.ButtonStyle.primary
            new_embed.description = msg
            for child in self.children:
                child.disabled = True
            

        await self.message.edit(view=self, embed=new_embed)

    @discord.ui.button(label='<<', style=discord.ButtonStyle.blurple)
    async def skipToFront(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self.agreed_to_TOS:
            self.page = self.lastViewed

        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def backward(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        
        if self.page != 0:
            self.page -= 1

        if self.page >= 3 and self.page < 3+len(self.candidates):
            self.lastViewed = self.page

                    
                           
        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label=':)', style=discord.ButtonStyle.blurple)
    async def action(self, interaction: discord.Interaction,
                     button: discord.ui.Button):

        if button.label == ":)":
            pass

        elif button.label == "X":
            self.vote = []

        else:
            self.db["votes"][self.authorID] = self.vote
            self.page = 3+len(self.candidates)+2

        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def forward(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        if self.page == 1:
            self.agreed_to_TOS = True
        self.page += 1
        if self.page >= 3 and self.page < 3+len(self.candidates):
            self.lastViewed = self.page
        await self.update()
        await interaction.response.defer()

    @discord.ui.button(label='>>', style=discord.ButtonStyle.blurple)
    async def skipToBack(self, interaction: discord.Interaction,
                         button: discord.ui.Button):

        if self.agreed_to_TOS:
            self.page = 3+len(self.candidates)

        await self.update()
        await interaction.response.edit_message()
                             

async def process_command(message, db):
    command = message.content.split()[1]
    if command in ["vote", "v"]:
        channel = await message.author.create_dm()
        await message.add_reaction("👍")
        if str(message.author.id) in db["votes"].keys():
            msg = "Your vote was:"
            
            for index, vote in enumerate(db["votes"][str(message.author.id)]):
                msg = f"{msg}\n{index+1}. {vote}"

        
            await channel.send(msg)
                

        else:
            embed = discord.Embed(
                title="Voting",
                color=0x0089D7,
                description=
                "Welcome to the Stoga Sophomores November Election. By participating, you agree to the [terms and conditions](https://disappointment-points.frankanator433.repl.co/ballottoc)"
            )
            voter = Voting(message.author.id, None, db)
            msg = await channel.send(embed=embed, view=voter)
            voter.message = msg
            await voter.update()

    if command in ["analyze"]:
        if message.author.id == 695290142721572935:
            voteCount = {}
            for key in db["votes"].keys():
                for index, person in enumerate(db["votes"][key]):
                    if person not in voteCount.keys():
                        voteCount[person] = 0

                    voteCount[person] += len(self.candidates) - index

            out = ""
            translate = {
                'Asish':643953075798933544, 'Declan':674367708971794483, 'Dylan':612067775388581899, 'Ethan G':873370390100049931, 'Gavin':475791868777594902, 'Jeffrey W':480879708364472347, 'Juliana':1115719653382180936, 'Kevin':712801780936998993, 'Matthew F':710265799700643911, 'Oliver':381471603869089792, 'Vaish':457630638388805633
            }
            
            
            for key, value in voteCount.items():
                member = get(message.guild.members, id=translate[key])
                out = f"{out}{member} - {value}\n"

            channel = await message.author.create_dm()
            await channel.send(out)
            await message.add_reaction("👍")
            return
                

        else:
            await message.channel.send("Only <@695290142721572935> can do this.")
            return

    if command in ["rmv"]:
        if message.author.id == 695290142721572935:
            person = message.mentions[0]
            del db["votes"][str(person.id)]
            await message.channel.send(f"Successfully removed {person}'s vote'")
