#======================================================================================================
# GNC-A Blog Python Tutorial: Part VII
#======================================================================================================# Required libraries ==================================================================================
import matplotlib.pyplot as plt # Import the Matplotlib package
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit&amp;amp;amp;amp;lt;/pre&amp;amp;amp;amp;gt;
import numpy as np # Import the Numpy package
from remap import remap # Import the Remap function
import matplotlib as matplotlib
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
from PIL import Image, ImageEnhance
import os
import imageio.v2 as imageio
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from osgeo import gdal # Add the GDAL library
import requests
import wget
import re
import time
import cv2
import urllib.request
from urllib.request import urlopen
import boto3
import botocore
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime, timezone, timedelta
#======================================================================================================
# Función para extraer la fecha de un nombre de archivo
def extraer_fecha(nombre_archivo):
    
    partes = nombre_archivo.split('_')
    fecha_str = partes[3]  # La fecha está en el cuarto elemento separado por '_'
    return datetime.strptime(fecha_str, '%d-%b-%Y-%H:%M:%S %Z')

def borrar_archivos_directorio(archivos):
    # Obtener la lista de archivos en el directorio

    # Iterar sobre cada archivo y borrarlo
    for archivo in archivos:
        if os.path.isfile(archivo):
            os.remove(archivo)

def descargar_archivo2():
    # Directorio que contiene las imágenes
    directory = '/var/py/volunclima/scripts/goes-16/Output/2/ECUADOR/'
    directory2 = '/var/py/volunclima/scripts/goes-16/Output/2/GUAYAQUIL/'
    directory3 = '/var/py/volunclima/scripts/goes-16/Output/2/GALAPAGOS/'

    directory4 = '/var/py/volunclima/scripts/goes-16/Output/2/PERU/'
    directory5 = '/var/py/volunclima/scripts/goes-16/Output/2/VENEZUELA/'
    directory6 = '/var/py/volunclima/scripts/goes-16/Output/2/COLOMBIA/'
    directory7 = '/var/py/volunclima/scripts/goes-16/Output/2/CHILE/'
    directory8 = '/var/py/volunclima/scripts/goes-16/Output/2/BOLIVIA/'
    directorios=[directory,directory2,directory3,directory4,directory5,directory6,directory7,directory8]
    for directorio_actual in directorios:
        archivos = [os.path.join(directorio_actual, file) for file in os.listdir(directorio_actual) if file.endswith('.png')]
        borrar_archivos_directorio(archivos)
    ruta_destino = "/var/py/volunclima/scripts/goes-16/GOES-16 Samples/2/"
    archivos = [os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.nc')]
    borrar_archivos_directorio(archivos)
    archivos = [os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.aux')]
    borrar_archivos_directorio(archivos)
    # Obtener la fecha y hora EST actual
    utc_time = datetime.utcnow()

    # Define the UTC offset for Eastern Standard Time (EST)
    est_offset = timedelta(hours=-5)  # EST is UTC-5
    
    # Calcular la hora actual en EST y la hora y media antes 
    est_time = utc_time + est_offset

    hora_actual_utc = utc_time.strftime("%H:%M")
    hora_media_ant = (utc_time - timedelta(hours=1, minutes=36)).strftime("%H:%M")

    # Calcular el día juliano
    start_of_year = datetime(utc_time.year, 1, 1)
    juliano_utc = (utc_time - start_of_year).days + 1
    start_of_year = datetime(utc_time.year, 1, 1)
    juliano_est = (est_time - start_of_year).days + 1
    juliano_str=str(juliano_utc).zfill(3)
    current_year = utc_time.year
    subcadena = 'CMIPF-M6C02'

    # Conexión a S3
    s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED),region_name='us-east-1')
    my_bucket = s3.Bucket('noaa-goes16')
    

    objetos = my_bucket.objects.filter(Prefix='ABI-L2-CMIPF/'+str(current_year)+'/'+juliano_str+'/')

    archivos_a_descargar = [] 
    if( '00:00' <= hora_actual_utc <= '01:00'):
        hora_actual_utc='23:59'
    # Iterar sobre todos los objetos en el bucket
    for obj in objetos.all():
        # Verificar si el nombre del objeto contiene la subcadena y está dentro del rango horario
        if subcadena in obj.key:
            
            nombre_archivo = obj.key.split('/')[-1]
            Start = (nombre_archivo[nombre_archivo.find("_s")+2:nombre_archivo.find("_e")])
            hora_archivo = Start [7:9] + ":" + Start [9:11]  # Hora de inicio del escaneo
            if hora_media_ant <= hora_archivo <= hora_actual_utc:
                archivos_a_descargar.append(obj.key)

    # Si no se encontraron archivos dentro del rango horario, retornar None
    if not archivos_a_descargar:
        return None

    # Descargar los archivos
    for archivo in archivos_a_descargar:
        nombre_archivo = archivo.split('/')[-1]
        download_file_path = os.path.join(ruta_destino, nombre_archivo)
        # Descargar el archivo desde S3 al directorio de destino local
        print(f"Descargando archivo: {nombre_archivo}")
        my_bucket.download_file(archivo, download_file_path)
        print(f"Archivo descargado: {download_file_path}")

    generar_png_CH2()
    generar_gif()
    # generar_video()


def generar_png_CH2():
    # Path to the GOES-16 image file
    path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/2/'
    paths = sorted([os.path.join(path, file) for file in os.listdir(path) if file.endswith('.nc')])
    # Choose the visualization extent (min lon, min lat, max lon, max lat)
    extent1 = [-81.1, -5.25, -75.1,  1.5] #ecuador
    #extent1 = [-120, -60, -30,  30]
    extent2 = [-80.68, -3.27, -78.98,  -0.82] #guayaquil
    extent3 = [-91.73, -1.51, -89.17,  0.69] #galapagos
    
    # Coordenadas para Perú
    extent4 = [-81.35, -19.35, -68.65, -0.01]

    # Coordenadas para Venezuela
    extent5 = [-73.35, -0.14, -59.8, 12.2]

    # Coordenadas para Colombia
    extent6 = [-79.0, -5.83, -66.85, 12.68]

    # Coordenadas para Chile
    extent7 = [-81.6, -60.58, -60.43, -17.5]

    # Coordenadas para Bolivia
    extent8 = [-69.8, -24.3, -57.28, -9.48]

    # Añadir los nuevos extents a la lista existente
    lista_extent=[extent1,extent2,extent3,extent4,extent5,extent6,extent7,extent8]
    #lista_extent = [extent1, extent2, extent3, extent4, extent5, extent6, extent7, extent8]

    # Choose the image resolution (the higher the number the faster the processing is)
    resolution = 1
    # Call the reprojection funcion
    data2= remap(paths[-1], [-120, -60, -30,  30], resolution, 'HDF5')
    data2= data2.ReadAsArray()
    # Definir los valores mínimos y máximos para el colormap
    vmin_custom = np.min(data2)
    vmax_custom = np.max(data2)
    for path in paths:
    #path=paths[-1]
        paises=[]
        paises.append(remap(path, extent1, 1, 'HDF5'))
        paises.append(remap(path, extent2, 0.1, 'HDF5'))
        paises.append(remap(path, extent3, 0.1, 'HDF5'))
        paises.append(remap(path, extent4, 1, 'HDF5'))
        paises.append(remap(path, extent5, 1, 'HDF5'))
        paises.append(remap(path, extent6, 1, 'HDF5'))
        paises.append(remap(path, extent7, 1, 'HDF5'))
        paises.append(remap(path, extent8, 1, 'HDF5'))

        for indice,pais in enumerate(paises):
        #for indice in range(3):   
            extent=lista_extent[indice]
            data = pais.ReadAsArray()
            # Define the size of the saved picture=================================================================
            DPI = 150
            ax = plt.figure(figsize=(2000/float(DPI), 2000/float(DPI)), frameon=True, dpi=DPI)

            #======================================================================================================

            # Plot the Data =======================================================================================
            # Create the basemap reference for the Rectangular Projection
            bmap = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[1], urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326)

            # Draw the countries and Brazilian states shapefiles
            if(indice ==0 or indice ==1 or indice ==2):
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/guayaquil-polygon','guayaquil-polygon',linewidth=0.5,color='white')
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/ecu_admbnda_adm1_inec_20190724','ecu_admbnda_adm1_inec_20190724',linewidth=0.50,color='white')
            if(indice ==3):
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/DEPARTAMENTOS_inei_geogpsperu_suyopomalia','DEPARTAMENTOS_inei_geogpsperu_suyopomalia',linewidth=0.5,color='white')
            
            if(indice ==4):
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/Estados_Venezuela', 'Estados_Venezuela', linewidth=0.5, color='white', default_encoding='iso-8859-15')
            
            if(indice ==5):
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/Servicios_P%C3%BAblicos_-_Departamentos','Servicios_P%C3%BAblicos_-_Departamentos',linewidth=0.5,color='white')

            if(indice ==6):
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/chl_admbnda_adm1_bcn_20211008','chl_admbnda_adm1_bcn_20211008',linewidth=0.5,color='white')

            if(indice ==7):
                bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/Departamentos_Bolivia','Departamentos_Bolivia',linewidth=0.5,color='white')

            # Draw parallels and meridians
            bmap.drawparallels(np.arange(-90.0, 90.0, 2.5), linewidth=0.3, dashes=[4, 4], color='white', labels=[False,False,False,False], fmt='%g', labelstyle="+/-", xoffset=-0.80, yoffset=-1.00, size=7)
            bmap.drawmeridians(np.arange(0.0, 360.0, 2.5), linewidth=0.3, dashes=[4, 4], color='white', labels=[False,False,False,False], fmt='%g', labelstyle="+/-", xoffset=-0.80, yoffset=-1.00, size=7)
            """ bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
            bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white') """
            # Converts a CPT file to be used in Python
            """ cpt = loadCPT('/var/py/volunclima/scripts/goes-16/Colortables/WVCOLOR35.cpt')
            # Makes a linear interpolation
            cpt_convert = LinearSegmentedColormap('cpt', cpt)
            """
            # getting the original colormap using cm.get_cmap() function 
            orig_map=matplotlib.colormaps["Greys"]

            # reversing the original colormap using reversed() function 
            reversed_map = orig_map.reversed() 

            # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
            bmap.imshow(data, origin='upper', cmap=reversed_map, vmin=vmin_custom, vmax=vmax_custom)
            
            """ cb.ax.tick_params(width = 1,direction= 'in') # Remove the colorbar ticks
            cb.ax.xaxis.set_tick_params(pad=-12.5) # Put the colobar labels inside the colorbar
            cb.ax.tick_params(axis='x', colors='black', labelsize=8, width=1) # Change the color and size of the colorbar labels """

            """ # Define los límites del colorbar y los ticks
            tick_interval = 5
            cb.set_ticks(range(-90, 5 + 1, tick_interval)) """

            # Search for the Scan start in the file name
            Start = (path[path.find("_s")+2:path.find("_e")])
            # Search for the GOES-16 channel in the file name
            Band = (path[path.find("M6C")+3:path.find("_G16")])
            # Create a GOES-16 Bands string array
            Wavelenghts = ['[]','[0.47 μm]','[0.64 μm]','[0.865 μm]','[1.378 μm]','[1.61 μm]','[2.25 μm]','[3.90 μm]','[6.19 μm]','[6.95 μm]','[7.34 μm]','[8.50 μm]','[9.61 μm]','[10.35 μm]','[11.20 μm]','[12.30 μm]','[13.30 μm]']

            # Converting from julian day to dd-mm-yyyy
            year = int(Start[0:4])
            dayjulian = int(Start[4:7]) - 1 # Subtract 1 because the year starts at "0"
            dayconventional = datetime(year,1,1) + timedelta(dayjulian) # Convert from julian to conventional
            date = dayconventional.strftime('%d-%b-%Y') # Format the date according to the strftime directives

            time = Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + " UTC" # Time of the Start of the Scan

            Unit = "Brightness Temperature [°C]"
            Institution = "CIIFEN "

            if(indice ==0):
                pad='-3.49%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
                currentAxis_londiff_factor= 0.02
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.003
                logo_GNC_pos=[680, 62]
                logo_INPE_pos=[1080, 62]
                logo_NOAA_pos=[1180, 62]
                logo_GOES_pos=[1265, 62]
                logo_CIIFEN_pos=[592, 62]
                pais="ECUADOR"
            elif(indice ==1):
                pad='-3.49%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
                currentAxis_londiff_factor= 0.02
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.003
                logo_GNC_pos=[10, 55]
                logo_INPE_pos=[400, 55]
                logo_NOAA_pos=[500, 55]
                logo_GOES_pos=[585, 55]
                logo_CIIFEN_pos=[718, 60]
                pais="GUAYAQUIL"

            elif(indice==2):
                pad='-3.49%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
                currentAxis_londiff_factor= 0.02
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.003
                logo_GNC_pos=[10, 55]
                logo_INPE_pos=[400, 55]
                logo_NOAA_pos=[500, 55]
                logo_GOES_pos=[585, 55]
                logo_CIIFEN_pos=[1465, 55]
                pais="GALAPAGOS"
            elif(indice==3):
                pad='-4.69%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + "\n " + date + " " + time
                currentAxis_londiff_factor= 0.05
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.009
                logo_GNC_pos=[10, 75]
                logo_INPE_pos=[400, 75]
                logo_NOAA_pos=[500, 75]
                logo_GOES_pos=[585, 75]
                logo_CIIFEN_pos=[718, 80]
                pais="PERU"
            elif(indice==4):
                pad='-3.49%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
                currentAxis_londiff_factor= 0.02
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.003
                logo_GNC_pos=[10, 55]
                logo_INPE_pos=[400, 55]
                logo_NOAA_pos=[500, 55]
                logo_GOES_pos=[585, 55]
                logo_CIIFEN_pos=[718, 50]
                pais="VENEZUELA"
            
            elif(indice==5):
                pad='-3.49%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
                currentAxis_londiff_factor= 0.02
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.003
                logo_GNC_pos=[10, 55]
                logo_INPE_pos=[400, 55]
                logo_NOAA_pos=[500, 55]
                logo_GOES_pos=[585, 55]
                logo_CIIFEN_pos=[718, 50]
                pais="COLOMBIA"
            elif(indice==6):
                pad='-4.79%'
                Title = "  GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + "Brightness \n  Temperature [°C]" + " " + date + " " + time
                currentAxis_londiff_factor= 0.06
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.009
                logo_GNC_pos=[5, 77]
                logo_INPE_pos=[375, 77]
                logo_NOAA_pos=[475, 77]
                logo_GOES_pos=[560, 77]
                logo_CIIFEN_pos=[693, 82]
                pais="CHILE"
            else:
                pad='-3.49%'
                Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
                currentAxis_londiff_factor= 0.02
                pltText_latdiff_factor_title= 0.003
                pltText_latdiff_factor_institution= 0.003
                logo_GNC_pos=[600, 62]
                logo_INPE_pos=[1000, 62]
                logo_NOAA_pos=[1100, 62]
                logo_GOES_pos=[1185, 62]
                logo_CIIFEN_pos=[512, 62]
                pais="BOLIVIA"
                       
            # Insert the colorbar at the bottom
            cb = bmap.colorbar(location='bottom', size = '2%', pad = pad)
            cb.outline.set_visible(False) # Remove the colorbar outline
            cb.ax.xaxis.set_ticklabels([])
            cb.ax.tick_params(width = 0,direction= 'in') # Remove the colorbar ticks
            # Add a black rectangle in the bottom to insert the image description
            lon_difference = (extent[2] - extent[0]) # Max Lon - Min Lon
            currentAxis = plt.gca()
            # Add logos / images to the plot
            logo_GNC = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GNC Logo.png')
            logo_INPE = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/INPE Logo.png')
            logo_NOAA = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/NOAA Logo.png')
            logo_GOES = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GOES Logo.png')
            logo_CIIFEN = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/ciifen.png')
            currentAxis.add_patch(Rectangle((extent[0], extent[1]), lon_difference, lon_difference * currentAxis_londiff_factor, alpha=1, zorder=3, facecolor='black'))
            # Add the image description inside the black rectangle
            lat_difference = (extent[3] - extent[1]) # Max lat - Min lat
            plt.text(extent[0], extent[1] + lat_difference * pltText_latdiff_factor_title,Title,horizontalalignment='left', color = 'white', size=10)
            plt.text(extent[2], extent[1]+ lat_difference * pltText_latdiff_factor_institution,Institution, horizontalalignment='right', color = 'white', size=10)
            ax.figimage(logo_GNC, logo_GNC_pos[0], logo_GNC_pos[1], zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, logo_INPE_pos[0], logo_INPE_pos[1], zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, logo_NOAA_pos[0], logo_NOAA_pos[1], zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, logo_GOES_pos[0], logo_GOES_pos[1], zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_CIIFEN, logo_CIIFEN_pos[0], logo_CIIFEN_pos[1], zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/2/'+pais +'/CMIPF_Band_2_'+date+'-'+time+'_'+pais+'.png', dpi=DPI, bbox_inches='tight', pad_inches=0)

            plt.close(ax)
            """ # Save the result
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/Channel_'+Band+'.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
            # Read the image
            im = Image.open('/var/py/volunclima/scripts/goes-16/Output/Channel_'+Band+'.png')
            # Image brightness enhancer
            enhancer = ImageEnhance.Brightness(im)
            factor = 1.2 #brightens the image
            im_output = enhancer.enhance(factor)
            im_output.save('/var/py/volunclima/scripts/goes-16/Output/Channel_'+Band+'_brightened.png') """

        

def generar_gif():
    # Directorio que contiene las imágenes
    directory = '/var/py/volunclima/scripts/goes-16/Output/2/ECUADOR/'
    directory2 = '/var/py/volunclima/scripts/goes-16/Output/2/GUAYAQUIL/'
    directory3 = '/var/py/volunclima/scripts/goes-16/Output/2/GALAPAGOS/'
    directory4 = '/var/py/volunclima/scripts/goes-16/Output/2/PERU/'
    directory5 = '/var/py/volunclima/scripts/goes-16/Output/2/VENEZUELA/'
    directory6 = '/var/py/volunclima/scripts/goes-16/Output/2/COLOMBIA/'
    directory7 = '/var/py/volunclima/scripts/goes-16/Output/2/CHILE/'
    directory8 = '/var/py/volunclima/scripts/goes-16/Output/2/BOLIVIA/'
    directorios=[directory,directory2,directory3,directory4,directory5,directory6,directory7,directory8]
    for indice,directorio_actual in enumerate(directorios):
        archivos = os.listdir(directorio_actual)
        # Filtrar los archivos que tienen la extensión .png y extraer la fecha de cada uno
        archivos_fecha = [(archivo, datetime.strptime(archivo.split('_')[3], '%d-%b-%Y-%H:%M:%S %Z')) for archivo in archivos if archivo.endswith('.png')]

        # Ordenar la lista de archivos_fecha por la fecha
        archivos_fecha_ordenados = sorted(archivos_fecha, key=lambda x: x[1])

        # Obtener solo los nombres de archivo ordenados
        image_files = [os.path.join(directorio_actual, archivo[0]) for archivo in archivos_fecha_ordenados]
        # Crear una lista para almacenar las imágenes
        images = []

        # Leer las imágenes y agregarlas a la lista
        for filename in image_files:
            images.append(imageio.imread(filename))
        rangoi = (image_files[0][image_files[0].find("Band_2_"):image_files[0].find(" UTC")])
        rangof = (image_files[-1][image_files[-1].find("Band_2_"):image_files[-1].find(" UTC")])

        if(indice==0):
            # Especificar el nombre del archivo de salida del GIF
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_ecuador.gif'
            output_file = directorio_actual+'band_02_ecuador.gif'
        elif(indice==1):
            # Especificar el nombre del archivo de salida del GIF
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_guayaquil.gif'
            output_file = directorio_actual+'band_02_guayaquil.gif'
        elif(indice==2):
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_galapagos.gif'
            output_file = directorio_actual+'band_02_galapagos.gif'
        elif(indice==3):
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_galapagos.gif'
            output_file = directorio_actual+'band_02_peru.gif'
        elif(indice==4):
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_galapagos.gif'
            output_file = directorio_actual+'band_02_venezuela.gif'
        elif(indice==5):
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_galapagos.gif'
            output_file = directorio_actual+'band_02_colombia.gif'
        elif(indice==6):
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_galapagos.gif'
            output_file = directorio_actual+'band_02_chile.gif'
        else:
            #output_file = directory+'band_02_'+rangoi+'_'+rangof+'_galapagos.gif'
            output_file = directorio_actual+'band_02_bolivia.gif'
        frame_duration = 5
        # Guardar las imágenes como un GIF
        imageio.mimsave(output_file, images, format='GIF', fps=2, loop=0)

        print(f"GIF creado con éxito: {output_file}")




descargar_archivo2()
""" generar_png_CH2()
generar_gif() """


