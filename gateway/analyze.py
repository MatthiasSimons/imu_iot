import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import signal
import gateway
import seaborn as sns

database = gateway.Training(database = "monitoring",collection = "ml_training Pflegeleicht 30/1000/3.1")
df = database.query()
labels = df.label.unique()

def y_freq(a, peaks=3):
    n = a.size
    a_z_without_mean = a - np.mean(a)
    yfreq = np.fft.rfft(a_z_without_mean,n,norm='ortho')
    yfreq = np.abs(yfreq)
    yfreq[0]=0.0
    yfreq[yfreq < sorted(yfreq, reverse=True)[:peaks][-1:]] = 0
    print(sorted(yfreq, reverse=True)[:peaks])
    return yfreq


for label in labels:
    df_ = df.query("label == '{}'".format(label))
    plt.title(label)
    print(label)

    ax1 = plt.subplot(311)
    ax1.set_title("signal (acceleration)")
    ax1.set_ylabel("acceleration in (g)")
    ax1.set_xlabel("time in (s)")
    g = sns.lineplot(x = df_["timedelta"], y = df_["A-mean"], label = label)

    ax2 = plt.subplot(312)
    ax2.set_title("fourier-transformed signal")
    ax2.set_ylabel("FFT(acceleration)")
    ax2.set_xlabel("frequenzy in (HZ)")
    yfreq = y_freq(df_["A-mean"])
    plt.plot(yfreq)

    # ax3 = plt.subplot(313, projection='3d')#.gca(projection='3d')
    # ax3 = Axes3D(ax3)
    # x,y = np.meshgrid(df_["A-mean"].size, yfreq)
    # ax3.plot_trisurf(x, y, yfreq)
#
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# #x,y = np.meshgrid(df_["A-mean"].size, yfreq.size)
# ax.plot_trisurf(df_["A-mean"].size, yfreq.size, yfreq)

sns.move_legend(g, "upper center", title=None, ncol=4)
plt.tight_layout()
plt.show()
