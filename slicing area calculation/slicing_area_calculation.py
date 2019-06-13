# -*- coding: utf-8 -*-
"""
Created on Mon May 27 10:05:19 2019

@author: pante
"""

from shapely import geometry
from scipy.spatial import ConvexHull
import numpy as np
import matplotlib.pyplot as plt
import alphashape
from sklearn.cluster import DBSCAN


def PolygonArea(data):
    n = len(data) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += data[i][0] * data[j][1]
        area -= data[j][0] * data[i][1]
    area = abs(area) / 2.0
    return area


#Create a list of lists:
file = open("C:/Users/Jordi/Desktop/clean_output_2_10_100_100.txt")
lines = []
for line in file:
    # The rstrip method gets rid of the "\n" at the end of each line
    lines.append(line.rstrip().split(","))
file.close()
   
facade = []
windows = []
for line in lines:
    if line[2] == "1":
        facade.append([float(line[0]), float(line[1])])
    else:
        windows.append([float(line[0]), float(line[1])])
        
#Facade area calculation      
facade = np.array(facade)
alpha_facade = alphashape.alphashape(facade,alpha=2.0)
facade_surface = alpha_facade.area

windows = np.array(windows)


clustering = DBSCAN(eps=0.030, min_samples=10).fit(windows)

unique_labels = np.unique(clustering.labels_)

window_indices = []
for label in unique_labels:
    window = np.where(clustering.labels_==label)
    window_indices.append(window)

final_windows = []
alpha_shapes = []
window_surfaces = []
total_windows_surface = 0
for i, ind_window in enumerate(window_indices):
    if i == 0:
        continue
    final_window = windows[ind_window[0]]
    final_windows.append(final_window)
    alpha_shapes.append(alphashape.alphashape(final_window, alpha=2.0))
    
    #calculate surface of every window
    polygon_window = alphashape.alphashape(final_window, alpha=2.0)
    window_surfaces.append(polygon_window.area)
    print(polygon_window.area)
    total_windows_surface = total_windows_surface + polygon_window.area

with open("C:/Users/Jordi/Desktop/windows2.txt","w") as polygon:
    polygon.write("id|geom\n")
    polygon.write(str(i) + "|" + alpha_facade.wkt + "\n")
    for i, alpha_shape in enumerate(alpha_shapes, start=1):
        polygon.write(str(i) + "|" + alpha_shape.wkt + "\n")
    
        
        
file = open("windows_labeled.txt" , "w")
for i in range(len(lines)):
    if int(lines[i][2]) == 0:
        lines[i][2] = -1

for i in range(len(window_indices)):
    for index in window_indices[i][0]:
        lines[index][2] = i + 1
        
for line in lines:
    file.write(str(line[0]) + " " + str(line[1]) + "  " + str(line[2]) + "\n")
    
file.close()
