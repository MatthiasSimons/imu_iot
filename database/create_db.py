import datetime
#import paho.mqtt.client as mqtt
import json
import calendar
from pymongo import MongoClient

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient("localhost:27017")
db = client.monitoring
collection = db.trainings_data

msg = {"key": "value"}
collection.insert_one(msg)
