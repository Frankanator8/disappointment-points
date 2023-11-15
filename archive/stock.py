		if command in ["bal", "balance"]:
			try:
				balance = db["money"][str(author.id)]

			except KeyError:
				await message.channel.send(
				    f"You haven't started yet! Do `{prefix} start`")
				return

			stocks = []

			for owner, stock in db["stocks"].items():
				if author.id in stock["investors"]:
					stocks.append((owner, stock["shares"][str(author.id)]))

			net_worth = balance
			stock_str = ""
			for owner, shares in stocks:
				net_worth += db["stocks"][owner]["value"] * shares
				stock_str = f"{stock_str}{get(SERVER.members, id=int(owner)).display_name} - {shares}\n"

			embed = discord.Embed(
			    title="Your Balance",
			    color=0x0089D7,
			    description=f"Balance: ${balance}\nNet Worth: ${net_worth}")

			if stock_str != "":
				embed.add_field(name="Stock Shares", value=stock_str)
			await message.channel.send(embed=embed)

		if command in ["start", "s"]:
			if str(author.id) in db["money"].keys():
				await message.channel.send("You already have an account!")
				return

			currentTime = datetime.datetime.now()
			if currentTime.hour < 9 or currentTime.hour > 21:
				await message.channel.send(
				    "The stock market is closed. It is open from 9 AM to 9:59 PM."
				)
				return

			embed = discord.Embed(
			    title="Welcome!",
			    color=0x0089D7,
			    description="Welcome to the Stoga Sophomores Stock Exchange!")
			embed.add_field(
			    name="Getting Started",
			    value=
			    f"You have been given $100. There is now also a stock attached to your name, currently with 100 shares, each worth $10.\nIf you want to see other people's stocks, do `{prefix} view`"
			)

			embed.add_field(
			    name="Buying/selling stocks",
			    value=
			    f"If you're interested in buying somebody's stock, just do `{prefix} buy <ping> <share amount>`.\n Stock share value updates every 30 minutes. Stock share value is based on <amount of messages today>/<half-hours since day started> / <total amount of shares>.\nIf you want to sell your stock, just do `{prefix} sell <ping> <share amount>`."
			)
			embed.add_field(
			    name="Winning",
			    value=
			    "The Stock Market will close on September 21, 2022. Your final net worth will be YOUR BALANCE, so it is advised to sell all your stock beforehand.\nPrize is a piece of paper acknowleding you are the greatest by the one and only Raphie Lubiniecki"
			)

			db["money"][author.id] = 100
			db["stocks"][author.id] = {
			    "investors": [],
			    "shares": {},
			    "value": 10,
			    "total_shares": 100
			}
			await message.channel.send(embed=embed)

		if command in ["view", "v"]:
			if str(author.id) not in db["money"].keys():
				await message.channel.send(
				    f"You haven't started yet! Do `{prefix} start` to start!")
				return

			embed = discord.Embed(title="Stocks",
			                      color=0x0089D7,
			                      description="Here are all the stocks.")
			for owner, stock in db["stocks"].items():
				sharesTaken = 0
				for amt in stock["shares"].values():
					sharesTaken += amt

				investor_names = []
				for investor in stock["investors"]:
					investor_names.append(
					    get(SERVER.members, id=int(investor)).display_name)

				stock_info = f"**Value**: ${stock['value']}\n**Shares Remaining**:{humanize.intword(stock['total_shares'] - sharesTaken)}\n**Investors**:{','.join(investor_names)}"
				embed.add_field(name=get(SERVER.members, id=int(owner)),
				                value=stock_info,
				                inline=False)

			await message.channel.send(embed=embed)

		if command in ["buy"]:
			if str(author.id) not in db["money"].keys():
				await message.channel.send(
				    f"You haven't started yet! Do `{prefix} start` to start!")
				return

			currentTime = datetime.datetime.now()
			if currentTime.hour < 9 or currentTime.hour > 21:
				await message.channel.send(
				    "The stock market is closed. It is open from 9 AM to 9:59 PM."
				)
				return

			try:
				buy_who = message.mentions[0]

			except IndexError:
				await message.channel.send("Specify a stock to buy")
				return

			if str(buy_who.id) not in db["money"].keys():
				await message.channel.send("This person doesn't have a stock.")
				return

			sharesTaken = 0
			for amt in db["stocks"][str(buy_who.id)]["shares"].values():
				sharesTaken += amt

			sharesLeft = db["stocks"][str(
			    buy_who.id)]["total_shares"] - sharesTaken

			try:
				buy_amt = int(message.content.split()[3])
				if not (buy_amt > 0 and buy_amt <= sharesLeft):
					await message.channel.send(
					    f"You bought too many shares! Max is {sharesLeft}.")
					return

			except IndexError:
				await message.channel.send("Did not specify how much to buy")
				return

			except ValueError:
				message.channel.send("Invalid number of shares.")
				return

			money_needed = db["stocks"][str(buy_who.id)]["value"] * buy_amt
			if db["money"][str(author.id)] < money_needed:
				await message.channel.send(
				    "You don't have enough money to do that")
				return

			if author.id not in db["stocks"][str(buy_who.id)]["investors"]:
				db["stocks"][str(buy_who.id)]["investors"].append(author.id)

			if author.id not in db["stocks"][str(buy_who.id)]["shares"].keys():
				db["stocks"][str(buy_who.id)]["shares"][author.id] = 0

			db["stocks"][str(buy_who.id)]["shares"][str(author.id)] += buy_amt
			db["money"][str(author.id)] -= money_needed

			await message.channel.send(
			    f"Successfully bought {buy_amt} shares of {buy_who.display_name}'s stock."
			)

		if command in ["sell"]:
			if str(author.id) not in db["money"].keys():
				await message.channel.send(
				    f"You haven't started yet! Do `{prefix} start` to start!")
				return

			currentTime = datetime.datetime.now()
			if currentTime.hour < 9 or currentTime.hour > 21:
				await message.channel.send(
				    "The stock market is closed. It is open from 9 AM to 9:59 PM."
				)
				return

			try:
				sell_who = message.mentions[0]

			except IndexError:
				await message.channel.send("Specify a stock to buy")
				return

			if str(sell_who.id) not in db["money"].keys():
				await message.channel.send("This person doesn't have a stock.")
				return

			try:
				sell_amt = int(message.content.split()[3])

			except IndexError:
				await message.channel.send("Did not specify how much to buy")
				return

			except ValueError:
				message.channel.send("Invalid number of shares.")
				return

			if author.id not in db["stocks"][str(sell_who.id)]["investors"]:
				await message.channel.send("You didn't invest in this stock!")
				return

			if db["stocks"][str(sell_who.id)]["shares"][str(
			    author.id)] < sell_amt:
				await message.channel.send(
				    f"You only have {db['stocks'][str(sell_who.id)]['shares'][str(author.id)]} shares."
				)
				return

			db["stocks"][str(sell_who.id)]["shares"][str(
			    author.id)] -= sell_amt
			if db["stocks"][str(sell_who.id)]["shares"][str(author.id)] == 0:
				del db["stocks"][str(sell_who.id)]["shares"][str(author.id)]
				db["stocks"][str(sell_who.id)]["investors"].remove(author.id)

			db["money"][str(author.id)] += db["stocks"][str(
			    sell_who.id)]["value"] * sell_amt

			await message.channel.send(
			    f"Successfully sold {sell_amt} shares of {sell_who.display_name}'s stock."
			)

		if command in ["expand", "publicoffering", "po", "fpo"]:

			def check_good(m):
				if m.content.lower() in ["y", "n"]:
					return True

				else:
					return False

			if str(author.id) not in db["money"].keys():
				await message.channel.send(
				    f"You haven't started yet! Do `{prefix} start` to start!")
				return

			currentTime = datetime.datetime.now()
			if currentTime.hour < 9 or currentTime.hour > 21:
				await message.channel.send(
				    "The stock market is closed. It is open from 9 AM to 9:59 PM."
				)
				return

			try:
				amt = int(message.content.split()[2])

			except IndexError:
				await message.channel.send(
				    "Specify how many shares you want to add")
				return

			except ValueError:
				await message.channel.send("Invalid amount of shares")
				return

			if amt < 1:
				await message.channel.send(
				    "You must increase the amount of total shares by at least 1."
				)
				return

			await message.channel.send(
			    "Increasing the total amount of shares will cause your stock value to significantly drop. Continue? (y/n)"
			)

			if db["stocks"][str(
			    author.id)]["total_shares"] + amt > 1_000_000_000:
				await message.channel.send(
				    "You can only have a maximum of 1 Billion shares per stock."
				)
				return

			try:
				back_msg = await client.wait_for("message",
				                                 timeout=15.0,
				                                 check=lambda m: check_good(m))

			except asyncio.exceptions.TimeoutError:
				await message.channel.send("Aborted")
				return

			if back_msg.content.lower() == "n":
				await message.channel.send("Aborted")
				return

            db["stocks"][str(author.id)]["total_shares"] += amt
            await message.channel.send(f"Added {amt} shares to your stock.")