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
 
import datetime # Library to convert julian day to dd-mm-yyyy
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from osgeo import gdal # Add the GDAL library
#======================================================================================================
 

def generar_png_LST():
    # Load the Data =======================================================================================
    # Path to the GOES-16 image file
    path = '/var/py/volunclima/scripts/goes-16/GOES-16 Samples/LST/'
    paths = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.nc')]
    

    # Choose the visualization extent (min lon, min lat, max lon, max lat)
    extent = [-81.1, -5.25, -75.1,  1.5] #ecuador
    extent2 = [-80.105, -2.305, -79.855,  -2.01] #guayaquil
    extent3 = [-91.73, -1.51, -89.17,  0.69] #galapagos
    #extent = [-120, -60, -30,  30]
    lista_extent=[extent,extent2,extent3]

    # Choose the image resolution (the higher the number the faster the processing is)
    resolution = 2.0
    paises=[]
    # Call the reprojection funcion
    paises.append(remap(paths, extent, resolution, 'HDF5'))
    paises.append(remap(paths, extent2, resolution, 'HDF5'))
    paises.append(remap(paths, extent3, resolution, 'HDF5'))
    for indice,pais in enumerate(paises):
        extent=lista_extent[indice]
        # Read the data returned by the function and convert it to Celsius
        data = pais.ReadAsArray() -273.15

        # Suponiendo que 'data' es tu matriz anidada
        data_flat = data.flatten()  # Aplanar la matriz para obtener una lista plana de elementos
        unique_values, counts = np.unique(data_flat, return_counts=True)  # Obtener valores únicos y sus frecuencias
        max_val=np.max(data_flat)
        min_val=np.min(data_flat)
        # Encontrar el índice del valor más repetido
        most_common_index = np.argmax(counts)

        # Obtener el valor más repetido y su frecuencia
        most_common_value = float('-inf')
        #most_common_value = unique_values[most_common_index]


        #print("Valor más repetido:", most_common_value)
        #print("Frecuencia:", most_common_count)
        #======================================================================================================
        # Converts a CPT file to be used in Python
        cpt = loadCPT('/var/py/volunclima/scripts/goes-16/Colortables/temperature.cpt')
        # Makes a linear interpolation
        cpt_convert = LinearSegmentedColormap('cpt', cpt)




        # Crea una máscara para el rango de datos
        mask = (data >= most_common_value-0.01) & (data <= most_common_value+0.01)
        # Crea una máscara para el valor más repetido


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

        

        # Crea el mapa de colores segmentado linealmente
        cmap = plt.get_cmap('jet')  # Can be any colormap that you want after the cm
        cmap.set_bad(color='grey')
        # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
        bmap.imshow(np.ma.masked_where(mask, data), origin='upper', cmap=cmap,vmin=-20,vmax=50)
        # Overlay the mask with black color
        #bmap.imshow(np.ma.masked_where(~mask, data), cmap='Greys', alpha=1, origin='upper')

        # Insert the colorbar at the bottom
        cb = bmap.colorbar(location='bottom', size = '2%', pad = '-3.49%')
        cb.outline.set_visible(False) # Remove the colorbar outline
        cb.ax.tick_params(width = 1,direction= 'in') # Remove the colorbar ticks
        cb.ax.xaxis.set_tick_params(pad=-12.5) # Put the colobar labels inside the colorbar
        cb.ax.tick_params(axis='x', colors='black', labelsize=8, width=1) # Change the color and size of the colorbar labels

        # Define los límites del colorbar y los ticks
        tick_interval = 5
        cb.set_ticks(range(-5, 45 + 1, tick_interval))
        path=paths[0]
        # Search for the Scan start in the file name
        Start = (path[path.find("_s")+2:path.find("_e")])
        # Search for the GOES-16 channel in the file name
        Band = (path[path.find("M6C")+3:path.find("_G16")])
        # Create a GOES-16 Bands string array
        
        # Converting from julian day to dd-mm-yyyy
        year = int(Start[0:4])
        dayjulian = int(Start[4:7]) - 1 # Subtract 1 because the year starts at "0"
        dayconventional = datetime.datetime(year,1,1) + datetime.timedelta(dayjulian) # Convert from julian to conventional
        date = dayconventional.strftime('%d-%b-%Y') # Format the date according to the strftime directives
        
        time = Start [7:9] + ":" + Start [9:11] + ":" + Start [11:13] + " UTC" # Time of the Start of the Scan
        
        Unit = " [°C]"
        Title = " GOES-16 ABI LST Daily Max. Temperature estimation " + Unit + " " + date
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
        
        # Save the result
        if(indice ==0):
            ax.figimage(logo_GNC, 700, 58, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, 1100, 58, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, 1200, 58, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, 1285, 58, zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/LST/LST_estimation_'+date+'_ECUADOR.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        elif(indice ==1):
            ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/LST/LST_estimation_'+date+'_GUAYAQUIL.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        else:
            ax.figimage(logo_GNC, 10, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_INPE, 400, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_NOAA, 500, 55, zorder=3, alpha = 1, origin = 'upper')
            ax.figimage(logo_GOES, 585, 55, zorder=3, alpha = 1, origin = 'upper')
            plt.savefig('/var/py/volunclima/scripts/goes-16/Output/LST/LST_estimation_'+date+'_GALAPAGOS.png', dpi=DPI, bbox_inches='tight', pad_inches=0)
        plt.close(ax)
        # Export the result to GeoTIFF
        """ driver = gdal.GetDriverByName('GTiff')
        driver.CreateCopy('E:\\VLAB\\Python\\Output\\Channel_13.tif', grid, 0) """
        #======================================================================================================

generar_png_LST()