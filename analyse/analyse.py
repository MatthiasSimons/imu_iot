import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

df = pd.read_csv('../src/process-related/client/imu.csv', usecols = ["datetime", "A_X", "A_Y", "A_Z"])
print(df)
StartSample = 0
LengthSample = len(df.index)

EndSample = StartSample+LengthSample
a_x = df.iloc[StartSample:EndSample,0].values
a_y = df.iloc[StartSample:EndSample,1].values
a_z = df.iloc[StartSample:EndSample,2].values

#bands = (0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5)
fs = 100 # Hz
#desired = (0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0)
#fir_firwin2 = signal.firwin2(51, bands, desired, fs=fs)
#y_filtered = signal.lfilter(fir_firwin2, [1.0], y)

#Period = 60.0*60.0*24.0
Period = 0.01
sample_rate = 1.0/Period
n = a_z.size
a_z_without_mean = a_z-np.mean(a_z)
yfreq = np.fft.rfft(a_z_without_mean,n,norm='ortho')
yfreq = np.abs(yfreq)
yfreq[0]=0.0
yfreq = yfreq/256
x=np.linspace(0.0,1.0,100)
plt.subplot(311)
plt.plot(x,a_x)
plt.plot(x,a_y)
plt.plot(x,a_z)
plt.subplot(312)
plt.psd(a_z, NFFT=LengthSample, Fs=1.0/Period, window=np.blackman(LengthSample),pad_to=256)
plt.subplot(313)
plt.plot(yfreq)
plt.show()
