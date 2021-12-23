from pymongo import MongoClient
import socket

####### db
client = MongoClient("localhost:27017")
db = client.monitoring
collection = db.trainings_data
####### db

csv_path = "test_csv.csv"#"../client/imu.csv"
label = "test"

with open(csv_path) as csv:
    row_counter = 0
    for row in csv:
        if row_counter > 0:
            data = row.replace("\n", "").split(";") # auf , anpassen im Programm
            data_dic = {
                "datetime": data[0],
                "AX": data[1],
                "AY": data[2],
                "AZ": data[3],
                "label": label}

            print(data_dic)
            collection.insert_one(data_dic)
        else:
            pass

        row_counter += 1