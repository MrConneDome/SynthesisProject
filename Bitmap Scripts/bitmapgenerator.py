
"""
@author: Konrad Jarocki
#Generator for the raster from xls to asc raster file.
"""

import xlrd
import xlsxwriter
import numpy
import filters
def makeasc(filename, parameter):
    
    #Making header for asc file
    x_size = parameter[0]
    y_size = parameter[1]
    rows = "nrows " + str(parameter[0])+"\n"
    cols = "ncols " + str(parameter[1])+"\n"
    xll = 50
    yll = 50
    xll_str ="xllcorner "+ str(xll)+"\n" 
    yll_str ="yllcorner "+ str(yll)+"\n" 
    cellsize = "cellsize " + str(parameter[2])+"\n"
    text_file = open(filename,"w+")
    text_file.write(cols)
    text_file.write(rows)
    text_file.write(xll_str)
    text_file.write(yll_str)
    text_file.write(cellsize)
    text_file.write("nodata_value -9999\n")
    
    #Opening the xls file
    workbook = xlrd.open_workbook('C:/Users/konra/Documents/GitHub/Bitmap Example/bitmaptest.xls')
    worksheet = workbook.sheet_by_name('Arkusz1')

    w=x_size
    h=y_size
    filt = filters.applygaussian('C:/Users/konra/Documents/GitHub/Bitmap Example/testraster.txt',1,120)
    print(filt)
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
    return 

#Parameters for input to function
filename = 'raster_gaussian150.asc'
cellsize = 1
width = 49
height = 49

parameters = [ 0 for x in range(3)]
parameters[0] = width
parameters[1] = height
parameters[2] = cellsize
makeasc(filename, parameters)