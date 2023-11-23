import json

import certifi
import pymongo as pymongo
import os

ca = certifi.where()

client = pymongo.MongoClient(f"mongodb+srv://Frankanator8:{os.getenv('DB_PASS')}@boardgamebot.nl1pe.mongodb.net/?retryWrites=true&w=majority")

client.admin.command('ping')
print("Connected to database")


class Database:

    def __init__(self, database, collection):
        self.db = client[database][collection]

    def add_data(self, data):
        self.db.insert_one(data)

    def append_data(self, data):
        self.add_data(data)

    def has_data(self, **search):
        return self.db.count_documents(search) != 0

    def find_data(self, **search):
        return self.db.find_one(search)

    def find_one(self, **search):
        return self.find_data(**search)

    def find(self, **search):
        return self.db.find(search)

    def fill_data(self, otherDb, func):
        for document in otherDb.find():
            self.add_data(func(document["uuid"]))

    def update_data(self, key, value, **search):
        self.db.update_one(search, {"$set":{key: value}})

    def update_inc(self, key, value, **search):
        self.db.update_one(search, {"$inc":{key: value}})

    def pop_list(self, key, front=True, **search):
        self.db.update_one(search, {"$pop":{key: -1 if front else 1}})

    def add_list(self, key, item, **search):
        self.db.update_one(search, {"$push":{key: item}})

    def delete_data(self, **search):
        self.db.delete_one(search)

    def delete_many(self, **search):
        self.db.delete_many(search)

    def len(self):
        return self.db.count_documents({})

activity = Database("disappointmentpoints", "activity")
weekActivity = Database("disappointmentpoints", "weekactivity")
activityData = Database("disappointmentpoints", "activitydata")
announcement = Database("disappointmentpoints", "announcement")
prefixes = Database("disappointmentpoints", "prefixes")
birthday = Database("disappointmentpoints", "birthday")
schedule = Database("disappointmentpoints", "schedule")
snipe = Database("disappointmentpoints", "snipe")
vote = Database("disappointmentpoints", "vote")
