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
        #esta clase permite añadir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        #se anade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        #se añade el campo de graficos
        layout.addWidget(self.__sc)
        
        #se organizan las se�ales 
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
        self.graficarescalog.clicked.connect(self.Grafica_fvt)
        
#        Botones para el segundo trabajo
        
#        welch
        self.welch_tamano.setValidator(QIntValidator())
        self.welch_solapa.setValidator(QIntValidator())
        self.nfft.setValidator(QIntValidator())
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
        self.graficarm.setEnabled(False)
#       frecuencia vs tiempo
#        self.tffs.setValidator(QIntValidator())
        self.FT_fh.setValidator(QIntValidator())
        self.FT_fl.setValidator(QIntValidator())
        self.FT_fs.setValidator(QIntValidator())
#        self.TF_sh.setValidator(QIntValidator())
#        self.TF_tl.setValidator(QIntValidator())
#        self.TF_th.setValidator(QIntValidator())
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
        # Selecciona y grafica un canal espec�fico
        canal = int(self.campo_canal.text())
        self.datos=self.__coordinador.devolver_canal(canal, self.__x_min, self.__x_max)
        desc=self.__coordinador.Descomposicion(canal, self.__x_min, self.__x_max)
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
        return self.datos
        
            
    def univ(self):
        # asigna lambda por umbral universal
        if self.boton_univ.isChecked()==True:
            #self.datos=self.selec_canal
            self.lamb=self.__coordinador.Limite_universal(self.datos, self.__x_min, self.__x_max)
            
    def minimax(self):
        # asigna lambda por umbral de minimos y m�ximos
        if self.boton_minimax.isChecked()==True:
            #self.datos=self.selec_canal
            self.lamb=self.__coordinador.Limite_minimax(self.datos, self.__x_min, self.__x_max)
    
    def sure(self):
        # asigna lambda por umbral sure
        if self.boton_sure.isChecked()==True:
            #datos=self.selec_canal
            self.lamb=self.__coordinador.Limite_sure(self.datos, self.__x_min, self.__x_max)
    
    def duro(self):
        # Asignaci�n filtro duro
        if self.boton_duro.isChecked()==True:
            self.filt=self.__coordinador.filduro()
            print("Filtrado Duro")

    def suave(self):
        # Asignaci�n filtro suave 
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
        #se imprime la se�al sin filtrar y filtrada
        self.__sc.graficar_2senal(self.datos,self.recon)
        print("SENAL FILTRADA")
        archivo=open("Senal Filtrada.mat","w")
        archivo.write(str(self.recon))
        archivo.close()
    
    def Mostrar_senal(self):
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
    
    def Grafica_fvt(self):
        fs=int(self.FT_fs.text())
        fl=int(self.FT_fl.text())
        fh=int(self.FT_fh.text())
        senal=self.senal-np.mean(self.senal)
        senal=np.squeeze(senal)
        N=senal.shape[0]        
        get_ipython().run_line_magic('matplotlib', 'qt')
        sampling_period =  1/fs
        Frequency_Band = [fl, fh] # Banda de frecuencia a analizar
        # M�todos de obtener las escalas para el Complex Morlet Wavelet  
        # M�todo 1:
        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1,N)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])]
        time_epoch = sampling_period*N
        # Analizar una epoca de un montaje (con las escalas del m�todo 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la se�al
        time = np.arange(0, time_epoch, sampling_period)
        scales=np.squeeze(scales)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet
        [coef, freqs] = pywt.cwt(senal, scales, 'cmor', sampling_period)
        # Calcular la potencia 
        power = np.power(np.abs(coef),2)
        # Graficar el escalograma obtenido del an�lisis tiempo frecuencia
        f, ax = plt.subplots(figsize=(15, 10))
        scalogram = ax.contourf(time,
                        freqs[(freqs >= 4) & (freqs <= 40)],
                        power[(freqs >= 4) & (freqs <= 40),:],
                         100, # Especificar 20 divisiones en las escalas de color 
                         extend='both')
        ax.set_ylim(4, 40)
        ax.set_ylabel('Frequencia [Hz]')
        ax.set_xlabel('Tiempo [s]')
        cbar = plt.colorbar(scalogram)

    def Me_Welch(self):
        self.senal=self.senal-np.mean(self.senal)
        tamano=int(self.welch_tamano.text())
        solapamiento=int(self.welch_solapa.text())
        tipo=str(self.tipoDeVentanaComboBox1.currentText())
        fs=int(self.fsw.text())
        nfft=int(self.nfft.text())
        f, Pxx = signal.welch(self.senal,fs,tipo,tamano, solapamiento, nfft, scaling='density')
        self.__coordinador.recibirDatosSenal(Pxx)
        self.__x_min=0
        self.__x_max=2000
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    
    def Me_Multi(self):
        self.senal=self.senal-np.mean(self.senal)
        fsm=int(self.fsm.text())
        flow=int(self.flow.text())
        fhigh=int(self.fhigh.text())
        w=int(self.multiw.text())
        t=int(self.multit.text())
        p=int(self.multip.text())
        params = dict(fs = fsm, fpass = [flow, fhigh], tapers = [w, t, p], trialave = 1)
        data = np.reshape(self.senal,(fsm*5,10),order='F')
        Pxx, f = mtspectrumc(data, params)
        Pxx=Pxx[(f >= 4) & (f <= 40)]
        Pxx=Pxx.reshape(1,len(Pxx))
        self.__coordinador.recibirDatosSenal(Pxx)
        self.__x_min=0
        self.__x_max=2000
        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    
        
    def cargar_senal(self):
        #se abre el cuadro de dialogo para cargar
        #* son archivos .mat y .txt
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Todos los archivos (*);;Archivos txt(*.txt)*;;Archivos mat (*.mat)*")
        if archivo_cargado != "":
            print(archivo_cargado)
            #la senal carga exitosamente entonces habilito los botones
            self.data = sio.loadmat(archivo_cargado)
            if len(self.data.keys()) <= 4:
                self.data = self.data["data"]
                #volver continuos los datos
                sensores,puntos,ensayos=self.data.shape
                senal_continua=np.reshape(self.data,(sensores,puntos*ensayos),order="F")
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
                for item in list(self.data.keys())[3::]:
                    self.comboBox.addItem(item)
                self.comboBox.setEnabled(True)
                self.boton_ok.setEnabled(True)
                self.boton_ok.clicked.connect(self.Mostrar_senal)
                print("SENAL CARGADA")
                print("SELECCIONE SENAL")
    
        



        