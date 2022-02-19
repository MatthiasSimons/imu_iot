import os
import time
import joblib
import numpy as np
import pandas as pd
from src.gateway import BNK
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import random

class ClassifierModel:
    def __init__(self, model_name):
        self.model_file_name = "model_{}.joblib".format(model_name)
        self.scaler_file_name = "scaler_{}.joblib".format(model_name)
        self.score = 0.
        self.label_column = model_name

        # if not os.path.isfile(self.model_file_name) or not os.path.isfile(self.scaler_file_name):
        #     self.train()
        #
        # self.scaler = joblib.load(self.scaler_file_name)
        # self.classifier = joblib.load(self.model_file_name)

    def train(self, trainings_fft):

        X = trainings_fft.drop(columns=[0]).values
        y = trainings_fft[0].values

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

    def predict(self, fft):
        return random.random(), [random.random(),random.random(),random.random(),random.random(),]

source = BNK(collection ="process_data")
target = BNK(collection ="backend")
target.clear()

df = pd.DataFrame(data=None, columns=["AX", "AY", "AZ", "A"])

# ggf länge von nur  n werten -> plot übersichtlicher
timestamp_history = []
prediction_history_trommel = []
prediction_history_pumpe = []
prediction_history_betriebszustand = []

classifier_trommel = ClassifierModel("Trommel")
classifier_pumpe = ClassifierModel("Pumpe")
classifier_betriebszustand = ClassifierModel("Betriebszustand")


def fft(df):
    """function for fast fourier analysis"""
    n = df.size
    a_z_without_mean = df - np.mean(df)
    yfreq = np.fft.rfft(a_z_without_mean, n, norm='ortho')
    yfreq = np.abs(yfreq)
    yfreq[0] = 0.0
    return yfreq.tolist()

def processing():
    """
    1. query acceleration acceleration
    2. append acceleration acceleration to df & calculate trainings_fft
    3. predict labels from trainings_fft
    4. (plot acceleration and trainings_fft)
    5. return df, acceleration_fft and label probabilities
        """
    history_length = 10
    query = source.query(last=1)
    acceleration = source.prepare(query)
    timestamp = acceleration.index.max()

    acceleration_A = acceleration["A"]
    acceleration_A.index = acceleration_A.index.strftime('%Y/%m/%d %H:%M:%S:%f')

    try:
        acceleration_fft = fft(acceleration_A)
    except:
        acceleration_fft = []

    #------------------------------------------------------
    # ml-model
    # model.predict(acceleration_fft)
    prediction_trommel, probabilities_trommel = classifier_trommel.predict(acceleration_fft)
    prediction_pumpe, probabilities_pumpe = classifier_pumpe.predict(acceleration_fft)
    prediction_betriebszustand, probabilities_betriebszustand = classifier_betriebszustand.predict(acceleration_fft)

    timestamp_history.append(timestamp)
    prediction_history_trommel.append(prediction_trommel)
    prediction_history_pumpe.append(prediction_pumpe)
    prediction_history_betriebszustand.append(prediction_betriebszustand)


    if len(timestamp_history) >= history_length:
        timestamp_history.pop(0)
    if len(prediction_history_trommel) >= history_length:
        prediction_history_trommel.pop(0)
    if len(prediction_history_pumpe) >= history_length:
        prediction_history_pumpe.pop(0)
    if len(prediction_history_betriebszustand) >= history_length:
        prediction_history_betriebszustand.pop(0)

    processed_dataset = {
            "timestamp": timestamp,
            "timestamp_history": timestamp_history,
            "acceleration": acceleration_A.to_dict(),
            "acceleration_fft": acceleration_fft,
            "probabilities_trommel": probabilities_trommel,
            "probabilities_pumpe": probabilities_pumpe,
            "probabilities_betriebszustand": probabilities_betriebszustand,
            "prediction_history_trommel": prediction_history_trommel,
            "prediction_history_pumpe": prediction_history_pumpe,
            "prediction_history_betriebszustand": prediction_history_betriebszustand
        }
    target.insert(processed_dataset)
    print(processed_dataset)

if __name__ == "__main__":
    while 1:
        processing()
        time.sleep(1)
