import pandas as pd
import numpy as np
#import sklearn as sk
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import os
import joblib
#from server import server
#from server import server
from src.gateway import Training


class ClassifierModel:
    def __init__(self, chunk_length=64, model_name="default", label_column=None):
        self.chunk_length = chunk_length
        self.model_file_name = "model_{}.joblib".format(model_name)
        self.scaler_file_name = "scaler_{}.joblib".format(model_name)
        self.score = 0.
        self.label_column = label_column

        if not os.path.isfile(self.model_file_name) or not os.path.isfile(self.scaler_file_name):
            self.train()

        self.scaler = joblib.load(self.scaler_file_name)
        self.classifier = joblib.load(self.model_file_name)


    def train(self):
        database = Training(database="monitoring", collection="ml_training")
        df = database.query()
        transformed_dataset = self.transform(df)

        X = transformed_dataset.drop(columns=[0]).values
        y = transformed_dataset[0].values

        split_factor = 0.25
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split_factor, random_state=1, stratify=y)

        scaler = StandardScaler()
        scaler.fit(X_train)
        joblib.dump(scaler, self.scaler_file_name)

        X_train_std = scaler.transform(X_train)
        X_test_std = scaler.transform(X_test)

        classifier = MLPClassifier(alpha=0.03, max_iter=5000, early_stopping=False)
        classifier.fit(X_train_std, y_train)
        joblib.dump(classifier, self.model_file_name)
        self.score = classifier.score(X_test_std, y_test)

    def transform(self, df):
        fft_data = []
        for chunk in self.chunker(df, self.chunk_length):
            if self.label_column in chunk.columns.values:
                labels = chunk[self.label_column].value_counts()
                if len(labels) > 0:
                    label = chunk[self.label_column].value_counts().index[0]

                    fft_data.append(self.fft_peaks(chunk["A"]) + label)
            else:
                fft_data.append(self.fft_peaks(chunk["A"]))
        return pd.DataFrame.from_dict(fft_data).dropna()

    def predict(self, df, counter):
        #database = Training(database="monitoring", collection="ml_training")
        #df = database.query(last=counter+self.chunk_length).iloc[counter:]

        X = self.transform(df).drop(columns = [0])
        X_std = self.scaler.transform(X)

        prediction = self.classifier.predict(X_std)
        probabilities = self.classifier.predict_proba(X_std)
        return probabilities

    def fft_df(self, dataset, size):
        fft_data = []
        for chunk in self.chunker(dataset, size):
            fft_data.append(self.fft_peaks(chunk["A"]))
        return pd.DataFrame.from_dict(fft_data).dropna()

    def chunker(self, seq, size=64):
        # splitting df in chunk of size
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def fft_peaks(self, a, peaks=None):
        # fast fourier analysis and return n-peak
        n = a.size
        a_z_without_mean = a - np.mean(a)
        yfreq = np.fft.rfft(a_z_without_mean, n, norm='ortho')
        yfreq = np.abs(yfreq)
        yfreq[0] = 0.0
        if peaks == None:
            peaks = len(yfreq)
        yfreq[yfreq < sorted(yfreq, reverse=True)[:peaks][-1:]] = 0
        return yfreq

if __name__ == "__main__":
    classifier = ClassifierModel("trommel", label_column="trommel")
    classifier.predict()
    print(classifier.score)
