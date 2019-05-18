import numpy as np, xml.etree.ElementTree as ET, fiona
from owslib.wfs import WebFeatureService
from shapely.geometry import Polygon, mapping, shape
from fiona.crs import from_epsg

def retrieve_bag():
    # Connect to BAG WFS service and parse to ElementTree
    wfs11 = WebFeatureService("https://geodata.nationaalgeoregister.nl/bag/wfs?", version="1.1.0")
    
    wfs_response = wfs11.getfeature(typename="bag:pand", bbox=(93020, 436021, 94263, 436884))
    
    bag_parse = ET.parse(wfs_response)
    bag = bag_parse.getroot()
    
    
    bag_polygons = []
    bag_polygons_buffered = []
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
            bag_polygons_buffered.append(Polygon(bag_polygon[0]).buffer(1, cap_style=3, join_style=2))
        # in this case, multiple geometries have been found for the feature, which means it has interior boundaries as well
        elif len(bag_polygon) > 1:
            bag_polygons.append(Polygon(bag_polygon[0], bag_polygon[1:]))
            bag_polygons_buffered.append(Polygon(bag_polygon[0], bag_polygon[1:]).buffer(1, cap_style=3, join_style=2))
            
    
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
        
    with fiona.open("bag_buffered_subset.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(bag_polygons)):
            bag_shp.write({
                    "geometry":mapping(bag_polygons_buffered[i]),
                    "properties": {"bag_id":bag_ids[i]}
                    })
    
    return bag_polygons
