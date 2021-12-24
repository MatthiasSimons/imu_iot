import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import gateway
from sklearn import preprocessing

database = gateway.Training(database="monitoring", collection="ml_training Pflegeleicht 30/1000/3.1")
df = database.query().drop(columns=['_id', 'datetime', 'AX', 'AY', 'AZ', 'timedelta', 'A'])

# changing string labels to categorical labels
le = preprocessing.LabelEncoder()
le.fit(df.label)
df['categorical_label'] = le.transform(df.label)
df = df.drop(columns=['label'])


# split df in chunks
def chunker(seq, size):
    # splitting df in chunk of size
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def label(df):
    # count labels in df and sort; first value in list is the label with most occurences
    labels = df.categorical_label.value_counts(normalize=True, sort=True)
    return list(labels.index)[0]


def fft_peaks(a, peaks=3):
    n = a.size
    a_z_without_mean = a - np.mean(a)
    yfreq = np.fft.rfft(a_z_without_mean, n, norm='ortho')
    yfreq = np.abs(yfreq)
    yfreq[0] = 0.0
    yfreq[yfreq < sorted(yfreq, reverse=True)[:peaks][-1:]] = 0
    return sorted(yfreq, reverse=True)[:peaks]


peaks = 3
columns = ["f_{}".format(i) for i in range(0, peaks)] + ["categorical_label"]

dic = {}
i = 0

for chunk in chunker(df, 10):
    frequencies = fft_peaks(chunk["A-mean"], peaks)
    if len(frequencies) == peaks:
        dic[i] = frequencies + [label(chunk)]
        i += 1

        
fft_df = pd.DataFrame.from_dict(dic, columns = columns,orient='index')
print(fft_df)

###
# Fourier Transformation
# calculate dominating frequency in time interval (t seconds)

####

X = df.drop(columns=['categorical_label'])
y = df['categorical_label']
