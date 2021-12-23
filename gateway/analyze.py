import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import gateway

database = gateway.Training(database = "monitoring",collection = "ml_training")
df = database.query()
df = df[df.label != "test"]

df["AX"] = df["AX"].astype(float)
df["AY"] = df["AY"].astype(float)
df["AZ"] = df["AZ"].astype(float)

StartSample = 0
LengthSample = len(df.index)

# calculate timeframe
# period in (ms); timeframe (minutes)
# #samples = timeframe * 60 * 1000 / period

Period = 500
timeframe = 5

EndSample = int(timeframe / Period * 60 * 1000) #StartSample+LengthSample
a_x = df.iloc[StartSample:EndSample,2].values
a_y = df.iloc[StartSample:EndSample,3].values
a_z = df.iloc[StartSample:EndSample,4].values

a = np.sqrt(a_x**2 + a_y**2 + a_y**2)

# def y_freq(a_z):
#     n = a_z.size
#     a_z_without_mean = a_z-np.mean(a_z)
#     yfreq = np.fft.rfft(a_z_without_mean,n,norm='ortho')
#     yfreq = np.abs(yfreq)
#     yfreq[0]=0.0
#     #yfreq = yfreq/256
#     return yfreq
#
# # acceleration
# x=np.linspace(0.0,1.0,EndSample)
#
# plt.subplot(311)
# plt.plot(x,a_x)
# #plt.plot(x,a_y)
# #plt.plot(x,a_z)
#
# # Fourier
# plt.subplot(312)
# plt.plot(y_freq(a_x))
# #plt.plot(y_freq(a_y))
# #plt.plot(y_freq(a_z))
# plt.show()

################

from scipy.fftpack import rfft, irfft, fftfreq

time   = np.linspace(0,1.,EndSample)
signal = np.sqrt(a_x**2 + a_y**2 + a_y**2)


W = fftfreq(signal.size, d=time[1]-time[0])
f_signal = rfft(signal)

amplitude = W.max()#signal.sum()
CI = 0.95
threshold = np.percentile(amplitude, CI)

# If our original signal time was in seconds, this is now in Hz
cut_f_signal = f_signal.copy()
cut_f_signal[(W<threshold)] = 0

cut_signal = irfft(cut_f_signal)

import pylab as plt
plt.subplot(221)
plt.plot(time,signal)
plt.subplot(222)
plt.plot(W,f_signal)

plt.xlim(0,EndSample)
plt.subplot(223)
plt.plot(W,cut_f_signal)
plt.xlim(0,EndSample)
plt.subplot(224)
plt.plot(time,cut_signal)
plt.show()