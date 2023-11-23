import math


def get_total_activity_points(activity, progress):
    total = 0
    for i in range(activity):
        total += get_required_points(i)
    total += progress

    return total


def get_required_points(activity_points):
    if activity_points <= 125:
        k = 0.065
        x0 = 33
        ret = 48 / (1 + math.e**(-k * (activity_points - x0)))

    else:
        ret = ((-1.025)**(-(activity_points - 285))) + 100

    return round(ret)


def add_progress_points(activity, progress, progressToAdd):
    progress += progressToAdd
    while True:
        req = get_required_points(activity)
        if progress >= req:
            activity += 1
            progress -= req

        else:
            break

    return activity, progress


def total_to_activity_and_progress(total):
    act_points = 0
    remaining = total
    while True:
        next = get_required_points(act_points)
        if remaining >= next:
            act_points += 1
            remaining -= next

        else:
            break

    return act_points, remaining