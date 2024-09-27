#======================================================================================================
# GNC-A Blog Python Tutorial: Part VII
#======================================================================================================# Required libraries ==================================================================================
import matplotlib.pyplot as plt # Import the Matplotlib package
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit&amp;amp;amp;amp;lt;/pre&amp;amp;amp;amp;gt;
import numpy as np # Import the Numpy package
import cartopy.feature as cfeature
from remap2 import remap # Import the Remap function
import matplotlib.patheffects as path_effects
import os
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
 
from datetime import datetime, timezone, timedelta
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from osgeo import gdal # Add the GDAL library
import boto3
import botocore
from botocore import UNSIGNED
from botocore.client import Config
import os
import requests
import re
import time
import wget
import urllib.request
from urllib.request import urlopen
#======================================================================================================


def descargar_archivo():
    # URL base del directorio
    base_url = "https://geo.nsstc.nasa.gov/satellite/goes16/abi/l2/fullDisk/"
    ruta_destino = "/var/py/volunclima/scripts/goes-16/GOES-16 Samples/LST/"
    # Patrón de expresión regular para extraer el número después de 'c' en el nombre del archivo
    pattern = re.compile(r"c(\d+)\.nc$")
    nc_files = sorted([os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.nc')])
      
    # Tipos de archivos a procesar
    #file_types = ["CMIPF-M6C02", "CMIPF-M6C08", "CMIPF-M6C14","LSTF"]
    file_type =  "LSTF"
    # Descargar el archivo con el número más alto para cada tipo
    max_number = 0
    max_file_url = ""
    # Obtener la lista de archivos en el directorio
    print("antes del request")
    response = requests.get(base_url)
    print("despues del request")
    file_list = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
    for file_name in file_list:
        if file_type in file_name:
            match = pattern.search(file_name)
            if match:
                current_number = int(match.group(1))
                if current_number > max_number:
                    max_number = current_number
                    max_file_url = base_url + file_name
    nombre_archivo2 = os.path.basename(max_file_url)
    if len(nc_files) != 0:
        nombre_archivo =os.path.basename(nc_files[-1])
        if nombre_archivo2==nombre_archivo:
            print("return vacio")
            return 
    print("descargando")
    # Obtener el nombre del archivo de la URL
    nombre_archivo = os.path.basename(max_file_url)
    # Construir la ruta completa de destino
    ruta_completa_destino = os.path.join(ruta_destino, nombre_archivo)
    urllib.request.urlretrieve(max_file_url, ruta_completa_destino)
    # Construir la ruta completa de destino
    print(f"Archivo descargado: {nombre_archivo}")
    path = max_file_url
    Start = (path[path.find("_s")+2:path.find("_e")])
    hora = Start [7:9] + ":" + Start [9:11]  # Hora de inicio del escaneo
    print(hora)


descargar_archivo()
#generar_png_LST()