from datetime import date, datetime, timedelta
import os

import matplotlib.dates as mdates
import numpy as np
from matplotlib import pyplot as plt

from FuncionesAuxiliares import cum_mean
from LectorYExtractorDeDatosPDF import ObtenerDatos


class Grafico(ObtenerDatos):

    def __init__ (self):
        self._lista_muertes = []
        self._lista_infecciones = []
        self._lista_fechas = []
        ObtenerDatos.__init__(self, "Archivos")

    def generar_listas(self, archivo = "/data.txt") -> None:
        """Arma las listas de datos importantes para poder suministrar a la grafica"""
        archivo = os.getcwd() + archivo
        with open(archivo, "r") as datos:
            dat = datos.read()
        datos.close()   
        dat_aux = dat.split(";")
        dat_aux.pop()

        #Muerte
        for x in range (2,len(dat_aux),3):
            self._lista_muertes.append(int(dat_aux[x]))
        self._lista_muertes = np.array(self._lista_muertes)

        #Fecha
        for x in range (0,len(dat_aux),3):
            fecha_aux = dat_aux[x] + "-2020"
            fecha_aux = datetime.strptime(fecha_aux, "%d-%m-%Y")
            self._lista_fechas.append(fecha_aux)

        #Casos
        for x in range (1,len(dat_aux),3):
            self._lista_infecciones.append(int((dat_aux[x])))
        self._lista_infecciones = np.array(self._lista_infecciones)

    def ver_lista_de_muertes(self) -> list:
        """Permite ver las muertes en formato lista"""
        return self._lista_muertes

    def ver_lista_de_infecciones(self) -> list:
        """Permite ver las infecciones en formato lista"""
        return self._lista_infecciones

    def ver_lista_de_fechas(self) -> list:
        """Permite ver las fechas en formato lista"""
        return self._lista_fechas

    def grafico_dia_a_dia(self) -> None:
        """Realiza el grafico de las nuevas infecciones y muertes dia a dia"""

        plt.xlabel("Fecha")
        plt.ylabel("Casos Nuevos")
        plt.title("Casos nuevos Covid-19")

        #Grafico de los diferentes casos y tipos
        plt.plot(self._lista_fechas,self._lista_infecciones,label = "Nuevos casos")
        plt.plot(self._lista_fechas, cum_mean(self._lista_infecciones), label = "Infecciones Promedio")
        plt.plot(self._lista_fechas,cum_mean(self._lista_muertes), label = "Muertes promedio")
        plt.plot(self._lista_fechas,self._lista_muertes,label = "Nuevas Muertes")
        plt.legend(loc="best")

        #Anotaciones extra
        aux = np.where(self._lista_infecciones == np.max(self._lista_infecciones))
        infecciones_max_pos = int(self._lista_infecciones[aux[0]])
        infecciones_max_pos_text = infecciones_max_pos - 15
        fecha_pos = self._lista_fechas[int(aux[0])]
        fecha_pos_text = fecha_pos - timedelta(days=15)
        plt.annotate("Pico \nactual",
                    xy=(fecha_pos,infecciones_max_pos),
                    xytext=(fecha_pos_text,infecciones_max_pos_text),
                    arrowprops= dict(facecolor='black', shrink=0.05))
        
        #Seteo de fechas orden y muestra en eje x
        date_format = mdates.DateFormatter("%d-%m") #Se le entrega el formato de la fecha
        plt.gca().xaxis.set_major_formatter(date_format) #Se setea el formato de la fecha 
        plt.gca().set_xlim(self._lista_fechas[0],self._lista_fechas[-1])
        plt.gca().set_ylim(np.min(self._lista_infecciones),np.max(self._lista_infecciones))
        plt.xticks(rotation = 45)
        plt.grid(True)
        
        #Mostrar grafico
        plt.tight_layout() #Evita que se vaya todo fuera de la grafica
        plt.show()
    
    def grafico_datos_totales(self) -> None:
        plt.xlabel("Fecha")
        plt.ylabel("Casos totales")
        plt.title("Casos Totales Covid-19")
        
        plt.plot_date(self._lista_fechas,np.cumsum(self._lista_infecciones), "r" ,
                    label = "Infecciones totales: {}".format(np.sum(self._lista_infecciones)))

        plt.plot_date(self._lista_fechas,np.cumsum(self._lista_muertes),"k",
                    label = "Muertes Totales: {}".format(np.sum(self._lista_muertes)) + "*")

        plt.legend(loc = "best")

        #Seteo de fechas orden y muestra en eje x
        date_format = mdates.DateFormatter("%d-%m") #Se le entrega el formato de la fecha
        plt.gca().xaxis.set_major_formatter(date_format) #Se setea el formato de la fecha 
        #plt.gca().set_xlim(self._lista_fechas[0],self._lista_fechas[-1])
        plt.xticks(rotation = 45)
        plt.grid(True)
        plt.xlim(self._lista_fechas[0],self._lista_fechas[-1])
        plt.ylim(0,np.max(np.sum(self._lista_infecciones)))
        
        plt.show()

    def checar(self) -> None:
        ayer = datetime.now() - timedelta(days=1)
        self.actualizar_ultimo_dato("data.txt")
        if self.ultimo_dato_cargado == datetime.now().strftime("%d-%m-%Y"):
            print("Tiene los archivos actualizados a la fecha actual: {}".format(datetime.today()))
        elif self.ultimo_dato_cargado == ayer.strftime("%d-%m-%Y") and datetime.now().hour < 21:
            print("Tiene los archivos actualizados, la proxima actualizacion es cerca de las 21hs")
        else:
            self.dame_los_datos()
            self.guardar_datos()

    def grafico_totales(self) -> None:
        pass

def main():
    opcion = str (input ("Elegi la opcion: \n 1- Grafico de Totales \n 2- Muestra diario \n 3- Muestra del ultimo dato cargado \n"))
    
    g = Grafico()
    
    # Esta mostrando el grafico acumulado
    if opcion == "1":
        g.checar()
        g.generar_listas()
        g.grafico_datos_totales()

    #Muestra de Grafico

    elif opcion == "2":
        g.checar()
        g.generar_listas()
        g.grafico_dia_a_dia()

    elif opcion == "3":
        g.generar_listas()
        ultima_fecha = g.ver_lista_de_fechas()
        ultimo_infectado = g.ver_lista_de_infecciones()
        print("La ultima fecha es: {}".format(ultima_fecha[-1]))
        print("El ultimo registro de infectados es: {}".format(ultimo_infectado[-1]))
    
    #input("Salida")




if __name__ == '__main__':
    main()
    