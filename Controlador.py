"""
David Alejandro Ijaji Guerrero       C.C.1017250858
Edison Sebastian Munoz Rodriguez     C.C 1214745427
"""
from Modelo import Biosenal
from interfaz import InterfazGrafico
import sys
from PyQt5.QtWidgets import QApplication
from chronux.mtspectrumc import mtspectrumc
from IPython import get_ipython
import pywt
class Principal(object):
    def __init__(self):        
        self.__app=QApplication(sys.argv)
        self.__mi_vista=InterfazGrafico()
        self.__mi_biosenal=Biosenal()
        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)
        self.__mi_vista.asignar_Controlador(self.__mi_controlador)
    def main(self):
        self.__mi_vista.show()
        sys.exit(self.__app.exec_())
    
class Coordinador(object):
    def __init__(self,vista,biosenal):
        self.__mi_vista=vista
        self.__mi_biosenal=biosenal
        
    def recibirDatosSenal(self,data):
        self.__mi_biosenal.asignarDatos(data)
        
    def devolverDatosSenal(self,x_min,x_max):
        return self.__mi_biosenal.devolver_segmento(x_min,x_max)
    
    def escalarSenal(self,x_min,x_max,escala):
        return self.__mi_biosenal.escalar_senal(x_min,x_max,escala)
    
    def devolver_canal(self, c, xmin, xmax):
        return self.__mi_biosenal.devolver_canal(c, xmin, xmax)
    
    def Limite_universal(self, li, xmin, xmax):
        return self.__mi_biosenal.Limite_universal(li, xmin, xmax)
#    
    def Limite_minimax(self, li, xmin, xmax):
        return self.__mi_biosenal.Limite_minimax(li, xmin, xmax)
#    
    def Limite_sure(self, li, xmin, xmax):
        return self.__mi_biosenal.Limite_sure(li, xmin, xmax)
#    
    def Descomposicion(self, d, xmin, xmax):
        return self.__mi_biosenal.Descomposicion(d, xmin, xmax)
    
    def Filtrado(self, li, f, xmin, xmax):
        return self.__mi_biosenal.Filtrado(li, f, xmin, xmax)
    
    def Funcion_madre(self,d,li,xmin,xmax):
        return self.__mi_biosenal.Funcion_madre(d, li, xmin, xmax)
    
    def Reconstruccion(self,ap,det):
        return self.__mi_biosenal.Reconstruccion(ap,det)
        
    def pondone(self):
        return self.__mi_biosenal.pondone()
    
    def pondsln(self):
        return self.__mi_biosenal.pondone()
    
    def pondmln(self):
        return self.__mi_biosenal.pondone()
    
    def filduro(self):
        return self.__mi_biosenal.filduro()
    
    def filsuave(self):
        return self.__mi_biosenal.filsuave()
    
    
p=Principal()
p.main()
