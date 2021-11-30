import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calcFFT(accel,nrsamples):
    accel_without_mean = accel - np.mean(accel)  # Subtract mean Value to reduce the DC Offset in the FFT
    freq = np.fft.rfft(accel_without_mean, nrsamples, norm='ortho')
    freq = np.abs(freq)
    freq = freq / nrsamples  # Normalize the Amplitude by the known sample number
    return freq

df = pd.read_csv('imu.csv')

StartSample = 0
LengthSample = len(df.index)
EndSample = StartSample+LengthSample

a_x = df.iloc[StartSample:EndSample,0].values
a_y = df.iloc[StartSample:EndSample,1].values
a_z = df.iloc[StartSample:EndSample,2].values

fs = 200.0 # Sample Frequency 200 Hz
SampleNr = LengthSample
Period = 1/fs

x_time=np.linspace(0.0,Period*SampleNr,SampleNr)
x_freq=np.linspace(0.0,fs/2.0,int(SampleNr/2)+1)

ax_freq=calcFFT(a_x,SampleNr)
ay_freq=calcFFT(a_y,SampleNr)
az_freq=calcFFT(a_z,SampleNr)

plt.subplot(311)
plt.plot(x_time,a_x)
plt.plot(x_time,a_y)
plt.plot(x_time,a_z)
plt.subplot(312)
plt.plot(x_freq,ax_freq) # plot FFT for x-accel
plt.plot(x_freq,ay_freq) # plot FFT for y-accel
plt.plot(x_freq,az_freq) # plot FFT for z-accel
plt.subplot(313)
plt.psd(a_x, NFFT=LengthSample, Fs=fs, window=np.blackman(LengthSample)) # plot all axis as PSD
plt.psd(a_y, NFFT=LengthSample, Fs=fs, window=np.blackman(LengthSample)) # plot ay-PSD
plt.psd(a_z, NFFT=LengthSample, Fs=fs, window=np.blackman(LengthSample)) # plot az-PSD
plt.show()