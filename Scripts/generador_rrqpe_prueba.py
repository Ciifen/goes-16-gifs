#======================================================================================================
# GNC-A Blog Python Tutorial: Part VII
#======================================================================================================# Required libraries ==================================================================================
from termios import VMIN
import matplotlib.pyplot as plt # Import the Matplotlib package
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit&amp;amp;amp;amp;lt;/pre&amp;amp;amp;amp;gt;
import numpy as np # Import the Numpy package
import cartopy.feature as cfeature
from remap3 import remap # Import the Remap function
import matplotlib.patheffects as path_effects
from matplotlib.colors import ListedColormap
import os
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
from matplotlib.colors import Normalize
from datetime import datetime, timezone, timedelta
 
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from osgeo import gdal # Add the GDAL library
import matplotlib.ticker as tkr

import boto3
import botocore
from botocore import UNSIGNED
from botocore.client import Config
import os
import time
#======================================================================================================
def descargar_generar_archivo():
    # Obtener la fecha y hora EST actual
    utc_time = datetime.utcnow()
    # Define the UTC offset for Eastern Standard Time (EST)
    est_offset = timedelta(hours=-5)  # EST is UTC-5

    # Add the UTC offset for EST
    est_time = utc_time + est_offset
    start_of_year = datetime(est_time.year, 1, 1)
    juliano=(est_time - start_of_year).days + 1
    juliano_str= str(juliano).zfill(3)
    
    print(juliano_str)
    s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED),region_name='us-east-1')
    my_bucket = s3.Bucket('noaa-goes16')
    current_year = est_time.year
    flag=True
    while(flag):
        objects = my_bucket.objects.filter(Prefix='ABI-L2-RRQPEF/'+str(current_year)+'/'+juliano_str+'/23/')
        bucketObjects = list(objects)
        print(len(bucketObjects))
        if (len(bucketObjects)==6):
            flag=False
        else:
            time.sleep(60)
    print("descargando")
    s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED),region_name='us-east-1')
    my_bucket = s3.Bucket('noaa-goes16')
    objects2 = my_bucket.objects.filter(Prefix='ABI-L2-RRQPEF/'+str(current_year)+'/'+juliano_str+'/')
    print(objects2)
    download_path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/RRQPE'
    for obj in objects2:
        
        path, filename = os.path.split(obj.key)
        print(filename)
        download_file_path = os.path.join(download_path, filename)
        my_bucket.download_file(obj.key, download_file_path)
        
    generar_png_RRQPE()
    ruta_destino = "/var/py/volunclima/scripts/goes-16/GOES-16 Samples/RRQPE/"
    aux_files = [os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.xml')] 
    nc_files = sorted([os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.nc')])
    # Eliminar los archivos XML
    for archivo in aux_files:
        os.remove(archivo)
    # Eliminar los archivos nc
    for archivo in nc_files:
        os.remove(archivo)

def generar_png_RRQPE():
    # Load the Data =======================================================================================
    # Path to the GOES-16 image file
    path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/RRQPE/'
    paths = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.nc')]

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
    extent6 = [-79.0, -6.23, -66.85, 12.68]

    # Coordenadas para Chile
    extent7 = [-81.6, -60.58, -60.43, -17.5]

    # Coordenadas para Bolivia
    extent8 = [-69.8, -24.3, -57.28, -9.48]

    # Añadir los nuevos extents a la lista existente
    lista_extent=[extent1,extent2,extent3,extent4,extent5,extent6,extent7,extent8]
    #extent = [-120, -60, -30,  30]
    # Choose the image resolution (the higher the number the faster the processing is)
    resolution = 2.0
    paises=[]
    # Call the reprojection funcion
    paises.append(remap(paths, extent1, resolution, 'HDF5'))
    paises.append(remap(paths, extent2, resolution, 'HDF5'))
    paises.append(remap(paths, extent3, resolution, 'HDF5'))
    paises.append(remap(paths, extent4, resolution, 'HDF5'))
    paises.append(remap(paths, extent5, resolution, 'HDF5'))
    paises.append(remap(paths, extent6, resolution, 'HDF5'))
    paises.append(remap(paths, extent7, resolution, 'HDF5'))
    paises.append(remap(paths, extent8, resolution, 'HDF5'))
    most_common_value=0.0
    for indice,pais in enumerate(paises):
        extent=lista_extent[indice]
        # Read the data returned by the function and convert it to Celsius
        data = pais.ReadAsArray() 
        #======================================================================================================

        # Suponiendo que 'data' es tu matriz anidada
        data_flat = data.flatten()  # Aplanar la matriz para obtener una lista plana de elementos
        max_val=np.max(data_flat)
        min_val=np.min(data_flat)
        unique_values, counts = np.unique(data_flat, return_counts=True)  # Obtener valores únicos y sus frecuencias
        
        # Encontrar el índice del valor más repetido
        most_common_index = np.argmax(counts)

        # Obtener el valor más repetido y su frecuencia
        if indice==0:
            most_common_value = unique_values[most_common_index]
        
        #print(most_common_value)
        # Crea una máscara para el rango de datos
        mask = (data == most_common_value)
        # Define the size of the saved picture=================================================================
        DPI = 150
        ax = plt.figure(figsize=(2000/float(DPI), 2000/float(DPI)), frameon=True, dpi=DPI)

        #======================================================================================================
        
        # Plot the Data =======================================================================================
        # Create the basemap reference for the Rectangular Projection
        bmap = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[1], urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326)
        
        # Draw the countries and Brazilian states shapefiles
        if(indice ==0 or indice ==1 or indice ==2):
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/guayaquil-polygon','guayaquil-polygon',linewidth=0.5,color='black')
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/ecu_admbnda_adm1_inec_20190724','ecu_admbnda_adm1_inec_20190724',linewidth=0.50,color='black')
        if(indice ==3):
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/DEPARTAMENTOS_inei_geogpsperu_suyopomalia','DEPARTAMENTOS_inei_geogpsperu_suyopomalia',linewidth=0.5,color='black')
        
        if(indice ==4):
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/Estados_Venezuela', 'Estados_Venezuela', linewidth=0.5, color='black', default_encoding='iso-8859-15')
        
        if(indice ==5):
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/Servicios_P%C3%BAblicos_-_Departamentos','Servicios_P%C3%BAblicos_-_Departamentos',linewidth=0.5,color='black')

        if(indice ==6):
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/chl_admbnda_adm1_bcn_20211008','chl_admbnda_adm1_bcn_20211008',linewidth=0.5,color='black')

        if(indice ==7):
            bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/Departamentos_Bolivia','Departamentos_Bolivia',linewidth=0.5,color='black')
        # Draw parallels and meridians
        bmap.drawparallels(np.arange(-90.0, 90.0, 2.5), linewidth=0.3, dashes=[4, 4], color='white', labels=[False,False,False,False], fmt='%g', labelstyle="+/-", xoffset=-0.80, yoffset=-1.00, size=7)
        bmap.drawmeridians(np.arange(0.0, 360.0, 2.5), linewidth=0.3, dashes=[4, 4], color='white', labels=[False,False,False,False], fmt='%g', labelstyle="+/-", xoffset=-0.80, yoffset=-1.00, size=7)
        """ bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
        bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white') """
        # Converts a CPT file to be used in Python
        cpt = loadCPT('/var/py/volunclima/scripts/goes-16/Colortables/precip2_17lev.cpt')
        # Makes a linear interpolation
        original_cmap  = LinearSegmentedColormap('cpt', cpt)
        
        # Número de intervalos para cada color
        num_intervals = [1, 1, 1, 1, 10,10,10,10,10,10,10,10,10,10,10,10,10,10]  # El primer color tiene menos intervalos

        # Normaliza los intervalos para que sumen 1
        total_intervals = sum(num_intervals)
        norm_intervals = [num / total_intervals for num in num_intervals]

        # Colores base del colormap original
        base_colors = original_cmap(np.linspace(0, 1, len(num_intervals)))

        # Crea una lista personalizada de colores con intervalos ajustados e interpolación lineal
        custom_colors = []
        for i, (color, interval) in enumerate(zip(base_colors, norm_intervals)):
            if i < len(base_colors) - 1:
                next_color = base_colors[i + 1]
                interpolated_colors = np.linspace(color, next_color, int(interval * total_intervals) + 1)
                custom_colors.extend(interpolated_colors[:-1])  # Excluye el último color para evitar duplicados
            else:
                custom_colors.extend([color] * int(interval * total_intervals))

        # Definir los colores en formato hexadecimal (azul claro y azul oscuro)
        color_light_blue = '#7dddff'
        color_dark_blue = '#003366'

        # Crear el nuevo colormap
        custom_cmap = LinearSegmentedColormap.from_list('CustomBlue', [color_light_blue, color_dark_blue])
        custom_cmap.set_bad(color='grey')
        if (0<=max_val<1):
            # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
            bmap.imshow(np.ma.masked_where(mask, data), origin='upper', cmap=custom_cmap, vmin =0,vmax = 1)
        else:
            # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
            bmap.imshow(np.ma.masked_where(mask, data), origin='upper', cmap=custom_cmap, vmin =0)
        
        path=paths[0]
        # Search for the Scan start in the file name
        Start = (path[path.find("_s")+2:path.find("_e")])
        # Search for the GOES-16 channel in the file name
        #Band = (path[path.find("M6C")+3:path.find("_G16")])
        # Create a GOES-16 Bands string array
       
        # Converting from julian day to dd-mm-yyyy
        year = int(Start[0:4])
        dayjulian = int(Start[4:7]) - 1 # Subtract 1 because the year starts at "0"
        dayconventional = datetime(year,1,1) + timedelta(dayjulian) # Convert from julian to conventional
        date = dayconventional.strftime('%d-%b-%Y') # Format the date according to the strftime directives
        
        #time = Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + " UTC" # Time of the Start of the Scan
        
        Unit = "millimeters per day [mm/day]"
        Institution = "CIIFEN "
        
        
        if(indice ==0):
            pad='-3.39%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation " + Unit + " " + date
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
            pad='-3.39%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation " + Unit + " " + date
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
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation " + Unit + " " + date
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
            pad='-4.81%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation\n " + Unit + " " + date
            currentAxis_londiff_factor= 0.06
            pltText_latdiff_factor_title= 0.003
            pltText_latdiff_factor_institution= 0.003
            logo_GNC_pos=[10, 75]
            logo_INPE_pos=[400, 75]
            logo_NOAA_pos=[500, 75]
            logo_GOES_pos=[585, 75]
            logo_CIIFEN_pos=[718, 80]
            pais="PERU"
        elif(indice==4):
            pad='-3.49%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation " + Unit + " " + date
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
            pad='-4.81%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation\n " + Unit + " " + date
            currentAxis_londiff_factor= 0.06
            pltText_latdiff_factor_title= 0.003
            pltText_latdiff_factor_institution= 0.003
            logo_GNC_pos=[10, 77]
            logo_INPE_pos=[400, 77]
            logo_NOAA_pos=[500, 77]
            logo_GOES_pos=[585, 77]
            logo_CIIFEN_pos=[718, 82]
            pais="COLOMBIA"
        elif(indice==6):
            pad='-4.81%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation\n " + Unit + " " + date
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
            pad='-3.51%'
            Title = " GOES-16 ABI RRQPE Daily Precipitation estimation " + Unit + " " + date
            currentAxis_londiff_factor= 0.02
            pltText_latdiff_factor_title= 0.003
            pltText_latdiff_factor_institution= 0.003
            logo_GNC_pos=[600, 62]
            logo_INPE_pos=[1000, 62]
            logo_NOAA_pos=[1100, 62]
            logo_GOES_pos=[1185, 62]
            logo_CIIFEN_pos=[512, 62]
            pais="BOLIVIA"
        

            
        cb = bmap.colorbar(location='bottom', size = '2%', pad = pad, aspect=46, shrink=1.0)
        #bmap.imshow(data, origin='upper', cmap=custom_cmap)
        # Insert the colorbar at the bottom
        cb.outline.set_visible(False) # Remove the colorbar outline
        cb.ax.tick_params(width = 1,direction= 'in') # Remove the colorbar ticks
        cb.ax.xaxis.set_tick_params(pad=-12.5) # Put the colobar labels inside the colorbar
        cb.ax.tick_params(axis='x', colors='white', labelsize=8, width=1) # Change the color and size of the colorbar labels
        #cb.ax.invert_xaxis()

        print (str(max_val)+ " "+pais)
        if (0<=max_val<1):
            # Configuración del colorbar
            tick_interval = 0.1
            cb.outline.set_edgecolor('white')
            ticks = np.arange(0, 1 + tick_interval, tick_interval)
            ticks = ticks[1:-1]  # Eliminar el primer y último tick

            cb.set_ticks(ticks)
            cb.ax.tick_params(labelsize=8, labelcolor='white')
            cb.ax.tick_params(width = 1,direction= 'in') # Remove the colorbar ticks
            cb.ax.xaxis.set_tick_params(pad=-12.5) # Put the colobar labels inside the colorbar

            for j in plt.getp(cb.ax.axes, 'xticklabels'):
                j.set_fontsize(8)
                j.set_bbox(dict(facecolor='white', edgecolor='None', alpha=0.01))
                j.set_rotation(0)
            


            #print(ticks)
        
        elif (1<=max_val<5):
            tick_interval = 1
            cb.set_ticks(range(0, int(max_val), tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:])
        # Define los límites del colorbar y los ticks
        elif (5<=max_val<20):
            tick_interval = 2
            cb.set_ticks(range(0, int(max_val), tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:])
        elif (20<=max_val<120):
            tick_interval = 5
            cb.set_ticks(range(0, int(max_val), tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:])
        elif (120<=max_val<200):
            tick_interval = 10
            cb.set_ticks(range(0, int(max_val), tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:])
        # Define los límites del colorbar y los ticks
        elif (200<=max_val<600):
            tick_interval = 20
            cb.set_ticks(range(0, int(max_val), tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:])
        elif (600<=max_val<2500):
            tick_interval = 100
            cb.set_ticks(range(0, int(max_val) , tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:-1])
        else:
            tick_interval = 500
            cb.set_ticks(range(0, int(max_val), tick_interval))
            cb.ax.set_xticks(cb.ax.get_xticks()[1:])
        # Add logos / images to the plot
        logo_GNC = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GNC Logo.png')
        logo_INPE = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/INPE Logo.png')
        logo_NOAA = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/NOAA Logo.png')
        logo_GOES = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GOES Logo.png')
        logo_CIIFEN = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/ciifen.png')
        # Add a black rectangle in the bottom to insert the image description
        lon_difference = (extent[2] - extent[0]) # Max Lon - Min Lon
        currentAxis = plt.gca()
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
        plt.savefig('/var/py/volunclima/scripts/goes-16/Output/RRQPE/rrqpe_estimation_'+pais+'.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        plt.close(ax)
        # Export the result to GeoTIFF
        """ driver = gdal.GetDriverByName('GTiff')
        driver.CreateCopy('E:\\VLAB\\Python\\Output\\Channel_13.tif', grid, 0) """
        #======================================================================================================

descargar_generar_archivo()
#generar_png_RRQPE()