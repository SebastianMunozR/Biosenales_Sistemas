#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 16:57:18 2020

@author: jfochoa
"""

#PRIMERA PARTE CARGA Y MANIPULACION BASICA

#library to load mat files
import scipy.io as sio;
import matplotlib.pyplot as plt;
import numpy as np;

from IPython import get_ipython

get_ipython().run_line_magic(r'matplotlib', 'qt')

#loading data
mat_contents = sio.loadmat(r'dataset_senales.mat')
#the data is loaded as a Python dictionary
print("the loaded keys are: " + str(mat_contents.keys()));
#in the current case the signal is stored in the data field
ojos_cerrados = np.squeeze(mat_contents['ojos_cerrados']); #to explain
ojos_abiertos = np.squeeze(mat_contents['ojos_abiertos']);
anestesia = np.squeeze(mat_contents['anestesia']);

plt.plot(ojos_cerrados)
plt.show()

#%%Transformada de Fourier
from scipy.fftpack import fft;

fs = 250
N = ojos_cerrados.shape[0];
#FREQUENCY RESOLUTION AND SAMPLING EFFECT OVER THE SPECTRA(to explain)
fs_res = fs/N

#frequency resolution fs/N
X = fft(ojos_cerrados);
freqs = np.arange(0.0, fs, fs_res);

get_ipython().run_line_magic('matplotlib', 'qt')

plt.plot(freqs, np.abs(X));
plt.show();

#FREQUENCY RESOLUTION AND SAMPLING EFFECT OVER THE SPECTRA(to explain)
#DC LEVELS
#%%se elimina el efecto del la baja frecuencia
ojos_cerrados = ojos_cerrados - np.mean(ojos_cerrados)
ojos_abiertos = ojos_abiertos - np.mean(ojos_abiertos)

#frequency resolution fs/N
X = fft(ojos_cerrados);
freqs = np.arange(0.0, fs, fs_res);

get_ipython().run_line_magic('matplotlib', 'qt')
plt.plot(freqs, np.abs(X));
plt.show();

#DC LEVELS
#%% graficacion espectro 'real'

get_ipython().run_line_magic('matplotlib', 'qt')
plt.plot(freqs[freqs <= fs/2], np.abs(X[freqs <= fs/2]));
plt.show();

#QUE ES EL ESPECTRO REAL? RECORDAR EN MUESTREO LA PERIODICIDAD
#%%analisis espectral directo

get_ipython().run_line_magic('matplotlib', 'qt')
X_power = np.power(np.abs(X),2)/N
plt.plot(freqs[freqs <= fs/2], X_power[freqs <= fs/2]);
plt.show();

#RECORDAR EL TEOREMA DE WIENNER-
#%%analisis en la frecuencia de interes
get_ipython().run_line_magic('matplotlib', 'qt')
X_power = np.power(np.abs(X),2)/N
plt.plot(freqs[(freqs >= 2) & (freqs <= 40)], X_power[(freqs >= 2) & (freqs <= 40)]);
plt.show();

#%%analisis usando welch
import scipy.signal as signal;
#signal.welch(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, 
#detrend='constant', return_onesided=True, scaling='density', axis=-1)
get_ipython().run_line_magic('matplotlib', 'qt')
f, Pxx = signal.welch(ojos_cerrados,fs,'hamming', 512, 256, 512, scaling='density');
print(f.shape)
plt.plot(f,Pxx)
plt.show()

#%%analisis usando welch
import scipy.signal as signal;
#signal.welch(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, 
#detrend='constant', return_onesided=True, scaling='density', axis=-1)
f, Pxx = signal.welch(ojos_cerrados,fs,'hamming', 512*0.5, 256*0.5, 512*0.5, scaling='density');
print(f.shape)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#%%analisis usando welch
import scipy.signal as signal;
#signal.welch(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, 
#detrend='constant', return_onesided=True, scaling='density', axis=-1)
f, Pxx = signal.welch(ojos_cerrados,fs,'hamming', 1024, 512, 1024, scaling='density');
print(f.shape)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#QUE HACEMOS CUANDO AUMENTAMOS EL NUMERO DE VENTANAS?

#%%analisis usando welch
import scipy.signal as signal;
#signal.welch(x, fs=1.0, window='hann', nperseg=None, noverlap=None, nfft=None, 
#detrend='constant', return_onesided=True, scaling='density', axis=-1)
f, Pxx = signal.welch(ojos_cerrados,fs,'hamming', fs*5, fs*2.5, scaling='density');
print(f.shape)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#QUE HACEMOS CUANDO AUMENTAMOS EL NUMERO DE VENTANAS?

#%% anestesia
anestesia = anestesia - np.mean(anestesia)
f, Pxx = signal.welch(anestesia,fs,'hamming', fs*5, fs*2.5, scaling='density');
print(f.shape)

plt.subplot(2,1,1)
plt.plot(anestesia)
plt.subplot(2,1,2)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#%%analisis usando multitaper
from chronux.mtspectrumc import mtspectrumc

#A numeric vector [W T p] where W is the
#bandwidth, T is the duration of the data and p 
#is an integer such that 2TW-p tapers are used.
params = dict(fs = fs, fpass = [0, 50], tapers = [4, 2, 1], trialave = 1)

data = np.reshape(anestesia,(fs*5,10),order='F')

#Calculate the spectral power of the data
Pxx, f = mtspectrumc(data, params)

plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#%%analisis usando multitaper
from chronux.mtspectrumc import mtspectrumc

#A numeric vector [W T p] where W is the
#bandwidth, T is the duration of the data and p 
#is an integer such that 2TW-p tapers are used.
params = dict(fs = fs, fpass = [0, 50], tapers = [4, 2, 1], trialave = 1)

data = np.reshape(anestesia,(fs*5,10),order='F')

#Calculate the spectral power of the data
Pxx, f = mtspectrumc(data, params)

plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#SUAVIZADO EN FRECUENCIAS CERCANAS
#%%analisis usando multitaper scipy 1.1.0
from chronux.mtspectrumc import mtspectrumc

params = dict(fs = fs, fpass = [0, 50], tapers = [2, 2, 1], trialave = 1)

data = np.reshape(anestesia,(fs,10*5),order='F')

#Calculate the spectral power of the data
Pxx, f = mtspectrumc(data, params)

plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show

#SUAVIZADO POR PROMEDIOS
#EFECTO DE W, T, y trialaverage
#%% anestesia
anestesia = anestesia - np.mean(anestesia)
f, Pxx = signal.welch(anestesia,fs,'hamming', fs*5, 0, fs*5, scaling='density');
print(f.shape)

plt.subplot(2,1,1)
plt.plot(anestesia)
plt.subplot(2,1,2)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#%% anestesia
anestesia = anestesia - np.mean(anestesia)
f, Pxx = signal.welch(anestesia,fs,'hamming', fs*5, 0, fs*5, scaling='spectrum');
print(f.shape)

plt.subplot(2,1,1)
plt.plot(anestesia)
plt.subplot(2,1,2)
plt.plot(f[(f >= 4) & (f <= 40)],Pxx[(f >= 4) & (f <= 40)])
plt.show()

#%%analisis usando wavelet continuo
import pywt #1.1.1

#%%
sampling_period =  1/fs
Frequency_Band = [4, 30] # Banda de frecuencia a analizar

# Métodos de obtener las escalas para el Complex Morlet Wavelet  
# Método 1:
# Determinar las frecuencias respectivas para una escalas definidas
scales = np.arange(1, 250)
frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
# Extraer las escalas correspondientes a la banda de frecuencia a analizar
scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 
#%%
# Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
time_epoch = sampling_period*N

# Analizar una epoca de un montaje (con las escalas del método 1)
# Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
time = np.arange(0, time_epoch, sampling_period)
# Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet

[coef, freqs] = pywt.cwt(anestesia, scales, 'cmor', sampling_period)
# Calcular la potencia 
power = (np.abs(coef)) ** 2

# Graficar el escalograma obtenido del análisis tiempo frecuencia
f, ax = plt.subplots(figsize=(15, 10))
scalogram = ax.contourf(time,
                 freqs[(freqs >= 4) & (freqs <= 40)],
                 power[(freqs >= 4) & (freqs <= 40),:],
                 100, # Especificar 20 divisiones en las escalas de color 
                 extend='both')
ax.set_ylim(4, 40)
ax.set_ylabel('frequency [Hz]')
ax.set_xlabel('Time [s]')
cbar = plt.colorbar(scalogram)

#%% Graficar el escalograma obtenido del análisis tiempo frecuencia
f, ax = plt.subplots(figsize=(15, 10))
scalogram = ax.contourf(time[0:fs*5],
                 freqs[(freqs >= 4) & (freqs <= 40)],
                 power[(freqs >= 4) & (freqs <= 40),0:fs*5],
                 100, # Especificar 20 divisiones en las escalas de color 
                 extend='both')
ax.set_ylim(4, 40)
ax.set_ylabel('frequency [Hz]')
ax.set_xlabel('Time [s]')
cbar = plt.colorbar(scalogram)
