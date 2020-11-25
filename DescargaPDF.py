import os
import re
import time
from datetime import date, datetime, timedelta

import requests
from tika import parser

import pandas as pd

from FuncionesAuxiliares import cum_mean
from CambiaNombres import CambiaNombres

class DescargaPDF(CambiaNombres):
    
    def __init__ (self):
        self.url_list = []
        self.ultimo_dato_cargado = ""
        self.dias_sin_actualizar = []
        self.lista_fecha = []
        self.meses_sin_actualizar = []
        self.mes_para_url = []
        self.url_para_scrap = []
        self.archivos_para_descargar_nuevos = []
        self.meses ={"January" : "enero",
                "February" : "febrero",
                "March" : "marzo",
                "May" : "mayo",
                "April" : "abril",
                "June" : "junio",
                "July" : "julio",
                "August" : "agosto",
                "September" : "septiembre",
                "October" : "octubre",
                "November" : "noviembre",
                "December" : "diciembre"}

    def listar_url (self) -> None:
        """Convierte las url de un archivo a una lista"""
        aux = ""
        with open ("listaUrl.txt","r") as f:
            aux = f.read()
        f.close()
        self.url_list = aux.split("\n")
        self.url_list.pop()
    
    def descargar (self) -> None:
        """Descarga los archivos PDF a la carpeta establecida"""
        descargo = False
        start = time.perf_counter()
        for i in self.archivos_para_descargar_nuevos:
            if re.search(r"matu", i):
                continue
            else:
                r = requests.get(i)
                contenido = r.content
                aux_dir = re.search(r"(\w*\d.*pdf)", i)
                dire = self.ver_directorio() + "/" + aux_dir.group(1)
                print ("Se esta descargando el archivo: {} \n".format(aux_dir.group(1)))
                with open (dire, "wb") as f:
                    f.write(contenido)
                f.close()
                descargo = True
        if descargo:
            end = time.perf_counter()
            print("La descarga tomo: {}".format(end - start))

    def actualizar(self, path = "") -> None:
        """ Esta funcion va a actualizar la lista de url y descargar en caso de ser necesario"""
        self.generar_lista_dias_sin_actualizar()
        self.dias_a_lista_str()
        self.armar_url_para_scrap()
        self.generar_links_descarga()
        self.guardar_nuevas_url()
        self.descargar()
        #Si hay un path distinto al standar (no creo) se utiliza
        if path == "":
            self.cambiame_el_nombre()
        else:
            self.cambiame_el_nombre(path)

    def actualizar_ultimo_dato(self, path = "data.csv") -> None:
        """Genera el ultimo dato sin actualizar tomando una ruta hacia el archivo"""
        df = pd.read_csv(path)
        ultima_fecha_aux = df["Fecha"].tail(1)
        ultima_fecha_aux = datetime.strptime(ultima_fecha_aux, "%Y-%m-%d")
        self.ultimo_dato_cargado = datetime.strftime(ultima_fecha_aux,"%d-%m-%Y")
        

    def generar_lista_dias_sin_actualizar(self) -> None:
        """Funcion que toma el ultimo dato que se guardo y genera una lista de
        dias que no estan computados"""
        dia_act = int(time.strftime("%d",time.localtime()))
        mes_act = int(time.strftime("%m",time.localtime()))
        año_act = int(time.strftime("%Y",time.localtime()))
        aux = self.ultimo_dato_cargado.split("-")
        dia_partida = int(aux[0])
        mes_partida = int(aux[1])
        año_partida = int(aux[2])
        fecha_comienzo = date(año_partida,mes_partida,dia_partida)
        fecha_fin = date(año_act,mes_act,dia_act)
        r = (fecha_fin + timedelta(days=1) - fecha_comienzo).days
        self.dias_sin_actualizar = [fecha_comienzo + timedelta(days= i) for i in range(r)]
        self.dias_sin_actualizar.pop(0)
    
    def dias_a_lista_str(self) -> None:
        """Convierte las fechas extraidas a una lista de fechas en str se puede usar para
        varias cosas, en este caso para verificar y extraer los archivos faltntes"""
        for fecha in self.dias_sin_actualizar:
            self.lista_fecha.append((fecha.strftime("%d-%m-%y")))
    
    def ver_dias_sin_actualizar(self) ->list:
        return self.lista_fecha.sort()

    def armar_url_para_scrap(self) -> None:
        """Arma las url donde se van a scrapear los nuevos links a los pdf"""
        aux = ""
        for i in self.dias_sin_actualizar:
            if aux != self.meses[i.strftime("%B")]:
                self.mes_para_url.append((self.meses[i.strftime("%B")]))
                aux = self.meses[i.strftime("%B")]
            else:
                continue
        
        for i in self.mes_para_url:
            self.url_para_scrap.append("https://www.argentina.gob.ar/coronavirus/informe-diario/" + i + datetime.now().strftime("%Y"))

    def generar_links_descarga(self) -> None:
        """ Se encarga de generar los links nuevos para descargar"""
        lista_aux = []
        for i in self.url_para_scrap:
            r = requests.get(i)
            texto = r.text.split('"')
            for j in texto:
                if re.search(r"pdf",j):
                    lista_aux.append(j)
                else:
                    continue
        for i in lista_aux:
            for j in self.lista_fecha:
                if re.search(j,i):
                    self.archivos_para_descargar_nuevos.append(i)
                else:
                    continue

    def guardar_nuevas_url (self, archivo = "listaUrl.txt") -> None:
        """Guarda las nuevas url"""
        with open(archivo,"a+") as f:
            for i in self.archivos_para_descargar_nuevos:
                f.seek(0,0)
                f.write(i + "\n")
        f.close()