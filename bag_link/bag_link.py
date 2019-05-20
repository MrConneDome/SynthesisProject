import numpy as np, scipy.spatial, xml.etree.ElementTree as ET, fiona
from shapely.geometry import Point, LineString, Polygon, mapping
from owslib.wfs import WebFeatureService
from fiona.crs import from_epsg
from rtree import index

def retrieve_bag():
    # Connect to BAG WFS service and parse to ElementTree
    wfs11 = WebFeatureService("https://geodata.nationaalgeoregister.nl/bag/wfs?", version="1.1.0")
    
    wfs_response = wfs11.getfeature(typename="bag:pand", bbox=(93020, 436021, 94263, 436884))
    
    bag_parse = ET.parse(wfs_response)
    bag = bag_parse.getroot()
    
    
    bag_polygons = []
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
            
        # in this case, multiple geometries have been found for the feature, which means it has interior boundaries as well
        elif len(bag_polygon) > 1:
            bag_polygons.append(Polygon(bag_polygon[0], bag_polygon[1:]))
    
    return bag_polygons, bag_ids

# creates a shapefile with the BAG-features
def create_bag_shp(ins, outs):
    bag_polygons, bag_ids = retrieve_bag()
    
    shp_schema = {
        'geometry': 'Polygon',
        'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("output/bag_subset.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(bag_polygons)):
            bag_shp.write({
                    "geometry":mapping(bag_polygons[i]),
                    "properties": {"bag_id":bag_ids[i]}
                    })
    return True

def bag_id(ins,outs):
    bag_polygons, bag_ids = retrieve_bag()
    
    # slightly erode BAG polygons
    polygons = []
    for polygon in bag_polygons:
        polygons.append(polygon.buffer(-0.001, cap_style=3, join_style=2))
    
    # arrange the points from the point cloud
    points = np.stack((ins['X'], ins['Y']), axis=-1)
    
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
            for distance in range(int(l.length / 0.5)):
                point = l.interpolate(0.5 * distance )
                polygon_points.append((point.x, point.y))
                polygon_points_ids.append(bag_ids[i])

    # the commented part below writes shapefiles for debugging purposes
    """
    shapely_test_points = []
    for point in polygon_points:
        shapely_test_points.append(Point(point[0], point[1]))
        
    # create line and created points shapefiles for testing purposes
    shp_schema = {
        'geometry': 'LineString',
        'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("output/bag_lines.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(polygon_lines_set)):
            bag_shp.write({
                    "geometry":mapping(polygon_lines_set[i]),
                    "properties": {"bag_id":1}
                    })
        
    shp_schema = {
    'geometry': 'Point',
    'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("output/bag_line_points.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(polygon_points)):
            bag_shp.write({
                    "geometry":mapping(shapely_test_points[i]),
                    "properties": {"bag_id":polygon_points_ids[i]}
                    })
    """
    
    # create kd-tree
    kdtree = scipy.spatial.cKDTree(polygon_points)   
    neigh_dist, neigh_i = kdtree.query(points, k=1)

    # we've just retrieved nearest neighbour indices, but we want the corresponding BAG-ids and put it in the .las
    neigh_bag_id = np.empty((0, 1))
    neigh_bag_id = np.append(neigh_bag_id, [ polygon_points_ids[i] for i in neigh_i ])


    # now, we need to change the BAG-id for points that actually intersect a BAG-feature, using rtree
    rtree = build_rtree(bag_polygons)
    func = get_intersection_func(rtree)
    
    # check for every point with which polygon it intersects
    for i, point in enumerate(points):
        my_intersections = func(point)
        if(len(my_intersections) > 0):  # because if len = 0, there is no intersection            
            neigh_bag_id[i] = bag_ids[my_intersections[0].id]   # assign BAG-id


    # time to update the point cloud with the BAG-ids
    neigh_bag_id = neigh_bag_id.astype(np.dtype('Float64'))     # a new dimension added (in the PDAL pipeline) always is of type float64
    
    outs['bag_id'] = neigh_bag_id       # update bag_id dimension in point cloud
           
    return True   # PDAL requires this for a self-defined function 
    

# the next three functions are for the rtree. mostly copied from https://stackoverflow.com/questions/53224490/how-can-i-look-up-a-polygon-that-contains-a-point-fast-given-all-polygons-are-a
def get_containing_box(p):
    # this function is needed because the rtree only takes boxes, and not polygons
    xcoords = [x for x, _ in p.exterior.coords]
    ycoords = [y for _, y in p.exterior.coords]
    box = (min(xcoords), min(ycoords), max(xcoords), max(ycoords))   
    return box

def build_rtree(polys):
    def generate_items():
        pindx = 0
        for pol in polys:
            box = get_containing_box(pol)
            yield (pindx, box,  pol)
            pindx += 1
    return index.Index(generate_items())

def get_intersection_func(rtree_index):
    def intersection_func(point):
        pbox = (point[0], point[1], 
                 point[0], point[1])
        hits = rtree_index.intersection(pbox, objects=True)
        # Filter false positives:
        result = [pol for pol in hits if (pol.object).intersects(Point(point)) ]
        return result
    return intersection_func
