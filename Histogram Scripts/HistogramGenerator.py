
"""
main part of the script for histogram generator. Saving the file to txt, using threshold.py and get_bb.py to automate the process.
@author: Konrad Jarocki
"""

# This scipt is producting numpy array that will be used to make the raster in the other one.
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import get_bb
import threshold

#Connect to postgresql database with postGIS extension installed
conn = psycopg2.connect("dbname=histogram user = postgres")
cur = conn.cursor()

#predefined size of the cell in [m]
cell_size = 500

#defining all the parameters of the grid
def define_grid(bb_box, cell_size):
    grid_par = [0 for x in range(4)]
    x_min = bb_box[0]
    x_max = bb_box[1]
    y_min = bb_box[2]
    y_max = bb_box[3]
    grid_width = abs(x_max-x_min)
    grid_height = abs(y_max-y_min)
    
    #number of cells in rows and columns
    cell_width = int(round(grid_width / cell_size,0) +1)
    cell_height = int(round(grid_height / cell_size,0) +1)
    
    print('number of cells width: ',cell_width, ' number of cells height: ',cell_height)
    
    grid_par[0] = grid_width
    grid_par[1] = grid_height
    grid_par[2] = cell_width
    grid_par[3] = cell_height
    
    return grid_par

    
def generate_histogram(grid_par, bb_box, cell_size):
    
    histogram = [[0 for x in range(grid_par[2])] for y in range(grid_par[3])] 
    
    #Iterating every cell in the grid
    for i in range(grid_par[2]): 
        for j in range(grid_par[3]): 
            
            #making boundaries for specific cell
            gx_min = bb_box[0] + cell_size*i
            gy_min = bb_box[2] + cell_size*j
            gx_max = bb_box[0] + cell_size*(i+1)
            gy_max = bb_box[2] + cell_size*(j+1)
            
            #query
            cur.execute("SELECT count(*) FROM point_cloud where x>={} and x<{} and y>={} and y<{};".format(gx_min,gx_max, gy_min, gy_max)) 
            
            for record in cur:
                print(i,j,record[0])
                
                #save the result to array
                histogram[j][i] = record[0]
    return histogram


bb_box = get_bb.getbb('histogram','postgres','point_cloud')
grid_par = define_grid(bb_box, cell_size)
histogram = generate_histogram(grid_par,bb_box,cell_size)

#plot of the results and save to file
f = np.array(histogram)  
np.savetxt('histogram_{}m.txt'.format(cell_size),f)           
plt.imshow(f, interpolation="nearest", origin="upper")
plt.colorbar()
plt.show()