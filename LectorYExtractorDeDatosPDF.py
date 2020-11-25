import os
import re
import time
from datetime import date, datetime, timedelta

import requests
from tika import parser

from FuncionesAuxiliares import cum_mean

from DescargaPDF import DescargaPDF

#Dieron de alta al primer caso https://www.infobae.com/sociedad/2020/03/12/dieron-de-alta-al-primer-infectado-por-coronavirus-en-la-argentina/



class ObtenerDatos(DescargaPDF):
    """ Esta clase se encarga de extraer todos los datos necesarios para hacer el grafico."""

    def __init__(self, path = "/Archivos"   ):
        """Inicializa el destino donde se van a obtener los datos"""
        self.path = os.getcwd() + path
        self.infectados_lista = []
        self.muertes_lista = []
        self.infectados_str = ""
        self.muertes_str = ""
        self.fechas = []
        self.fechas_wiped = []
        self.lista_archivos = []
        self.datos_combinados = ""
        self.lista_fecha = []
        self._fallecidos_con_parentesis = r"\D.*[(](\d+)[)].*falle"
        self._fallecidos_sin_parentesis =r"\D.*([ ]\d+).*falle|([ ]\d+)\n\n.*falle"
        self._ajuste_a_las_muertes_totales = -11
        self.primer_infectado_fecha = "05-03"

    def obtener_fechas(self) -> None:
        """Toma la direccion y retorna las fechas en formato dd-mm-aaaa"""
        self.directorio = os.listdir(self.path)
        aux = ""
        fecha = []
        self.lista_fecha.clear()
        for i in self.directorio:
            aux = str(i)
            fecha = aux[7:9] + "-" + aux[9:11] + "-" + "20" + aux[11:13]
            self.lista_fecha.append(fecha)

    def ordenar_fechas(self) -> None:
        """ Se encarga de ordenar las fechas"""
        self.lista_fecha.sort(key=lambda x: time.mktime(time.strptime(x,"%d-%m-%Y")))
    
    def procesar_infectados(self, contenido:str) -> None:
        """Procesa los infectados teniendo en cuenta el texto"""
        casos = re.search(r"confirmados\s(\d*)\snuevos",contenido)
        if casos == None:
            casos = re.search(r"[(](\d+)[)]|nuevo|caso",contenido)  
            if casos.group(1) == None:
                lista_aux =re.findall(r"[(](\d+)[)]|nuevo|caso",contenido)
                for m in lista_aux:
                    if m != "":
                        self.infectados_str += m + ";"
                        break
            else:
                self.infectados_str += casos.group(1) + ";"
        else:
            self.infectados_str += casos.group(1) + ";"

    def procesar_muertes(self,contenido:str) -> None:
        """Extrae los fallecidos de un texto"""
        muertos = re.search(r"(\d+).*muerte",contenido)
        if muertos == None:
            muertos = re.search(self._fallecidos_con_parentesis,contenido) 
            if muertos == None:
                muertos = re.search(self._fallecidos_sin_parentesis,contenido)
                if muertos == None:
                    self.muertes_str += "0;"
                elif muertos.group(1) != None:
                    self.muertes_str += self.control_regex(muertos.group(1).strip() + ";")
                elif muertos.group(2) != None:
                    self.muertes_str += self.control_regex(muertos.group(2).strip() + ";")
            elif muertos.group(1) != None:

                self.muertes_str += self.control_regex(muertos.group(1).strip() + ";")
            elif muertos.group(2) != None:
                self.muertes_str += self.control_regex(muertos.group(2).strip() + ";")
        else:
                self.muertes_str += muertos.group(1).strip() + ";"
        
    def parsear_textos (self, lista_nombres = []) -> None:
        """ La funcion se encarga de tomar una lista de archvios y extraer la cantidad de nuevos infectados, tambien
        acepta una lista y los parsea """
        if self.lista_fecha == []:
            pass
        elif lista_nombres != []: #En caso que se le otorgue una lista
            for i in lista_nombres:
                archivo = self.path + "/" + str(i)
                raw = parser.from_file(archivo) # Se lee el archivo
                self.procesar_infectados(raw["content"])
                self.procesar_muertes(raw["content"])
        else:
            for i in self.cambiar_nombre_standar(self.lista_fecha):
                archivo = self.path + "/" + str(i)
                raw = parser.from_file(archivo) # Se lee el archivo
                self.procesar_infectados(raw["content"])
                self.procesar_muertes(raw["content"])
    
    def wipe_2020(self) -> None:
        """Elimina el 2020 de la fecha para lograr algo mas sintetico y legible"""
        aux = ""
        for i in range(len(self.lista_fecha)):
            aux = self.lista_fecha[i]
            aux = aux[0:5]
            self.fechas_wiped.append(aux)

    def combinar(self) -> None:
        """ Genera un str fotmato: Fecha;Infectado;muerte... """
        self.infectados_lista = self.infectados_str.split(";")
        self.muertes_lista = self.muertes_str.split(";")
        self.muertes_lista.pop()
        self.infectados_lista.pop()
        for i in range(len(self.fechas_wiped)):
            self.datos_combinados += str(self.fechas_wiped[i]) + ";" + str(self.infectados_lista[i]) + ";" + str(self.muertes_lista[i]) + ";"

    def ver_datos_combinados(self) -> str:
        """Muestra los datos combinados"""
        return self.datos_combinados
    
    def ver_fechas_wiped(self) -> list:
        """Devuelve las fechas sin el 2020"""
        return self.fechas_wiped

    def dame_los_datos(self) -> None:
        """Esta funcion hace que toda la maquinaria ande, y entrega los datos"""
        self.actualizar()
        self.obtener_fechas()
        self.ordenar_fechas()
        self.parsear_textos()
        self.wipe_2020()
        self.combinar()
        #return self.ver_datos_combinados()

    def ver_muertes(self) -> list:
        """muestra las muertes en una lista"""
        return self.muertes_lista
    
    def fecha_y_muerte (self) -> list:
        """Funcion auxiliar de testeo NO USABLE """
        auxi = []
        for i in range(len(self.fechas_wiped)):
            auxi.append(str(self.fechas_wiped[i]) + ":  " + str(self.muertes_lista[i]))  
        return auxi
    
    def guardar_datos(self, nombre_archivo:str = "data.txt") -> None:
        """Guarda los datos en un archivo con la terminacion deseada"""
        with open (nombre_archivo,"w") as fuck:
            fuck.write(self.datos_combinados)
        fuck.close()
        

    def ultimo_guardado(self) -> bool:
        """esta funcion va a checar que esten los datos actualizados"""
        pass

    def dame_el_texto(self, archivo:str) -> str:
        """Funcion de testeo para ver el texto de un archivo particular"""
        raw = parser.from_file(archivo)
        return raw["content"]

    def control_regex(self,valor:str) -> str:
        """Evita que se acumulen valores, por lo que los corrige evitando repeticiones"""
        valor = int(valor.replace(";", ""))
        aux = self.muertes_str.split(";")
        aux.pop()
        if aux[-1:] == valor:
            return str("0;")
        else:
            restando = aux[-1:]
            rest = int(restando[0])
            return str(valor - rest) + ";"

    def obtener_muertos_acumulado(self) -> int:
        """Suma todos los muertos y entrega un acumulado"""
        suma = 0
        for i in self.muertes_lista:
            suma += int(i)
        return (suma + self._ajuste_a_las_muertes_totales)
    
    def obtener_infectados_acumulado(self) -> int:
        """Suma todos los infectados y los devuelve en una lista"""
        suma = 0
        for i in self.infectados_lista:
            suma += int(i)
        return suma

    