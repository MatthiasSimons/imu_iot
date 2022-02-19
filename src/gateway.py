from pymongo import MongoClient
import socket
import pandas as pd
import numpy as np

class Gateway:
    def __init__(self, collection):
        self.client_ip = "localhost:27017"
        self.tcp_ip = '192.168.101.129'
        self.tcp_port = 8000
        self.batch_size = 64
        self.database_name = "DLSP-Project"

        self.client = MongoClient(self.client_ip)
        self.db = self.client[self.database_name]
        self.collection = self.db[collection]

class BNK(Gateway):
    def query(self, condition = {}, first = None, last = None):
        """function for acceleration query from database; returns a pandas DataFrame"""
        query = list(self.collection.find(condition))
        if query is None:
            query = []
        if first != None:
            query = query[:first]
        if last != None:
            query = query[-last:]
        return query#self.prepare(query)

    def prepare(self, query):
        """function for acceleration cleaning; returns a pandas DataFrame"""

        query[0].pop("_id")

        df = pd.DataFrame.from_dict(query[0], orient="index")
        df.index = pd.to_datetime(df.index, format='%Y/%m/%d %H:%M:%S:%f', errors="ignore")

        df = df[0].str.split(",", expand=True)
        df.columns = ["AX", "AY", "AZ"]

        df["AX"] = df["AX"].astype(float, errors="ignore")
        df["AY"] = df["AY"].astype(float, errors="ignore")
        df["AZ"] = df["AZ"].astype(float, errors="ignore")

        df["A"] = np.sqrt(df["AX"] ** 2 + df["AY"] ** 2 + df["AZ"] ** 2)

        return df

    def clear(self):
        self.collection.delete_many({})

    def insert(self, dataset):
        """function for inserting labels into database {"timestamp": [{label_1: Bool}, {label_2: Bool}]}"""
        self.collection.insert_one(dataset)
        return

class PNK(Gateway):
    def insert(self, training=False, buffer_size = 20480):
        """function for inserting imu acceleration to database {timestamp: acceleration}

        Due to the high sampling rate, arrays may get messed up.
        Because of this, only complete arrays are written to the database.
        In this case, complete means that n (=batch size)
        acceleration records are recorded one after the other without being mixed up."""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.tcp_ip, self.tcp_port))
        print("Waiting for Connection...")
        s.listen(1)
        conn, addr = s.accept()
        print('Connection address:', addr)
        print("succesfully connected to device")

        i = 0
        missed = 0
        batches = 0
        batch = {}

        if not training:
            self.collection.delete_many( { } )

        while 1:
            data = conn.recv(buffer_size)
            if not data:
                break

            datasets = data.decode().split("?")[:-1]
            for dataset in datasets:
                data_string = dataset.split(";")
                try:
                    dt, accel_xyz = data_string[0].replace("(", "").replace(")", ""), data_string[1].replace("(", "").replace(")", "")
                    batch[dt] = accel_xyz

                    if len(batch) >= self.batch_size:
                        self.collection.insert_one(batch)
                        batches += 1
                        print("------------------------------------------------------------------------")
                        print(batches, "full batches")
                        print("missed {} datasets from a total of {} datasets.".format(missed, i))
                        print("Thats equal to a loss of {} %".format(round(float(missed / i * 100)), 5))
                except:
                    batch = {}
                    missed += 1
                i += 1
        conn.close()

if __name__ == "__main__":
    gw = PNK(collection = "process")
    gw.insert(training=False)