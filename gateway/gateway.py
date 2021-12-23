import pymongo
from pymongo import MongoClient
import socket
import pandas as pd
import numpy as np

class Gateway:
    def __init__(self, client_ip = "localhost:27017", database = "monitoring",collection = "test_collection"):
        self.client = MongoClient(client_ip)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def listen(self, tcp_ip ='192.168.0.129', tcp_port = 8000):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((tcp_ip, tcp_port))

        print("Waiting for Connection...")
        s.listen(1)
        conn, addr = s.accept()

        print('Connection address:', addr)
        return conn

    def query(self, condition = {}, first = None, last = None):
        query = list(self.collection.find(condition))
        if query is None:
            query = []
        if first != None:
            query = query[:first]
        if last != None:
            query = query[-last:]
        return self.process(query)

    def process(self, query):
        df = pd.DataFrame(query)
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y/%m/%d %H:%M:%S:%f')
        df["timedelta"] = (df['datetime'] - df['datetime'].values[0]).dt.total_seconds()

        df["AX"] = df["AX"].astype(float)
        df["AY"] = df["AY"].astype(float)
        df["AZ"] = df["AZ"].astype(float)

        df["A"] = np.sqrt(df["AX"] ** 2 + df["AY"] ** 2 + df["AZ"] ** 2)
        df["AX-mean"] = df["AX"] - df["AX"].mean()
        df["AY-mean"] = df["AY"] - df["AY"].mean()
        df["AZ-mean"] = df["AZ"] - df["AZ"].mean()
        df["A-mean"] = df["A"] - df["A"].mean()
        return df



class Process(Gateway):
    def fill_db(self, buffer_size = 20480):
        conn = super().listen()
        while 1:
            data = conn.recv(buffer_size)
            if not data:
                break

            datasets = data.decode().split("?")[:-1]

            for dataset in datasets:
                data_string = dataset.split(",")
                data_dic = {
                    "datetime": data_string[0],
                    "AX": data_string[1],
                    "AY": data_string[2],
                    "AZ": data_string[3],
                    }
                self.collection.insert_one(data_dic)
        conn.close()

    def label(self):
        # implement ml model -> input data; output label
        return None



class Training(Gateway):
    def fill_db(self, label = 0,buffer_size = 20480):
        conn = super().listen()
        #for i in range(0, 200):
        i = 0
        while 1:
            data = conn.recv(buffer_size)
            if not data:
                break

            datasets = data.decode().split("?")[:-1]

            for dataset in datasets:
                print(i, dataset)
                data_string = dataset.split(",")
                data_dic = {
                    "datetime": data_string[0],
                    "AX": data_string[1],
                    "AY": data_string[2],
                    "AZ": data_string[3],
                    "label": label,
                    }
                self.collection.insert_one(data_dic)
                i += 1
        conn.close()

if __name__ == "__main__":
    program, f, w = "Pflegeleicht 30", 1000, 3.1
    # labels: leerlauf, pumpen, waschen, schleudern

    #label = str(input("label: "))
    training = Training(database = "monitoring",collection = "ml_training {}/{}/{}".format(program, f, w))
    #training.fill_db(label=label)

