import numpy as np, fiona
from fiona.crs import from_epsg
from shapely.geometry import Point, mapping

def pdal_cloud_to_shp(ins, outs):
    cloud_to_shp(ins)
    return True

def cloud_to_shp(ins):
    ids = ins['bag_id']
    points = np.stack((ins['X'], ins['Y']), axis=-1)
    
    points = np.split(points, len(points))
    shapely_points = []
    for point in points:
        shapely_points.append(Point(list(map(tuple, point))))
    
    shp_schema = {
        'geometry': 'Point',
        'properties': {'bag_id': 'int'},
    }
                     
    with fiona.open("output/bag_classified_points.shp", "w", crs=from_epsg(28992), driver="ESRI Shapefile", schema=shp_schema) as bag_shp:
        for i in range(len(points)):
            bag_shp.write({
                    "geometry":mapping(shapely_points[i]),
                    "properties": {"bag_id":ids[i]}
                    })