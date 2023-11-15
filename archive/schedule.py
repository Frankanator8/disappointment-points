
        if command in ["postschedule", "ps"]:

            def checkGood(m, choices, channel):
                if m.channel.id != channel.id:
                    return False

                content = m.content
                if content == "N/A":
                    return True
                ans = content.split()
                try:
                    classID = ans[0]
                    level = ans[1]
                    teacher = ans[2]

                except IndexError:
                    return False

                try:
                    classId = int(classID) - 1
                    className = choices[classId]

                except (ValueError, IndexError):
                    for choice in choices:
                        if choice.lower() == classID.lower():
                            return True

                    return False

                if level.upper() not in ["AP", "H", "X", "A"]:
                    return False

                return True

            choices = [
                "Chem", "US History", "American Voices", "Calc", "Spanish",
                "French", "Other Language", "Seminar", "CS A", "CS P",
                "Music Course", "Alg 2", "Geometry", "Math Anal",
                "Other Course (e.g. Elective)"
            ]

            await message.channel.send("Please fill out the form in your dms.")
            try:
                if content.split()[2] == "as":
                    if message.author.id == 695290142721572935:
                        await message.channel.send(
                            f"Assuming identity of {message.mentions[0]}")
                        author = message.mentions[0]

                    else:
                        await message.channel.send(
                            "Function only available for <@695290142721572935>"
                        )

            except IndexError:
                pass

            channel = await message.author.create_dm()
            db["classData"][author.id] = []
            for i in range(8):
                await channel.send(
                    f"Please fill in your Period {i + 1} class. \nFormat should be: `classId` `level` `teacher's last name`. *Make sure to spell everything correctly, and within 60 seconds!*\n\nIf you have a free period, say `N/A`"
                )

                out = "Levels are: `AP`, `H`, `X`, or `A`\n\nClass IDs:"
                for index, choice in enumerate(choices):
                    out = f"{out}\n{index+1}. {choice}"

                await channel.send(out)

                try:
                    back_msg = await client.wait_for(
                        "message",
                        timeout=60.0,
                        check=lambda m: checkGood(m, choices, channel))
                    content = back_msg.content
                    if content == "N/A":
                        db["classData"][str(author.id)].append(
                            ("Free", "", ""))
                        await channel.send("Marked as Free Period")

                    else:
                        ans = content.split()
                        try:
                            classID = int(ans[0]) - 1

                        except ValueError:
                            for index, choice in enumerate(choices):
                                if choice.lower() == ans[0].lower():
                                    classID = index
                                    break
                        level = ans[1].upper()
                        teacher = ans[2].capitalize()
                        className = choices[classID]
                        choices.pop(classID)
                        db["classData"][str(author.id)].append(
                            (className, level, teacher))

                        await channel.send(
                            f"Your Period {i+1} class has been saved as {level} {className} with {teacher}"
                        )

                except asyncio.exceptions.TimeoutError:
                    await channel.send(f"Marking Period {i+1} as a Free Period"
                                       )
                    db["classData"][str(author.id)].append(("Free", "", ""))

            await channel.send(
                "Thanks for your time! To view your schedule, do `dis vs`")
            return

        if command in ["viewschedule", "vs"]:
            try:
                schedule = db["classData"][str(author.id)]

            except KeyError:
                await message.channel.send(
                    "You haven't specified your schedule yet")
                return

            out = "Your schedule is:"
            for period, classData in enumerate(schedule):
                name, level, teacher = classData
                out = f"{out}\n**{period+1}. {level} {name} ({teacher})**"
                shared = []
                for key, value in db["classData"].items():
                    try:
                        classForPeriod = value[period]
                        if classForPeriod[0] == name and classForPeriod[
                                1] == level and classForPeriod[2] == teacher:
                            if int(key) != message.author.id:
                                shared.append(int(key))

                    except IndexError:
                        pass

                sharedStr = "---> Shared with: "
                for person in shared:
                    sharedStr = f"{sharedStr} {get(SERVER.members, id=person).display_name}, "

                out = f"{out}\n{sharedStr}"
            await message.channel.send(out)
