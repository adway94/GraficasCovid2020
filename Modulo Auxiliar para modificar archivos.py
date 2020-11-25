import numpy as np

#Abrir el archivo a modificar

with open ("Graficas para coronavirus/Covid19.txt", "r") as datos:
    solucion = datos.read()
datos.close()

#Abro la lista de muertes para anexar
with open("Graficas para coronavirus/aliba.txt", "r") as datos:
    muertes = datos.read()
datos.close()

#Se definen las variables aux y se crean las listas
m_aux = muertes.split(";")
aux = solucion.split(";")
solucion = ""
i = 0

#iteracion para armar el archivo final
for x in aux:

    print (str(solucion))


#Guardar archivo
with open ("Graficas para coronavirus/test.txt","w") as datos:
    datos.write(solucion)
datos.close()


