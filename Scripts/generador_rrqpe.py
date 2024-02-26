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
import datetime # Library to convert julian day to dd-mm-yyyy
 
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from osgeo import gdal # Add the GDAL library
#======================================================================================================

def generar_png_RRQPE():
    # Load the Data =======================================================================================
    # Path to the GOES-16 image file
    path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/RRQPE/'
    paths = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.nc')]

    # Choose the visualization extent (min lon, min lat, max lon, max lat)
    extent = [-81.1, -5.25, -75.1,  1.5] #ecuador
    extent2 = [-80.105, -2.305, -79.855,  -2.01] #guayaquil
    extent3 = [-91.73, -1.51, -89.17,  0.69] #galapagos
    lista_extent=[extent,extent2,extent3]
    #extent = [-120, -60, -30,  30]
    # Choose the image resolution (the higher the number the faster the processing is)
    resolution = 2.0
    paises=[]
    # Call the reprojection funcion
    paises.append(remap(paths, extent, resolution, 'HDF5'))
    paises.append(remap(paths, extent2, resolution, 'HDF5'))
    paises.append(remap(paths, extent3, resolution, 'HDF5'))
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
        # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
        bmap.imshow(np.ma.masked_where(mask, data), origin='upper', cmap=custom_cmap)

        #bmap.imshow(data, origin='upper', cmap=custom_cmap)
        # Insert the colorbar at the bottom
        cb = bmap.colorbar(location='bottom', size = '2%', pad = '-3.49%')
        cb.outline.set_visible(False) # Remove the colorbar outline
        cb.ax.tick_params(width = 1,direction= 'in') # Remove the colorbar ticks
        cb.ax.xaxis.set_tick_params(pad=-12.5) # Put the colobar labels inside the colorbar
        cb.ax.tick_params(axis='x', colors='white', labelsize=8, width=1) # Change the color and size of the colorbar labels
        #cb.ax.invert_xaxis()

        # Define los límites del colorbar y los ticks
        if (max_val<400):
            tick_interval = 5
            cb.set_ticks(range(int(min_val)+5, int(max_val) + 1, tick_interval))
        else:
            tick_interval = 100
            cb.set_ticks(range(int(min_val)+50, int(max_val) + 1, tick_interval))
        path=paths[0]
        # Search for the Scan start in the file name
        Start = (path[path.find("_s")+2:path.find("_e")])
        # Search for the GOES-16 channel in the file name
        #Band = (path[path.find("M6C")+3:path.find("_G16")])
        # Create a GOES-16 Bands string array
        Wavelenghts = ['[]','[0.47 μm]','[0.64 μm]','[0.865 μm]','[1.378 μm]','[1.61 μm]','[2.25 μm]','[3.90 μm]','[6.19 μm]','[6.95 μm]','[7.34 μm]','[8.50 μm]','[9.61 μm]','[10.35 μm]','[11.20 μm]','[12.30 μm]','[13.30 μm]']
        
        # Converting from julian day to dd-mm-yyyy
        year = int(Start[0:4])
        dayjulian = int(Start[4:7]) - 1 # Subtract 1 because the year starts at "0"
        dayconventional = datetime.datetime(year,1,1) + datetime.timedelta(dayjulian) # Convert from julian to conventional
        date = dayconventional.strftime('%d-%b-%Y') # Format the date according to the strftime directives
        
        #time = Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + " UTC" # Time of the Start of the Scan
        
        Unit = "millimeters per hour [mm/h]"
        Title = " GOES-16 ABI RRQPE Daily Precipitation estimation " + Unit + " " + date 
        Institution = "CIIFEN "
        
        # Add a black rectangle in the bottom to insert the image description
        lon_difference = (extent[2] - extent[0]) # Max Lon - Min Lon
        currentAxis = plt.gca()
        currentAxis.add_patch(Rectangle((extent[0], extent[1]), lon_difference, lon_difference * 0.017, alpha=1, zorder=3, facecolor='black'))
        
        # Add the image description inside the black rectangle
        lat_difference = (extent[3] - extent[1]) # Max lat - Min lat
        plt.text(extent[0], extent[1] + lat_difference * 0.003,Title,horizontalalignment='left', color = 'white', size=10)
        plt.text(extent[2], extent[1],Institution, horizontalalignment='right', color = 'white', size=10)
        
        # Add logos / images to the plot
        logo_GNC = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GNC Logo.png')
        logo_INPE = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/INPE Logo.png')
        logo_NOAA = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/NOAA Logo.png')
        logo_GOES = plt.imread('/var/py/volunclima/scripts/goes-16/Logos/GOES Logo.png')
        """ ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper') """
        """ ax.figimage(logo_GNC, 700, 58, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_INPE, 1100, 58, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_NOAA, 1200, 58, zorder=3, alpha = 1, origin = 'upper')
        ax.figimage(logo_GOES, 1285, 58, zorder=3, alpha = 1, origin = 'upper') """
        # Save the result
        if(indice ==0):
            ax.figimage(logo_GNC, 700, 58, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, 1100, 58, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, 1200, 58, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, 1285, 58, zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/RRQPE/rrqpe_estimation_'+date+'_ECUADOR.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        elif(indice ==1):
            ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/RRQPE/rrqpe_estimation_'+date+'_GUAYAQUIL.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        else:
            ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/RRQPE/rrqpe_estimation_'+date+'_GALAPAGOS.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        
        plt.close(ax)
        # Export the result to GeoTIFF
        """ driver = gdal.GetDriverByName('GTiff')
        driver.CreateCopy('E:\\VLAB\\Python\\Output\\Channel_13.tif', grid, 0) """
        #======================================================================================================

generar_png_RRQPE()