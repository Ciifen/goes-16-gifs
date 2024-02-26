#======================================================================================================
# GNC-A Blog Python Tutorial: Part VII
#======================================================================================================# Required libraries ==================================================================================
import matplotlib.pyplot as plt # Import the Matplotlib package
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit&amp;amp;amp;amp;lt;/pre&amp;amp;amp;amp;gt;
import numpy as np # Import the Numpy package
import cartopy.feature as cfeature
from remap import remap # Import the Remap function
import matplotlib.patheffects as path_effects

from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import os
import datetime # Library to convert julian day to dd-mm-yyyy
import imageio.v2 as imageio
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from osgeo import gdal # Add the GDAL library
import requests
import re
import time
#======================================================================================================
def descargar_archivo():
  # URL base del directorio
  base_url = "https://geo.nsstc.nasa.gov/satellite/goes16/abi/l2/fullDisk/"
  ruta_destino = "/var/py/volunclima/scripts/goes-16/GOES-16 Samples/8/"
  # Patrón de expresión regular para extraer el número después de 'c' en el nombre del archivo
  pattern = re.compile(r"c(\d+)\.nc$")
  nc_files = sorted([os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.nc')])
  aux_files = [os.path.join(ruta_destino, file) for file in os.listdir(ruta_destino) if file.endswith('.xml')]
  # Eliminar los archivos XML
  for archivo in aux_files:
      os.remove(archivo)
  # Tipos de archivos a procesar
  #file_types = ["CMIPF-M6C02", "CMIPF-M6C08", "CMIPF-M6C14","LSTF"]
  file_type =  "CMIPF-M6C08"
  # Descargar el archivo con el número más alto para cada tipo


  max_number = 0
  max_file_url = None
  while(1):
      # Obtener la lista de archivos en el directorio
      response = requests.get(base_url)
      file_list = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)

      for file_name in file_list:
          if file_type in file_name:
              match = pattern.search(file_name)
              if match:
                  current_number = int(match.group(1))
                  if current_number > max_number:
                      max_number = current_number
                      max_file_url = base_url + file_name
      
      if len(nc_files)==0:
        break
      else:
        if nc_files[-1]==max_file_url:
          time.sleep(10)
          pass
        else:
          os.remove(nc_files[0])
          break  
  response = requests.get(max_file_url)
  # Obtener el nombre del archivo de la URL
  nombre_archivo = os.path.basename(max_file_url)
  # Construir la ruta completa de destino
  ruta_completa_destino = os.path.join(ruta_destino, nombre_archivo)
  # Escribir el contenido descargado en el archivo en la nueva ruta
  with open(ruta_completa_destino, 'wb') as file:
    file.write(response.content)
  print(f"Archivo descargado: {os.path.basename(max_file_url)}")

def generar_png_CH8():
  # Load the Data =======================================================================================
  # Path to the GOES-16 image file
  path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/8/'
  paths = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.nc')]

  # Choose the visualization extent (min lon, min lat, max lon, max lat)
  extent1 = [-81.1, -5.25, -75.1,  1.5] #ecuador
  extent2 = [-80.105, -2.305, -79.855,  -2.01] #guayaquil
  extent3 = [-91.73, -1.51, -89.17,  0.69] #galapagos
  lista_extent=[extent1,extent2,extent3]
  #extent = [-120, -60, -30,  30]
  # Choose the image resolution (the higher the number the faster the processing is)
  resolution = 2.0
  
  # Call the reprojection funcion
  for path in paths:
    paises=[]
    paises.append(remap(path, extent1, resolution, 'HDF5'))
    paises.append(remap(path, extent2, resolution, 'HDF5'))
    paises.append(remap(path, extent3, resolution, 'HDF5'))
    for indice,pais in enumerate(paises):
      extent=lista_extent[indice]
      data = pais.ReadAsArray() - 273.15
      # Define the size of the saved picture=================================================================
      DPI = 150
      ax = plt.figure(figsize=(2000/float(DPI), 2000/float(DPI)), frameon=True, dpi=DPI)

      #======================================================================================================
      
      # Plot the Data =======================================================================================
      # Create the basemap reference for the Rectangular Projection
      bmap = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[1], urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326)
      
      # Draw the countries and Brazilian states shapefiles
      #bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/ne_10m_admin_0_countries','ne_10m_admin_0_countries',linewidth=0.50,color='white')
      if (indice == 1):
        bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/guayaquil-polygon','guayaquil-polygon',linewidth=0.5,color='black')
      else:
        bmap.readshapefile('/var/py/volunclima/scripts/goes-16/Shapefiles/ecu_admbnda_adm1_inec_20190724','ecu_admbnda_adm1_inec_20190724',linewidth=0.50,color='black')
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
      # Define los colores personalizados y los intervalos
      cvals = [-92,-80,
              -79,-70,
              -69, -60,
              -59, -50,-49,-46,
              -45,  -25,        -20,-17,-16, -9, -3,-2, 7]
      colors  = ['#c5c59b','#ebeb09',
                '#f51f00', '#6b0000',
                '#00fa00', '#006d00',
                '#0004f3', '#000067','#5082b4', '#6a99c8',
                'white',  '#2e2e2e'      , '#dc6700','#ef7400', '#da0000', '#4f1e1e','#fc4a4a','#bebe00', '#bebe00']



      norm=plt.Normalize(min(cvals),max(cvals))
      tuples = list(zip(map(norm,cvals), colors))
      # Crea el mapa de colores segmentado linealmente
      cpt_convert = LinearSegmentedColormap.from_list('', tuples)

      # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
      bmap.imshow(data, origin='upper', cmap=cpt_convert,norm=norm)
      # Insert the colorbar at the bottom
      cb = bmap.colorbar(location='bottom', size = '2%', pad = '-3.49%')
      cb.outline.set_visible(False) # Remove the colorbar outline
      cb.ax.tick_params(width = 1,direction= 'in') # Remove the colorbar ticks
      cb.ax.xaxis.set_tick_params(pad=-12.5) # Put the colobar labels inside the colorbar
      cb.ax.tick_params(axis='x', colors='black', labelsize=8, width=1) # Change the color and size of the colorbar labels
      cb.ax.invert_xaxis()

      # Define los límites del colorbar y los ticks
      tick_interval = 5
      cb.set_ticks(range(-90, 5 + 1, tick_interval))

      # Search for the Scan start in the file name
      Start = (path[path.find("_s")+2:path.find("_e")])
      # Search for the GOES-16 channel in the file name
      Band = (path[path.find("M6C")+3:path.find("_G16")])
      # Create a GOES-16 Bands string array
      Wavelenghts = ['[]','[0.47 μm]','[0.64 μm]','[0.865 μm]','[1.378 μm]','[1.61 μm]','[2.25 μm]','[3.90 μm]','[6.19 μm]','[6.95 μm]','[7.34 μm]','[8.50 μm]','[9.61 μm]','[10.35 μm]','[11.20 μm]','[12.30 μm]','[13.30 μm]']
      
      # Converting from julian day to dd-mm-yyyy
      year = int(Start[0:4])
      dayjulian = int(Start[4:7]) - 1 # Subtract 1 because the year starts at "0"
      dayconventional = datetime.datetime(year,1,1) + datetime.timedelta(dayjulian) # Convert from julian to conventional
      date = dayconventional.strftime('%d-%b-%Y') # Format the date according to the strftime directives
      
      time = Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + " UTC" # Time of the Start of the Scan
      
      Unit = "Brightness Temperature [°C]"
      Title = " GOES-16 ABI CMI Band " + Band + " " + Wavelenghts[int(Band)] + " " + Unit + " " + date + " " + time
      Institution = "CIIFEN "
      
      # Add a black rectangle in the bottom to insert the image description
      lon_difference = (extent[2] - extent[0]) # Max Lon - Min Lon
      currentAxis = plt.gca()
      currentAxis.add_patch(Rectangle((extent[0], extent[1]), lon_difference, lon_difference * 0.015, alpha=1, zorder=3, facecolor='black'))
      
      # Add the image description inside the black rectangle
      lat_difference = (extent[3] - extent[1]) # Max lat - Min lat
      plt.text(extent[0], extent[1] + lat_difference * 0.003,Title,horizontalalignment='left', color = 'white', size=10)
      plt.text(extent[2], extent[1],Institution, horizontalalignment='right', color = 'white', size=10)
      
      # Add logos / images to the plot
      logo_GNC = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GNC Logo.png')
      logo_INPE = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/INPE Logo.png')
      logo_NOAA = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/NOAA Logo.png')
      logo_GOES = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GOES Logo.png')
      """ ax.figimage(logo_GNC, 10, 50, zorder=3, alpha = 1, origin = 'upper')
      ax.figimage(logo_INPE, 400, 50, zorder=3, alpha = 1, origin = 'upper')
      ax.figimage(logo_NOAA, 500, 50, zorder=3, alpha = 1, origin = 'upper')
      ax.figimage(logo_GOES, 585, 50, zorder=3, alpha = 1, origin = 'upper') """
      if(indice ==0):
        ax.figimage(logo_GNC, 700, 58, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_INPE, 1100, 58, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_NOAA, 1200, 58, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_GOES, 1285, 58, zorder=3, alpha = 1, origin = 'upper')
        plt.savefig('/var/py/volunclima/scripts/goes-16/Output/8/ECUADOR/CMIPF_Band_8_'+date+'_'+time+'_ECUADOR.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
      elif(indice ==1):
        ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper')
        plt.savefig('/var/py/volunclima/scripts/goes-16/Output/8/GUAYAQUIL/CMIPF_Band_8_'+date+'_'+time+'_GUAYAQUIL.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
      else:
        ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper')
        plt.savefig('/var/py/volunclima/scripts/goes-16/Output/8/GALAPAGOS/CMIPF_Band_8_'+date+'_'+time+'_GALAPAGOS.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
      plt.close(ax)
      # Export the result to GeoTIFF
      """ driver = gdal.GetDriverByName('GTiff')
      driver.CreateCopy('E:\\VLAB\\Python\\Output\\Channel_13.tif', grid, 0) """
      #======================================================================================================



def generar_gif():
  # Directorio que contiene las imágenes
  directory = '/var/py/volunclima/scripts/goes-16/Output/8/ECUADOR/'
  directory2 = '/var/py/volunclima/scripts/goes-16/Output/8/GUAYAQUIL/'
  directory3 = '/var/py/volunclima/scripts/goes-16/Output/8/GALAPAGOS/'
  directorios=[directory,directory2,directory3]
  for indice,directory in enumerate(directorios):
    # Obtener la lista de nombres de archivo de las imágenes en el directorio y ordenarla
    image_files = sorted([os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.png')])

    # Crear una lista para almacenar las imágenes
    images = []

    # Leer las imágenes y agregarlas a la lista
    for filename in image_files:
        images.append(imageio.imread(filename))
    rangoi = (image_files[0][image_files[0].find("Band_8_"):image_files[0].find(" UTC")])
    rangof = (image_files[-1][image_files[-1].find("Band_8_"):image_files[-1].find(" UTC")])

    if(indice==0):
      # Especificar el nombre del archivo de salida del GIF
      output_file = directory+'band_8_'+rangoi+'_'+rangof+'_ecuador.gif'
    elif(indice==1):
      # Especificar el nombre del archivo de salida del GIF
      output_file = directory+'band_8_'+rangoi+'_'+rangof+'_guayaquil.gif'
    else:
      output_file = directory+'band_8_'+rangoi+'_'+rangof+'_galapagos.gif'
    frame_duration = 0.7
    # Guardar las imágenes como un GIF
    imageio.mimsave(output_file, images, duration=frame_duration)

    print(f"GIF creado con éxito: {output_file}")

descargar_archivo()