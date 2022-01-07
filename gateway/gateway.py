from pymongo import MongoClient
import socket
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
import joblib


class Gateway:
    def __init__(self, client_ip = "localhost:27017", database = "monitoring",collection = "test_collection"):
        self.client = MongoClient(client_ip)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.chunk_size = 10
        self.peaks = 3


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
        return self.prepare(query)

    def prepare(self, query):
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

        # changing string labels to categorical labels
        encoder = LabelEncoder()
        encoder.fit(df.label)
        np.save('classes.npy', encoder.classes_)

        df['categorical_label'] = self.encode_label(df.label)

        return df

    def encode_label(self, labels):
        encoder = LabelEncoder()
        encoder.fit(labels)
        np.save('classes.npy', encoder.classes_)
        return encoder.transform(labels)

    def decode_label(self, label):
        encoder = LabelEncoder()
        encoder.classes_ = np.load('classes.npy', allow_pickle=True)
        return encoder.inverse_transform(label)

    def fft_peaks(a, peaks=None):
        # fast fourier analysis and return n-peak
        n = a.size
        a_z_without_mean = a - np.mean(a)
        yfreq = np.fft.rfft(a_z_without_mean, n, norm='ortho')
        yfreq = np.abs(yfreq)
        yfreq[0] = 0.0
        if peaks == None:
            peaks = len(yfreq)
        yfreq[yfreq < sorted(yfreq, reverse=True)[:peaks][-1:]] = 0
        return yfreq#sorted(yfreq, reverse=True)[:peaks]

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

    def watch(self):
        # watch changes in collection
        pipeline = [{'$match': {'operationType': 'insert'}}]
        with self.collection.watch(pipeline) as stream:
            for insert_change in stream:
                print(insert_change)

    def apply_model(self, sample):
        # return category string from sample
        classifier = joblib.load('model.joblib')
        # predict categorical label by sample
        categorical_label = classifier.predict(sample)
        # inverse transform categorical labels (LabelEncoder.inverse_transform)
        return self.decode_label(categorical_label)

    def label(self):
        # query last n elements (=self.chunk_size)
        # calc fft with n-peaks (self.peaks)
        # implement ml model -> input data; output label
        return



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

    def fft_processing(self):
        df = self.query()

        ###############
        # data preperation
        # split df in chunks
        def chunker(seq, size):
            # splitting df in chunk of size
            return (seq[pos:pos + size] for pos in range(0, len(seq), size))

        def label(df):
            # count labels in df and sort; first value in list is the label with most occurences
            labels = df.categorical_label.value_counts(normalize=True, sort=True)
            return list(labels.index)[0]

        columns = ["f_{}".format(i) for i in range(0, self.peaks)] + ["categorical_label"]
        dic = {}
        i = 0

        for chunk in chunker(df, self.chunk_size):
            frequencies = Gateway.fft_peaks(chunk["A-mean"], self.peaks)
            if len(frequencies) == self.peaks:
                dic[i] = frequencies + [label(chunk)]
                i += 1

        return pd.DataFrame.from_dict(dic, columns = columns,orient='index')

    def train_model(self):
        fft_df = self.fft_processing()

        classifier = SGDClassifier(loss="hinge", penalty="l2", max_iter=5)

        X = fft_df.drop(columns=['categorical_label'])
        y = fft_df['categorical_label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
        classifier.fit(X_train, y_train)

        joblib.dump(classifier, 'model.joblib')

        score = classifier.score(X_test, y_test)
        print("accuracy: {} %".format(round(score*100, 2)))


if __name__ == "__main__":
    program, f, w = "test", 1000, 3.1
    training = Training(database = "monitoring",collection = "ml_training {}/{}/{}".format(program, f, w))

    # labels: leerlauf, pumpen, waschen, schleudern
    label = str(input("label: "))
    training.fill_db(label=label)
    #training.train_model()

