"""
David Alejandro Ijaji Guerrero       C.C.1017250858
Edison Sebastian Munoz Rodriguez     C.C 1214745427
"""
import numpy as np
import math
from chronux.mtspectrumc import mtspectrumc
from IPython import get_ipython
import pywt
class Biosenal(object):
    def __init__(self,data=None):

        if not data==None:
            self.asignarDatos(data)
        else:
            self.__data=np.asarray([])
            self.__canales=0
            self.__puntos=0
    def asignarDatos(self,data):
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
        
    def asignarDatos2(self,data):
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        #prevengo errores logicos
        if x_min>=x_max:
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[:,x_min:x_max]
    
    def devolver_canal(self, canal, x_min,x_max):
        #Se previenen errores logicos
        if (x_min >= x_max) and (canal > self.__canales):
            return None
        #Se toma valores que se necesita en la bioseñal
        self.datac=self.__data[canal, x_min:x_max]
        return self.datac
    
    def Descomposicion(self,señal, x_min, x_max):
        #Esta funcion pide como parametro una señal y entrega dos diccionarios uno  
        #con los detalles y otro con las aproximaciones, ademas de la señal compuesta
        #de la ultima aproximacion y los detalles de forma descendente
        wavelet = [-1/np.sqrt(2) , 1/np.sqrt(2)];
        scale = [1/np.sqrt(2) , 1/np.sqrt(2)];
        #defino el maximo numero de descomposiciones
        self.data1=self.datac
        self.level=0
        self.level=np.floor(np.log2(self.data1.shape[0]/len(wavelet))-1)
        self.aproximaciones={}
        self.detalles={}
        todos_detalles=[]
        #este ciclo recorre todos los nivele de descomposición
        for i in np.arange(1,self.level+1):
        #verificar si el numero de datos es par y corregirlo
            
            if (self.data1.shape[0] % 2) != 0:
                self.data1=np.append(self.data1, 0);
                
            #Convolucion de la aproximacion se pone desde el primero saltando 2                
            Aprox = np.convolve(self.data1,scale,'full');
            Aprox = Aprox[1::2];
            #el mismo proceso para el detalle
            Detail = np.convolve(self.data1,wavelet,'full');
            Detail = Detail[1::2];
            #Guardamos todo para despues usar lo que queremos
            self.aproximaciones[i]=Aprox
            self.detalles[i]=Detail
            todos_detalles=np.append(todos_detalles,Detail)
            self.data1=Aprox
            
        self.señal_th=np.concatenate((self.aproximaciones[self.level],todos_detalles[::-1]))
        return self.señal_th, self.detalles, self.aproximaciones 
#    
    def Limite_universal(self,señal, x_min, x_max):
        #se encuentra el valor de lambda usando el limite universal
        print("Limite universal")
        self.lamb=np.sqrt(2*np.log10(self.señal_th.shape[0]))
        print("El valor de lambda es: "+str(self.lamb))
        return self.lamb
#    
    def Limite_minimax(self,señal, x_min, x_max):
        #se encuentra el valor de lambda usando el limite minimax
        print("limite minimax")
        self.longitud=0
        self.lamb=0
        longitud=int(self.señal_th.shape[0])
        self.lamb=0.3936 + (0.1829*(math.log10(longitud/math.log10(2))))
        print("El valor de lambda es: "+str(self.lamb))
        return self.lamb
    
    def Limite_sure(self,señal, x_min, x_max):
        #se encuentra el valor de lambda usando el limite sure
        print("liminte sure")
        long=0
        self.lamb=0
        long=int(self.señal_th.shape[0])
        self.ps = np.power(np.sort(abs(self.señal_th )),2);
        risks = long-2*np.arange(0,long)+(np.cumsum(self.ps.shape[0])+(np.arange(long,0,-1)*self.ps.shape[0]))/long
        best = min(risks);
        self.lamb = math.sqrt(np.power(abs(best),2));
        print("El valor de lambda es: "+str(self.lamb))
        return self.lamb
    
    def pondone(self):
        self.pond=1
        return self.pond
    
    def pondsln(self):
        self.pond=2
        return self.pond
    
    def pondmln(self):
        self.pond=3
        return self.pond

    def filduro(self):
        self.fil=1
        return self.fil

    def filsuave(self):
        self.fil=2
        return self.fil
    
    def Filtrado(self,lamb,detalles, x_min, x_max):
        #esta funcion hace el filtrado en si, recibe el tipo de filtrado, el vector de 
        #lambda a utilizar y genera los detalles fitrados
        

       self.lista_detalles=[]
       self.detallesf={}
       k=0
       #este ciclo recorre cada vector del deatlles en su diccionario
       for cada_detalle in self.detalles.values():
           #para cada detalle hay un lamba creado en la funcion madre, se escoge solo uno aca
          
           lambe=self.lamb
           for cada_valor in cada_detalle:

               #se escoge cada valor de cada nivel del detalle
               if abs(cada_valor) >= lambe:
#                   print("IF MAYORQUE")
                   #si es mayor a lamba se agrega el mismo valor
                   self.lista_detalles=np.append(self.lista_detalles,cada_valor)
               if abs(cada_valor) < lambe:
#                   print("IF MENORQUE")
                   #si es menor entonces depende del tipo de filtrado
                   if self.fil==2:
#                       print("BOTON_SUAVE")
                       self.lista_detalles=np.append(self.lista_detalles,np.sign(cada_valor)*(cada_valor-lambe))
                   if self.fil==1:
#                       print("BOTON_DURO")
                       self.lista_detalles=np.append(self.lista_detalles,0)
                       
           #cada que pase de nivel en detalles agrego esa filtracion a detallesf
           self.detallesf[int(k+1)]=self.lista_detalles.tolist()
           self.lista_detalles=[]#reinicio la lista una vez l a guardo
           k=k+1#cambio mi lambda[k]
       return self.detallesf
   
    def Funcion_madre(self,descomposicion,umbral, x_min, x_max):
        #esta funcion recibe todos los datos y genera el filtrado con ayuda de Filtrado
        # genero el umbral que necesito, segun se escoja en consola

            
        ####Despues hago la ponderacion del lamba segun sea el caso
        if self.pond==1:
            print("entra en One") #vector de lambdas
            lamb_pass=np.zeros(int(max(self.detalles.keys())))+self.lamb#tantos lambda como detalles
            self.detalles1=self.Filtrado(lamb_pass,self.detalles, x_min, x_max)#filtro
            
        if self.pond==2:
            print("entra en sln")
            primer_detalle=self.detalles[1]
            sigma=np.median(primer_detalle)/0.6745#se calcula la ponderacion
            lamb_pass=np.zeros(int(max(self.detalles.keys())))+self.lamb#agrego todos los labda
            lamb_pass[0]=sigma*self.lamb#el primer labda se agraga
            print(lamb_pass)
            self.detalles1=self.Filtrado(lamb_pass,self.detalles, x_min, x_max)#filtro
            
        if self.pond==3:
            print("entra en mln")
            lamb_pass=[]
            for cada_detalle in self.detalles.values():#creo todos los lamba de cada vector
                sigma=np.median(cada_detalle)/0.6745
                lamb_ponderado=sigma*self.lamb
                lamb_pass=np.append(lamb_pass,lamb_ponderado)
            print(lamb_pass)
            self.detalles1=self.Filtrado(lamb_pass,self.detalles, x_min, x_max)#filtro
        return self.detalles1


    def Reconstruccion(self, aproximaciones, detallesf):
        ##toma los detalles filtrados las aproximaciones y las reconstruye
        wavelet_inv = [1/np.sqrt(2) , -1/np.sqrt(2)];
        scale_inv = [1/np.sqrt(2) , 1/np.sqrt(2)];
        level=int(max(self.detalles1.keys()))#numero de niveles de descomposicion y reconstruccion
        npoints_aprox=self.aproximaciones[level].shape[0]#longitud de ultimo detalle
        for i in np.arange(1,level+1)[::-1]:#se hace la reconstruccion en descenso
            print('i es: '+str(i))
            Aprox_inv = np.zeros((2*npoints_aprox));
            Aprox_inv[0::2] = self.aproximaciones[int(i)];
            Aprox_inv[1::2] = 0;#se hace el sobremuestreo
            APROX = np.convolve(Aprox_inv,scale_inv,'full');#conveolucion con la escala invertida
            npoints_aprox = self.detalles[i].shape[0];
            Detail_inv3 = np.zeros((2*npoints_aprox));#se repite el procedimiento de sobredimensionar
            Detail_inv3[0::2] = self.detalles[int(i)];
            Detail_inv3[1::2] = 0;
            DETAIL = np.convolve(Detail_inv3,wavelet_inv,'full');
            X = APROX + DETAIL;#se genera la señal que se sigue reusando hasta terminar la reconstruccion
            if i-1>=1:#para que no salte error antes de llegar al return
                if X.shape[0] > self.detalles[i-1].shape[0]:#para que concuerden los tamaños 
                    #con el siguiente ciclo
                    print("Quitando ceros");
                    X = X[0:self.detalles[i-1].shape[0]];
                Aprox_inv=X#la aproximacion es la resultante del anterior proceso
                npoints_aprox=len(X)#actualiza la longitud
            else:#si ya llega al ultimo nivel sale del proceso y entrega la reconstruccion
                return X
#%%
    def escalar_senal(self,x_min,x_max,escala):
        copia_datos=self.__data[:,x_min:x_max].copy()
        return copia_datos*escala