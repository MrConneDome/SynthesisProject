"""
@author: Konrad Jarocki
#Scipt with different types of filters to apply on bitmap created from facade points.
"""

from scipy.ndimage import gaussian_filter
from scipy.signal import medfilt
import numpy as np

def applygaussian(fn, sigma):
    #applying gaussian filter with given sigma on the numpy table imported from text file
    
    raster = np.loadtxt(fn) 
    raster = raster.reshape((49,49))
    print(raster)
    raster_after = gaussian_filter(raster, sigma)
    print(raster_after)
    return raster_after

def applymedian(fn,kernel_size):
    #applying median filter with given kernel size on the numpy table imported from text file
    raster = np.loadtxt(fn) 
    raster = raster.reshape((49,49))
    print(raster)
    raster_after = medfilt(raster, kernel_size)
    print(raster_after)
    return raster_after
