import time

import database


def add_points(id, amt):
    if not database.aprilfools.has_data(id=f"lt{id}"):
        database.aprilfools.add_data({"id":f"lt{id}", "pts":0, "time":0})
    database.aprilfools.update_inc("pts", amt, id=f"lt{id}")

def restrict_time(id):
    if not database.aprilfools.has_data(id=f"lt{id}"):
        database.aprilfools.add_data({"id":f"lt{id}", "pts":0, "time":0})
    database.aprilfools.update_data("time", time.time(), id=f"lt{id}")

def can_impersonate(id):
    if database.aprilfools.has_data(id=f"lt{id}"):
        elapsed = time.time() - database.aprilfools.find_one(id=f"lt{id}")["time"]

        cooldown = 1800
        if elapsed > cooldown:
            return (True, 0)

        else:
            return (False, round(cooldown-elapsed))

    else:
        return (True, 0)