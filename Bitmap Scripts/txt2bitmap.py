# -*- coding: utf-8 -*-
"""
@author: Konrad Jarocki
"""
#making asc raster out of text file generated by Liyao 

import numpy as np
#import filters
def makearray(fn):
    data = np.genfromtxt(fn, skip_header=1,usecols = 2)
    header = np.genfromtxt(fn, max_rows=1)
    raster = data.reshape((int(header[0]),int(header[1])))
    print('size of pushed raster:', int(header[0]), int(header[1]))
    return raster,header

def rasterize(raster_array, filename, parameters):
    
    #Making header for asc file
    x_size = int(parameters[0])
    y_size = int(parameters[1])
    rows = "nrows " + str(x_size)+"\n"
    cols = "ncols " + str(y_size)+"\n"
    xll = 50
    yll = 50
    xll_str ="xllcorner "+ str(xll)+"\n" 
    yll_str ="yllcorner "+ str(yll)+"\n" 
    cellsize = "cellsize " + str(1)+"\n"
    text_file = open(filename,"w+")
    text_file.write(cols)
    text_file.write(rows)
    text_file.write(xll_str)
    text_file.write(yll_str)
    text_file.write(cellsize)
    text_file.write("nodata_value -9999\n")
    w=x_size
    h=y_size

    filt = raster_array
    fn2 = filename.split('.')[0]+'r.txt'
    np.savetxt(fn2,filt)
    for i in range(w):
        for j in range(h):
            
#            markers = worksheet.cell(i+1,j+1)       
#            d = markers.value
            d = filt[i][j]
            #saving to asc
            if j==x_size:
                text = str(d)+"\n"
                text_file.write(text)
            else:
                text=str(d)+" "
                text_file.write(text)
    print('done')
    return 

inputf = 'test2.txt'
outputf = 'test2.asc'
points,header = makearray(inputf)
#rasterize(points,outputf, header)
input_path = 'k122.txt'
#raster = filters.applygaussian(input_path, 0.5, 0.4 ,int(header[0]), int(header[1]))
#raster = filters.applymedian(input_path,7,int(header[0]), int(header[1]))
rasterize(points,outputf, header)
