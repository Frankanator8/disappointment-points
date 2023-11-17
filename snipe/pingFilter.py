from discord.utils import get


def filter_content(content, guild):
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
                filteredContent = f"{filteredContent}<@{get(guild.roles, id=int(ids[indexStartDeletions.index(index)][1:])).name}>"

            else:
                filteredContent = f"{filteredContent}<@{get(guild.members, id=int(ids[indexStartDeletions.index(index)])).display_name}>"

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