import database
from activity.pointscalc import add_progress_points


def add_points_overall(user, points):
    if not database.activity.has_data(id=user):
        database.activity.add_data({"id":user, "activity":3, "progress":0})

    userData = database.activity.find_one(id=user)
    activity, progress = add_progress_points(userData["activity"], userData["progress"], points)
    userData["progress"] = progress
    userData["activity"] = activity

    database.activity.update_data("progress", userData["progress"], id=user)
    database.activity.update_data("activity", userData["activity"], id=user)

def add_points_weekly(user, points):
    if not database.weekActivity.has_data(id=user):
        database.weekActivity.add_data({"id":user, "activity":3, "progress":0})

    userData = database.weekActivity.find_one(id=user)
    activity, progress = add_progress_points(userData["activity"], userData["progress"], points)
    userData["progress"] = progress
    userData["activity"] = activity

    database.weekActivity.update_data("progress", userData["progress"], id=user)
    database.weekActivity.update_data("activity", userData["activity"], id=user)