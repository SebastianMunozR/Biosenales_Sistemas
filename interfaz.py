"""
David Alejandro Ijaji Guerrero       C.C.1017250858
Edison Sebastian Munoz Rodriguez     C.C 1214745427
"""
#%%Librerias
import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un    organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator
import matplotlib.pyplot as plt;
import scipy.signal as signal;
from chronux.mtspectrumc import mtspectrumc
from matplotlib.figure import Figure
from PyQt5.uic import loadUi
from numpy import arange, sin, pi
import math
from IPython import get_ipython
import pywt

#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import scipy.io as sio
import numpy as np
from Modelo import Biosenal
# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)

        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        self.barraexist=False#para saber si la barra de colores del wavelet existe
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)
        

        
    #este metodo me grafica al senal senoidal que yo veo al principio, mas no senales
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s)
    #hay que crear un metodo para graficar lo que quiera
    def graficar_datos(self,datos):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        self.axes.plot(datos)
        #y lo graficamos
        print("datos")
        print(datos)
        #voy a graficar en un mismo plano varias senales que no quecden superpuestas cuando uso plot me pone las graficas en un mismo grafico
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c,:]+c*10)
        self.axes.set_xlabel("muestras")
        self.axes.set_ylabel("voltaje (uV)")
        #self.axes.set
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()
        
    def graficar_senal(self,senal):
        self.axes.clear()
        if senal.ndim == 1:
            self.axes.plot(senal)
        else:
            DC = 10 
            for canal in range(senal.shape[0]):
                self.axes.plot(senal[canal,:]+DC*canal)
        self.axes.figure.canvas.draw()
        
    def graficar_metodos(self,Pxx,f,metodo):
        if self.barraexist == True:#si la barra existe hay que eliminarla
            self.barra.remove()#la borro
            self.barraexist = False#si la borro deja de exixtir 
        self.axes.clear()# se limpia la ventana
        self.axes.plot(Pxx,f)
        #y lo graficamos
        if metodo == "welch":
            ejex="Frequency[Hz]"
            ejey="PSD [V**2/Hz]"
        if metodo == "multitaper":
            ejex="Frequency[Hz]"
            ejey="PSD"
        self.axes.set_xlabel(ejex)
        self.axes.set_ylabel(ejey)
        self.axes.figure.canvas.draw()
        
    def graficar_senal3D(self,time,freqs,power,fl,fh,ti,tf,fs):
        self.barraexist=True
        self.axes.clear()
        self.axes.set_ylabel("Frecuencia [Hz]")
        self.axes.set_xlabel("Tiempo [s]")
        scalogram=self.axes.contourf(time[fs*ti:fs*tf],
                        freqs[(freqs >= fl) & (freqs <= fh)],
                        power[(freqs >= fl) & (freqs <= fh),fs*ti:fs*tf],
                         20, # Especificar 20 divisiones en las escalas de color 
                         extend='both')
        self.barra=self.fig.colorbar(scalogram)
        self.axes.figure.canvas.draw()
        
    def graficar_2senal(self,sena,senb):
        self.axes.clear()
        self.axes.plot(sena)
        self.axes.plot(senb-20)
        self.axes.set_xlabel("muestras")
        self.axes.set_title("Senal Canal - Senal Filtrada ")
        self.axes.figure.canvas.draw()
        

#%%
        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    #condtructor
    def __init__(self):
        #siempre va
        super(InterfazGrafico,self).__init__()
        #se carga el diseno
        loadUi ('anadir_grafico2.ui',self)
        #se llama la rutina donde configuramos la interfaz
        self.setup()
    
        #se muestra la interfaz
        self.show()
        
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite aÃ±adir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        #se anade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        #se aÃ±ade el campo de graficos
        layout.addWidget(self.__sc)
        
        #se organizan las señales 
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_adelante.clicked.connect(self.adelante_senal)
        self.boton_atras.clicked.connect(self.atrasar_senal)
        self.boton_aumentar.clicked.connect(self.aumentar_senal)
        self.boton_disminuir.clicked.connect(self.disminuir_senal) 
        self.boton_canal.clicked.connect(self.selec_canal)
        self.campo_canal.setValidator(QIntValidator(0,7))
        self.boton_filtro.clicked.connect(self.fil_signal)
        self.boton_univ.toggled.connect(self.univ)
        self.boton_minimax.toggled.connect(self.minimax)
        self.boton_sure.toggled.connect(self.sure)
        self.boton_duro.toggled.connect(self.duro)
        self.boton_suave.toggled.connect(self.suave)
        self.boton_one.toggled.connect(self.one)
        self.boton_single.toggled.connect(self.sln)
        self.boton_mult.toggled.connect(self.mln)
        self.graficarw.clicked.connect(self.Me_Welch)
        self.graficarm.clicked.connect(self.Me_Multi)
        self.graficarescalog.clicked.connect(self.Me_Wavelet)
        
#        Botones para el segundo trabajo
#        welch
        self.welch_tamano.setValidator(QIntValidator())
        self.welch_solapa.setValidator(QIntValidator())
        self.fsw.setValidator(QIntValidator())
        self.tipoDeVentanaComboBox1.setEnabled(False)
        self.graficarw.setEnabled(False)
        
#       multitaper
        self.multiw.setValidator(QIntValidator())
        self.multit.setValidator(QIntValidator())
        self.multip.setValidator(QIntValidator())
        self.fsm.setValidator(QIntValidator())
        self.flow.setValidator(QIntValidator())
        self.fhigh.setValidator(QIntValidator())
        self.tiempom.setValidator(QIntValidator())
        self.graficarm.setEnabled(False)
#       frecuencia vs tiempo
        self.ft_fs.setValidator(QIntValidator())
        self.ft_fl.setValidator(QIntValidator())
        self.ft_fh.setValidator(QIntValidator())
        self.ft_ti.setValidator(QIntValidator())
        self.ft_tf.setValidator(QIntValidator())
        self.graficarescalog.setEnabled(False)    


        
        #hay botones que no deberian estar habilitados si no he cargado la senal
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_aumentar.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.boton_canal.setEnabled(False)
        self.boton_univ.setEnabled(False)
        self.boton_minimax.setEnabled(False)
        self.boton_sure.setEnabled(False)
        self.boton_duro.setEnabled(False)
        self.boton_suave.setEnabled(False)
        self.boton_one.setEnabled(False)
        self.boton_single.setEnabled(False)
        self.boton_mult.setEnabled(False)
        self.boton_filtro.setEnabled(False)
        self.boton_ok.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.show()
        #cuando cargue la senal debo volver a habilitarlos
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador
    def adelante_senal(self):
        self.__x_min=self.__x_min+2000
        self.__x_max=self.__x_max+2000
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def atrasar_senal(self):
        #que se salga de la rutina si no puede atrazar
        if self.__x_min<2000:
            return
        self.__x_min=self.__x_min-2000
        self.__x_max=self.__x_max-2000
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def aumentar_senal(self):
        #en realidad solo necesito limites cuando tengo que extraerlos, pero si los 
        #extraigo por fuera mi funcion de grafico puede leer los valores
        self.__sc.graficar_datos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,2))
    def disminuir_senal(self):
        self.__sc.graficar_datos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,0.5))
    def selec_canal(self): 
        # Selecciona y grafica un canal específico
        canal = int(self.campo_canal.text())
        self.senal=np.squeeze(self.data[canal,0::])
        #defino esto por que con esta senal trabajan los nuevos metodos para que tomen toda la senal y no solo 2000 puntos
        self.senal=self.senal.reshape(1,self.senal.shape[0]*self.senal.shape[1])
        print("LA SENAL DAAAA")
        print(self.senal.shape)
        print(self.senal.ndim)
        self.datos=self.__coordinador.devolver_canal(canal, self.__x_min, self.__x_max)
        self.__sc.graficar_senal(self.datos)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        print(self.datos)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_aumentar.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.boton_univ.setEnabled(True)
        self.boton_minimax.setEnabled(True)
        self.boton_sure.setEnabled(True)            
        self.boton_duro.setEnabled(True)
        self.boton_suave.setEnabled(True)
        self.boton_one.setEnabled(True)
        self.boton_single.setEnabled(True)
        self.boton_mult.setEnabled(True)
        self.boton_filtro.setEnabled(True)
        #botones del welch
        self.tipoDeVentanaComboBox1.setEnabled(True)
        self.graficarw.setEnabled(True)
        #botones del multitaper
        self.graficarm.setEnabled(True)
        #botones del fvst
        self.graficarescalog.setEnabled(True)
        
        return self.datos
        
            
    def univ(self):
        # asigna lambda por umbral universal
        if self.boton_univ.isChecked()==True:
            #self.datos=self.selec_canal
            self.lamb=self.__coordinador.Limite_universal(self.datos, self.__x_min, self.__x_max)
            
    def minimax(self):
        # asigna lambda por umbral de minimos y máximos
        if self.boton_minimax.isChecked()==True:
            #self.datos=self.selec_canal
            self.lamb=self.__coordinador.Limite_minimax(self.datos, self.__x_min, self.__x_max)
    
    def sure(self):
        # asigna lambda por umbral sure
        if self.boton_sure.isChecked()==True:
            #datos=self.selec_canal
            self.lamb=self.__coordinador.Limite_sure(self.datos, self.__x_min, self.__x_max)
    
    def duro(self):
        # Asignación filtro duro
        if self.boton_duro.isChecked()==True:
            self.filt=self.__coordinador.filduro()
            print("Filtrado Duro")

    def suave(self):
        # Asignación filtro suave 
        if self.boton_suave.isChecked()==True:
            self.filt=self.__coordinador.filsuave()
            print("Filtrado Suave")
    
    def one(self):
        # Ponderacion One
        if self.boton_one.isChecked()==True:
            self.pond=self.__coordinador.pondone()
            print("Ponderado One")
            
    def sln(self):
        # Ponderacion single
        if self.boton_single.isChecked()==True:
            self.pond=self.__coordinador.pondsln()
            print("Ponderado Single")
    
    def mln(self):
        # Ponderacion multiple
        if self.boton_mult.isChecked()==True:
            self.pond=self.__coordinador.pondsln()
            print("Ponderado Multiple")
            
            
    def fil_signal(self):
        #ejecuta las funciones para filtrar
        datosc=self.selec_canal

        self.desc=self.__coordinador.Descomposicion(datosc, self.__x_min, self.__x_max)
        
        self.filt=self.__coordinador.Filtrado(self.lamb,self.desc[1], self.__x_min, self.__x_max)
        self.fcnmdr=self.__coordinador.Funcion_madre(self.desc[1],self.lamb, self.__x_min, self.__x_max)
        self.recon=self.__coordinador.Reconstruccion(self.desc[2], self.fcnmdr)
        #se imprime la señal sin filtrar y filtrada
        self.__sc.graficar_2senal(self.datos,self.recon)
        print("SENAL FILTRADA")
        archivo=open("Senal Filtrada.mat","w")
        archivo.write(str(self.recon))
        archivo.close()
    
    def Mostrar_senal(self):
        #Con esto elijo la senal disponibles en el paquete cargado
        self.senal=self.data[str(self.comboBox.currentText())] 
        self.__coordinador.recibirDatosSenal(self.senal)
        self.__x_min=0
        self.__x_max=2000
        #graficar utilizando el controlador
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
        self.boton_adelante.setEnabled(True)
        self.boton_atras.setEnabled(True)
        self.boton_aumentar.setEnabled(True)
        self.boton_disminuir.setEnabled(True)
        #botones del welch
        self.tipoDeVentanaComboBox1.setEnabled(True)
        self.graficarw.setEnabled(True)
        #botones del multitaper
        self.graficarm.setEnabled(True)
        #botones del fvst
        self.graficarescalog.setEnabled(True)
    
    def Me_Wavelet(self):
        fl=int(self.ft_fl.text())
        fh=int(self.ft_fh.text())
        ti=int(self.ft_ti.text())
        tf=int(self.ft_tf.text())
        fs=int(self.ft_fs.text())
        senal=self.senal-np.mean(self.senal)
        senal=np.squeeze(senal)
        N=senal.shape[0]        
        get_ipython().run_line_magic('matplotlib', 'qt')
        sampling_period =  1/fs
        Frequency_Band = [fl, fh] # Banda de frecuencia a analizar
        # Métodos de obtener las escalas para el Complex Morlet Wavelet  
        # Método 1:
        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1,N)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])]
        time_epoch = sampling_period*N
        # Analizar una epoca de un montaje (con las escalas del método 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)
        scales=np.squeeze(scales)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet
        [coef, freqs] = pywt.cwt(senal, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = (np.abs(coef)) ** 2
        if ti>=tf or (ti==0 and tf==0):
            #si no es logico simplemente muestra toda la grafica
            ti=0
            ti=int(ti)
            tf=int(max(time))         
        self.__sc.graficar_senal3D(time,freqs,power,fl,fh,ti,tf,fs)
    

    def Me_Welch(self):
        self.senal=self.senal-np.mean(self.senal)
        tamano=int(self.welch_tamano.text())
        solapamiento=int(self.welch_solapa.text())
        tipo=str(self.tipoDeVentanaComboBox1.currentText())
        fs=int(self.fsw.text())
        tamano=tamano*fs
        #defino el nfft a partir de nperseg=tamano si es potencia 2, lo deja
        if math.log2(tamano).is_integer()==True:
            nfft=tamano
            print("es igual         ")
        else:#si no, pone el siguiente numero de potencia 2 
            print("siguiente potencia       ")
            nfft=int(2 ** np.ceil(math.log2(tamano)))
            print("ceros agrgados"+str(nfft))
        f, Pxx = signal.welch(self.senal,fs,tipo,tamano, solapamiento, nfft, scaling='density')
        self.__sc.graficar_metodos(f,np.squeeze(Pxx),"welch")

    
    def Me_Multi(self):
        self.senal=self.senal-np.mean(self.senal)
        fsm=int(self.fsm.text())
        flow=int(self.flow.text())
        fhigh=int(self.fhigh.text())
        w=int(self.multiw.text())
        t=int(self.multit.text())
        ntapers=int(self.multip.text())
        tiempom=int(self.tiempom.text())
        #como pido el numero de tapers tengo que sacar el parametro q con la siguiente formula
        p=2*w*t-ntapers
        params = dict(fs = fsm, fpass = [flow, fhigh], tapers = [w, t, p], trialave = 1)
        #COMO TRIALAVE ES 1 LAS UNIDADES SON FRECUENCIAS 
        print("estooooooooooooooooo")
        print(self.senal.shape)
        print(self.senal.ndim)
        
        if not self.senal.ndim == 2:#esto para que funcione con las senales de 8 canales
            print("si entraaaaaa")
            self.senal=np.squeeeze(self.senal)
            print(self.senal.shape)
        b=int(self.senal.shape[1]/(fsm*tiempom))
        data = np.reshape(self.senal,(fsm*tiempom,b),order='F')
        Pxx, f = mtspectrumc(data, params)
        Pxx=Pxx[(f >= flow) & (f <= fhigh)]
        self.__sc.graficar_metodos(f,np.squeeze(Pxx),"multitaper")
    
        
    def cargar_senal(self):
        self.barraexist=False# esto es para ver si hay barra y eliminarla
        #se abre el cuadro de dialogo para cargar
        #* son archivos .mat y .txt
        self.boton_ok.setEnabled(False)
        self.comboBox.clear()
        self.comboBox.setEnabled(False)
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir seÃ±al","","Todos los archivos (*);;Archivos txt(*.txt)*;;Archivos mat (*.mat)*")
        if archivo_cargado != "":
            print(archivo_cargado)
            #la senal carga exitosamente entonces habilito los botones
            self.data = sio.loadmat(archivo_cargado)
            if len(self.data.keys()) <= 4:
                n=np.zeros(0)
                for i in self.data.keys():
                    n=np.append(n,i)
                self.data = self.data[n[-1]]
                #volver continuos los datos
                if n[-1]=='data':#esto hay que generalizarlos con ndim
                    sensores,puntos,ensayos=self.data.shape
                    senal_continua=np.reshape(self.data,(sensores,puntos*ensayos),order="F")
                if n[-1]=='ecg':
                    senal_continua=np.reshape(self.data,(1,self.data.shape[0]),order="F")
                #el coordinador recibe y guarda la senal en su propio .py, por eso no 
                #necesito una variable que lo guarde en el .py interfaz
                print('tipo de senal')
                print(type(senal_continua))
                print(np.shape(senal_continua))
                self.__coordinador.recibirDatosSenal(senal_continua)
                print('tipo de senal')
                print(type(senal_continua))
                print(np.shape(senal_continua))
                self.__x_min=0
                self.__x_max=2000
                #graficar utilizando el controlador
                self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
                self.boton_adelante.setEnabled(True)
                self.boton_atras.setEnabled(True)
                self.boton_aumentar.setEnabled(True)
                self.boton_disminuir.setEnabled(True)
                self.boton_canal.setEnabled(True)            
            if len(self.data.keys()) > 4:
                #agrego al combobox los nombres de cada denal
                for item in list(self.data.keys())[3::]:
                    self.comboBox.addItem(item)
                self.comboBox.setEnabled(True)
                self.boton_ok.setEnabled(True)
                self.boton_ok.clicked.connect(self.Mostrar_senal)
    
        



        