
import numpy as np;
import matplotlib.pyplot as plt;
import scipy.io as sio;
#Carga de señal
mat_contents = sio.loadmat(r'ecg.mat')
#los campos que tenga la señal 
print("Los campos carga son: " + str(mat_contents.keys()));
#se ponen la señal y se dimensiona como  vector de 1D
signal = mat_contents['ecg'];
signal = np.squeeze(signal);
#Numero de datos que tiene originalmente
longitud_original = signal.shape[0];
def Descomposicion(señal):
    #Esta funcion pide como parametro una señal y entrega dos diccionarios uno  
    #con los detalles y otro con las aproximaciones, ademas de la señal compuesta
    #de la ultima aproximacion y los detalles de forma descendente
    wavelet = [-1/np.sqrt(2) , 1/np.sqrt(2)];
    scale = [1/np.sqrt(2) , 1/np.sqrt(2)];
    #defino el maximo numero de descomposiciones
    level=np.floor(np.log2(señal.shape[0]/len(wavelet))-1)
    aproximaciones={}
    detalles={}
    todos_detalles=[]
    #este ciclo recorre todos los nivele de descomposición
    for i in np.arange(1,level+1):
    #verificar si el numero de datos es par y corregirlo
        if (señal.shape[0] % 2) != 0:
            señal=np.append(señal, 0);
            
        #Convolucion de la aproximacion se pone desde el primero saltando 2
        Aprox = np.convolve(señal,scale,'full');
        Aprox = Aprox[1::2];
        
        #el mismo proceso para el detalle
        Detail = np.convolve(señal,wavelet,'full');
        Detail = Detail[1::2];
        
        #Guardamos todo para despues usar lo que queremos
        aproximaciones[i]=Aprox
        detalles[i]=Detail
        todos_detalles=np.append(todos_detalles,Detail)
        señal=Aprox
        
    señal_th=np.concatenate((aproximaciones[level],todos_detalles[::-1]))
    return señal_th,detalles,aproximaciones 

[señal,detalles,aproximaciones]=Descomposicion(signal)
        
def Filtrado(tipo,lamb,detalles):
    #esta funcion hace el filtrado en si, recibe el tipo de filtrado, el vector de 
    #lambda a utilizar y genera los detalles fitrados
    lista_detalles=[]
    detallesf={}
    k=0
    print("XXXXXXXXXXXVALOR DE LAMBDA" + str(lamb))
    #este ciclo recorre cada vector del deatlles en su diccionario
    for cada_detalle in detalles.values():
        #para cada detalle hay un lamba creado en la funcion madre, se escoge solo uno aca
        lambe=lamb[int(k)]
        print("XXXXXXXXXXxxxxxxxxxXVALOR DE LAMBDe" + str(lamb))
        for cada_valor in cada_detalle:
            #se escoge cada valor de cada nivel del detalle
            if abs(cada_valor) >= lambe:
                #si es mayor a lamba se agrega el mismo valor
                lista_detalles=np.append(lista_detalles,cada_valor)
            if abs(cada_valor) < lambe:
                #si es menor entonces depende del tipo de filtrado
                if tipo=='suave':
                    lista_detalles=np.append(lista_detalles,np.sign(cada_valor)*(cada_valor-lambe))
                if tipo=='fuerte':
                    lista_detalles=np.append(lista_detalles,0)
        #cada que pase de nivel en detalles agrego esa filtracion a detallesf
        detallesf[int(k+1)]=lista_detalles.tolist()
        lista_detalles=[]#reinicio la lista una vez l a guardo
        k=k+1#cambio mi lambda[k]
    return detallesf

def Funcion_madre(descomposicion,umbral,ponderacion,tipo_filtro):
    #esta funcion recibe todos los datos y genera el filtrado con ayuda de Filtrado
    #descopongo en señal;detalles y aproximaciones
    [señal,detalles,aproximaciones]=descomposicion#descompongo en los vectores establecidos
    # genero el umbral que necesito, segun se escoja en consola
    if(umbral=='universal'):
        print("Limite universal")
        lamb=np.sqrt(2*np.log10(señal.shape[0]))
    if(umbral=='minimax'):
        print("minimax")
        longitud=int(señal.shape[0])
        lamb=0.3936 + (0.1829*(np.log10(longitud/np.log10(2))))
        
    ####Despues hago la ponderacion del lamba segun sea el caso
    if(ponderacion=='One'):
        print("entra en One")#vector de lambdas
        lamb_pass=np.zeros(int(max(detalles.keys())))+lamb#tantos lambda como detalles
        detalles1=Filtrado(tipo_filtro,lamb_pass,detalles)#filtro
    if(ponderacion=='sln'):
        print("entra en sln")
        primer_detalle=detalles[1]
        sigma=np.median(primer_detalle)/0.6745#se calcula la ponderacion
        lamb_pass=np.zeros(int(max(detalles.keys())))+lamb#agrego todos los labda
        lamb_pass[0]=sigma*lamb#el primer labda se agraga
        print(lamb_pass)
        detalles1=Filtrado(tipo_filtro,lamb_pass,detalles)#filtro
    if(ponderacion=='mln'):
        print("entra en mln")
        lamb_pass=[]
        for cada_detalle in detalles.values():#creo todos los lamba de cada vector
            sigma=np.median(cada_detalle)/0.6745
            lamb_ponderado=sigma*lamb
            lamb_pass=np.append(lamb_pass,lamb_ponderado)
        print(lamb_pass)
        detalles1=Filtrado(tipo_filtro,lamb_pass,detalles)#filtro
    return detalles1
            
detalles_filtrados=Funcion_madre(Descomposicion(signal),'universal','mln','fuerte')  

def Reconstruccion(aproximaciones,detalles_f):
    ##toma los detalles filtrados las aproximaciones y las reconstruye
    wavelet_inv = [1/np.sqrt(2) , -1/np.sqrt(2)];
    scale_inv = [1/np.sqrt(2) , 1/np.sqrt(2)];
    level=int(max(detalles_f.keys()))#numero de niveles de descomposicion y reconstruccion
    npoints_aprox=aproximaciones[level].shape[0]#longitud de ultimo detalle
    for i in np.arange(1,level+1)[::-1]:#se hace la reconstruccion en descenso
        print('i es: '+str(i))
        Aprox_inv = np.zeros((2*npoints_aprox));
        Aprox_inv[0::2] = aproximaciones[int(i)];
        Aprox_inv[1::2] = 0;#se hace el sobremuestreo
        APROX = np.convolve(Aprox_inv,scale_inv,'full');#conveolucion con la escala invertida
        npoints_aprox = detalles[i].shape[0];
        Detail_inv3 = np.zeros((2*npoints_aprox));#se repite el procedimiento de sobredimensionar
        Detail_inv3[0::2] = detalles[int(i)];
        Detail_inv3[1::2] = 0;
        DETAIL = np.convolve(Detail_inv3,wavelet_inv,'full');
        X = APROX + DETAIL;#se genera la señal que se sigue reusando hasta terminar la reconstruccion
        if i-1>=1:#para que no salte error antes de llegar al return
            if X.shape[0] > detalles[i-1].shape[0]:#para que concuerden los tamaños 
                #con el siguiente ciclo
                print("Quitando ceros");
                X = X[0:detalles[i-1].shape[0]];
            Aprox_inv=X#la aproximacion es la resultante del anterior proceso
            npoints_aprox=len(X)#actualiza la longitud
        else:#si ya llega al ultimo nivel sale del proceso y entrega la reconstruccion
            return X

señal_recontruida= Reconstruccion(aproximaciones,detalles_filtrados)

print(señal_recontruida)
plt.subplot(2,1,1)
plt.plot(signal,'r')
plt.subplot(2,1,2)
plt.plot(señal_recontruida,'b')



