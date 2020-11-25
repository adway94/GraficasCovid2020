import os
import re
import time
from datetime import date, datetime, timedelta

import requests
from tika import parser

from FuncionesAuxiliares import cum_mean

class CambiaNombres:
    """ Esta clase se encarga de cambiar el nombre a todos los archivos para poder
    conseguir un standar con formato reporteddmmaav.pdf"""
    
    def __init__(self) -> None:
        """Constructor de la clase"""
        self._lista_archivos = []
        self._caracteres_malos = ["-","_"]
        self._lista_corregida =[]
        self._fechas_dd_mm_aa = []

    def cambiar_nombre_standar(self, fecha = []) -> None:
        """Standariza al formato reporteddmmaav.pdf en caso de no ingresar datos, si se ingresa una lista
        devuelve los datos standarizados, tiene que recibir una fecha en formato dd-mm-aaaa*"""
        if fecha == []:
            fecha = self._fechas_dd_mm_aa
            for i in fecha: 
                aux = str(i)
                aux = "".join(j for j in aux if not j in self._caracteres_malos)
                if len(aux) > 6:
                    aux = aux[:6]
                if aux[-1:] == "2":
                    aux = "0" + aux[:5]
                self._lista_corregida.append("reporte" + aux + "v.pdf")
        else:
            lista_aux = []
            for i in fecha: 
                aux = str(i)
                aux = "".join(j for j in aux if not j in self._caracteres_malos)
                if len(aux) > 6:
                    aux = aux[:6]
                if aux[-1:] == "2":
                    aux = "0" + aux[:5]
                lista_aux.append("reporte" + aux + "v.pdf")    
            return lista_aux
    
    def definir_directorio(self, path="/Archivos"):
        self.path = os.getcwd() + path

    def ver_directorio(self) -> str:
        return self.path

    def ver_lista_archivos(self) -> list:
        return self._lista_corregida

    def lista_fechas_formato(self) -> None:
        """arma una lista en formato dd-mm-aa"""
        aux = ""
        self._lista_archivos = os.listdir(self.path)
        for i in self._lista_archivos:
            aux += str(i)
        self._fechas_dd_mm_aa = (re.findall(r"(\d*.-\d*.-\d+[-_])", aux))
    

    def modificar_nombres_del_directorio(self) -> None:
        """Se toman la lista (o nombre) de archivo/s a cambiar, y los nombres nuevos (tienen que estar ordenados)
        adicionalmente se le puede poner un directorio en caso q no sea raiz"""
        for i in range(len(self._lista_corregida)):
            self._lista_archivos[i] = self.path + "/" + self._lista_archivos[i]
            self._lista_corregida[i] = self.path + "/" +  self._lista_corregida[i]
            try:
                os.renames(self._lista_archivos[i],self._lista_corregida[i])
            except FileExistsError:
                print("El archivo {} existe\n".format(self._lista_corregida[i]))
                os.replace(self._lista_archivos[i],self._lista_corregida[i])
            finally:
                pass
                
    
    def cambiame_el_nombre(self, path="/Archivos") -> None:
        """Se asigna el directorio y hace que los nombres se cambien, es lo que hace la magia"""
        self.definir_directorio(path)
        self.lista_fechas_formato()
        self.cambiar_nombre_standar()
        self.modificar_nombres_del_directorio()

    #Aca Van funciones sin uso practico    
    def ver_fecha(self, count = None) -> list:
        """Herramienta de testeo, no tiene uso practico"""
        if count == None:
            return self._fechas_dd_mm_aa
        else:
            return self._fechas_dd_mm_aa[count]

    def comparar (self):
        for i in range(len(self._lista_archivos)):
            print(self._lista_archivos[i] + "es igual a: " + self._fechas_dd_mm_aa[i] +"\n")

    def generar_nombre(self, fechas):
        """Genera los nombres para agregar al csv"""
        corrected_date = []
        for i in fechas:
            i = datetime.strptime(i,"%Y-%m-%d")
            corrected_date.append(datetime.strftime(i,"%d-%m-%Y")) 
        return self.cambiar_nombre_standar(corrected_date)


        

