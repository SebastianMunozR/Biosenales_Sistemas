# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un    organizador de widget en la ventana, este en particular los apila en vertcal
#soporta la carga de multiples tipos de archivos
#si se desea cargar archivos de texto se podria usar numpy.loadtxt
import scipy.io as sio;
# libreria para hacer graficos tipos matlab (pyplot)
import matplotlib.pyplot as plt;
#libreria de manejo de arreglos de grandes dimensiones (a diferencia de las listas basicas de python)
import numpy as np;
#libreria con rutinas de PDS
import scipy.signal as signal;

#PRIMERA PARTE CARGA Y MANIPULACION BASICA

#loading data
#mat_contents = sio.loadmat('D:\Bioseñales 2018-2\Lab2\signals.mat');
mat_contents = sio.loadmat(r'C001R_EP_REPOSO');

#los datos se cargan como un diccionario, se puede evaluar los campos que contiene
print("Los campos cargados son: " + str(mat_contents.keys()));
#la senal esta en el campo data
data1 = mat_contents['data'];
data2 = np.squeeze(mat_contents['data']);
print("Variable python: " + str(type(data2)));
print("Tipo de variable cargada: " + str(data2.dtype));
print("Dimensiones de los datos cargados: " + str(data2.shape));
print("Numero de dimensiones: " + str(data2.ndim));
print("Tamanio: " + str(data2.size));
print("Tamanio en memoria (bytes): " + str(data2.nbytes));

mat_contents2 = sio.loadmat(r'dataset_senales');

#los datos se cargan como un diccionario, se puede evaluar los campos que contiene
print("Los campos cargados son: " + str(mat_contents.keys()));
#la senal esta en el campo data
data3 = mat_contents2['anestesia'];
data4 = np.squeeze(mat_contents2['anestesia']);
print("Variable python: " + str(type(data4)));
print("Tipo de variable cargada: " + str(data4.dtype));
print("Dimensiones de los datos cargados: " + str(data4.shape));
print("Numero de dimensiones: " + str(data4.ndim));
print("Tamanio: " + str(data4.size));
print("Tamanio en memoria (bytes): " + str(data4.nbytes));