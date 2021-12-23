import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import gateway
from sklearn import preprocessing

database = gateway.Training(database = "monitoring",collection = "ml_training Pflegeleicht 30/1000/3.1")
df = database.query().drop(columns = ['_id', 'datetime', 'AX', 'AY', 'AZ', 'timedelta', 'A', 'A-mean'])

# changing string labels to categorical labels
le = preprocessing.LabelEncoder()
le.fit(df.label)
df['categorical_label'] = le.transform(df.label)
df = df.drop(columns = ['label'])

###
# Fourier Transformation
# calculate dominating frequency in time interval (t seconds)
# divide df in chunks of time interval
####

X = df.drop(columns = ['categorical_label'])
y = df['categorical_label']


print(df)