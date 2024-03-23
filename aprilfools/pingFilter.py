from discord.utils import get


def filter_content(content):
    filteredContent = content.replace("@everyone", "(everyone ping)").replace("@here", "(here ping)")

    return filteredContent