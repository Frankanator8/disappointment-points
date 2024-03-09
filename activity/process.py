import time
import traceback

import database
from activity.activityDb import add_points_overall, add_points_weekly
from activity.pointscalc import get_required_points

BLACKLISTED_CHANNELS = [
    975925480882585610
]
def process_message(message):
    author = message.author
    content = message.content
    if time.time() - database.activityData.find_one(fId="week_time")["time"] > 604800:
        database.activityData.update_data("time", round(time.time()), fId="week_time")
        database.weekActivity.delete_many()

    if not database.activity.has_data(id=author.id):
        database.activity.add_data({"id":author.id, "activity":3, "progress":0})

    if not database.weekActivity.has_data(id=author.id):
        database.weekActivity.add_data({"id":author.id, "activity":3, "progress":0})

    if message.channel.id not in BLACKLISTED_CHANNELS and content not in database.activityData.find_one(fId="messages")["msgs"]:
        database.activityData.add_list("msgs", content, fId="messages")
        if not database.activityData.has_data(fId="messageCount", id=author.id):
            database.activityData.add_data({"fId":"messageCount", "id":author.id, "count":0})

        database.activityData.update_inc("count", 1, fId="messageCount", id=author.id)

    if len(database.activityData.find_one(fId="messages")["msgs"]) >= 100:
        try:
            for count in database.activityData.find(fId="messageCount"):
                add_points_overall(count["id"], 1 + round((count["count"]-1) / 100, 2))
                add_points_weekly(count["id"], 1 + round((count["count"]-1) / 100, 2))

            database.activityData.delete_many(fId="messageCount")
            database.activityData.update_data("msgs", [], fId="messages")

        except Exception as e:
            print(traceback.format_exc())
