import numpy as np, xml.etree.ElementTree as ET, fiona, scipy.spatial
from owslib.wfs import WebFeatureService
from shapely.geometry import Polygon, mapping, Point, LineString
from fiona.crs import from_epsg

def retrieve_bag():
    # Connect to BAG WFS service and parse to ElementTree
    wfs11 = WebFeatureService("https://geodata.nationaalgeoregister.nl/bag/wfs?", version="1.1.0")
    
    wfs_response = wfs11.getfeature(typename="bag:pand", bbox=(93020, 436021, 94263, 436884))
    
    bag_parse = ET.parse(wfs_response)
    bag = bag_parse.getroot()
    
    
    bag_polygons = []
    eroded_polygons = []
    bag_ids = []
    
    # find all BAG panden
    for pand in bag.findall(".//{http://bag.geonovum.nl}pand"):
        
        # find all BAG ids
        for bag_id in pand.findall(".//{http://bag.geonovum.nl}identificatie"):
            bag_ids.append(bag_id.text)
            
        # find all BAG geometries    
        bag_polygon = []
        for geom in pand.findall(".//{http://www.opengis.net/gml}posList"):
            
            # place in array to remove z-coordinates (they are always 0) and format them for a Shapely polygon
            np_points = (np.array(geom.text.split())).astype(float)
            np_points = np_points[np_points != 0]
            np_points = np.split(np_points, len(np_points)/2)   
            bag_polygon.append(list(map(tuple, np_points)))     # some features have interiors, thus don't make a polygon yet!
        
        # in this case, the feature's geometry only has an exterior boundary
        if len(bag_polygon) == 1:   
            bag_polygons.append(Polygon(bag_polygon[0]))
            eroded_polygons.append(Polygon(bag_polygon[0]).buffer(-0.001, cap_style=3, join_style=2))
            
        # in this case, multiple geometries have been found for the feature, which means it has interior boundaries as well
        elif len(bag_polygon) > 1:
            bag_polygons.append(Polygon(bag_polygon[0], bag_polygon[1:]))
            eroded_polygons.append(Polygon(bag_polygon[0], bag_polygon[1:]).buffer(-0.001, cap_style=3, join_style=2))

    # create shapefiles, both for original BAG and buffered BAG
    shp_schema = {
        'geometry': 'Polygon',
        'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("bag_subset.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(bag_polygons)):
            bag_shp.write({
                    "geometry":mapping(bag_polygons[i]),
                    "properties": {"bag_id":bag_ids[i]}
                    })
    
    return eroded_polygons, bag_ids


def bag_id(ins,outs):
    points = np.stack((ins['X'], ins['Y']), axis=-1)
    
    polygons, ids = retrieve_bag()
        
    polygon_points = []
    polygon_points_ids = []
    polygon_lines_set = []
    
    # first, retrieve all the lines from the polygons
    for i, polygon in enumerate(polygons):
        x, y = polygon.exterior.coords.xy
        polygon_lines = []
        
        for c in range(len(x) - 1):
            polygon_lines.append(LineString((Point(x[c], y[c]), Point(x[c+1], y[c+1]))))    # create line with current and next point
            polygon_lines_set.append(LineString((Point(x[c], y[c]), Point(x[c+1], y[c+1]))))
        
        # then, create points on the lines
        for l in polygon_lines:
            line_length = l.length
            for j, distance in enumerate(range(10)):
                point = l.interpolate((line_length / 10) * distance )
                polygon_points.append((point.x, point.y))
                polygon_points_ids.append(ids[i])

    shapely_test_points = []
    for point in polygon_points:
        shapely_test_points.append(Point(point[0], point[1]))
        
    
    # create line and created points shapefiles for testing purposes
    shp_schema = {
        'geometry': 'LineString',
        'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("bag_lines.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(polygon_lines_set)):
            bag_shp.write({
                    "geometry":mapping(polygon_lines_set[i]),
                    "properties": {"bag_id":1}
                    })
        
    shp_schema = {
    'geometry': 'Point',
    'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("bag_line_points.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(polygon_points)):
            bag_shp.write({
                    "geometry":mapping(shapely_test_points[i]),
                    "properties": {"bag_id":polygon_points_ids[i]}
                    })
    
    # create kd-tree
    kdtree = scipy.spatial.cKDTree(polygon_points)   
    neigh_dist, neigh_i = kdtree.query(points, k=1)
    neigh_i = neigh_i.astype(np.uint16)     # for saving in point cloud dimension
    
    # we've just retrieved nearest neighbour indices, but we want the corresponding BAG-ids and put it in the .las
    neigh_bag_id = np.empty((0, 1))
    neigh_bag_id = np.append(neigh_bag_id, [ polygon_points_ids[i] for i in neigh_i ])
    
    outs['Intensity'] = neigh_i





    # write points + assigned BAG id to shapefile for testing purposes
    points = np.split(points, len(points))
    shapely_points = []
    for point in points:
        shapely_points.append(Point(list(map(tuple, point))))
    
    shp_schema = {
        'geometry': 'Point',
        'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("bag_classified_points.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(points)):
            bag_shp.write({
                    "geometry":mapping(shapely_points[i]),
                    "properties": {"bag_id":neigh_bag_id[i]}
                    })
      
        
    # PDAL requires this for a self-defined function    
    return True