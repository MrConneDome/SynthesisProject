import numpy as np
import alphashape  #https://pypi.org/project/alphashape/    a=0 --> convex hull , a=2 --> concave hull, If you go too high on the alpha parameter, you will start to lose points from the original data set.
from sklearn.cluster import DBSCAN   #https://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html#sphx-glr-auto-examples-cluster-plot-dbscan-py
from shapely.geometry import Point, LineString, mapping
import scipy.spatial
import fiona
from fiona.crs import from_epsg

#Read the txt file in a list of lists
file_name = ""
input_path = "facade5.txt"
output_path = ""
file = open(input_path)
t_matrix = []
lines = []
for i, line in enumerate(file):
    # The rstrip method gets rid of the "\n" at the end of each line
    if i < 5:
        t_matrix.append(line.rstrip().split())
    else:
        lines.append(line.rstrip().split())
file.close()


# Distinguish window and facade points
facade = []
windows = []
for line in lines:
    if line[2] == "0":
        windows.append([float(line[0]), float(line[1])])
    else:
        facade.append([float(line[0]), float(line[1])])


#Facade area calculation
facade = np.array(facade)
alpha_facade = alphashape.alphashape(facade, alpha=2.0)
facade_surface = alpha_facade.area

#Clustering of windows
windows = np.array(windows)
clustering = DBSCAN(eps=0.055, min_samples=40).fit(windows)
unique_labels = np.unique(clustering.labels_)




#Collect indices of each individual window according to the clustering
window_indices = []
for label in unique_labels:
    window = np.where(clustering.labels_ == label)
    window_indices.append(window)

# create points on facade alpha shape
alpha_facade_points = []
x, y = alpha_facade.exterior.coords.xy
polygon_lines = []
for c in range(len(x) - 1):
    polygon_lines.append(LineString((Point(x[c], y[c]), Point(x[c+1], y[c+1]))))    # create line with current and next point

for l in polygon_lines:
    for distance in range(int(l.length * 1000)):
        point = l.interpolate(((l.length / (int(l.length * 1000))) * distance))
        alpha_facade_points.append((point.x, point.y))

#collect final windows from indices
kdtree = scipy.spatial.cKDTree(alpha_facade_points)
window_facade_threshold = 0.000
windows_distance_threshold = 0.000
final_windows = []
alpha_shapes = []
window_surfaces = []
total_windows_surface = 0
for i, ind_window in enumerate(window_indices):
    if i == 0:
        continue
    final_window = windows[ind_window[0]]
    
    neigh_dist, neigh_i = kdtree.query(final_window, k=1)

    if min(neigh_dist) < window_facade_threshold:             # if the window is too close to the facade, do not add it
        continue
    #elif (alphashape.alphashape(final_window, alpha=3.5)).area < 0.000:
    #    continue
    else:        
        combined_windows_indices = []
        deprecated_windows_indices = []
        polygon_window = alphashape.alphashape(final_window, alpha=3.5)
        
        # merge clusters based on the distances between their alpha shapes
        if(len(alpha_shapes) > 0):
            for j, window in enumerate(alpha_shapes):
                if polygon_window.distance(window) < windows_distance_threshold:
                    #if polygon_window.area < 0.010 and window.area < 0.010:
                    final_window = np.concatenate((final_window, final_windows[j]))
                    polygon_window = alphashape.alphashape(final_window, alpha=3.5)
                    deprecated_windows_indices.append(j)
                    
                    
                    
        final_windows.append(final_window)
        alpha_shapes.append(polygon_window)
        
        for i in sorted(deprecated_windows_indices, reverse=True):
            del final_windows[i]
            del alpha_shapes[i]
        
        # calculate surface of every window
        window_surfaces.append(polygon_window.area)
        #print("Current polygon area: ", polygon_window.area)
        total_windows_surface = total_windows_surface + polygon_window.area
        #print ("Total windows area: ",total_windows_surface)



#write the output WKT file
with open("alpha_shapes_test.txt", "w") as polygon:
    polygon.write("id|geom\n")
    polygon.write("0" + "|" + alpha_facade.wkt + "\n")
    for i, alpha_shape in enumerate(alpha_shapes, start=1):
        polygon.write(str(i) + "|" + alpha_shape.wkt + "|" +  "\n")


with open("clusters.txt","w") as clustered:
    count = 0
    clustered.write("id|geom\n")
    for label in unique_labels:
        if label == -1: 
            continue
        window = np.where(clustering.labels_==label)
        for index in window[0]:
            point_shapely = Point(windows[index][0],windows[index][1])
            clustered.write("1" + "|" + str(point_shapely) + "|" + str(count) + "\n")
        count +=1        
        
ratio = total_windows_surface / facade_surface
with open("windows_labeled_test.txt" , "w") as labeled_points:
    for line in t_matrix:
        labeled_points.write(' '.join(line) + "\n") 
    
    for facade_point in facade:
        labeled_points.write(str(facade_point[0]) + " " + str(facade_point[1]) + " " + "1" + " " + str(ratio) + "\n")
    
    for i, window in enumerate(final_windows):
        for window_point in window:
            labeled_points.write(str(window_point[0]) + " " + str(window_point[1]) + " " + str(i+2) + " " + str(ratio) + "\n")

        """
file = open("windows_labeled_test.txt" , "w")
for i in range(len(lines)):
    if int(lines[i][2]) == 0:
        lines[i][2] = -1

for i in range(len(window_indices)):
    for index in window_indices[i][0]:
        lines[index][2] = i + 2

for line in lines:
    file.write(str(line[0]) + " " + str(line[1]) + "  " + str(line[2]) + "\n")
    
    
file.close()
"""