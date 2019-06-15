from owslib.wfs import WebFeatureService
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from shapely import ops
import numpy as np, pdal, json

# retrieve BAG features
wfs11 = WebFeatureService("https://geodata.nationaalgeoregister.nl/bag/wfs?", version="1.1.0")

wfs_response = wfs11.getfeature(typename="bag:pand", bbox=(93020, 436021, 94263, 436884))

bag_parse = ET.parse(wfs_response)
bag = bag_parse.getroot()

# parse BAG features into a list
bag_polygons = []
for geom in bag.iter("{http://www.opengis.net/gml}posList"):
    bag_polygon = []

    np_points = (np.array(geom.text.split())).astype(float)

    np_points = np_points[np_points != 0]
    
    np_points = np.split(np_points, len(np_points)/2)
    
    # append BUFFERED features
    bag_polygons.append(Polygon(list(map(tuple, np_points))).buffer(4.8, cap_style=3))

# now unify them. because buffers are unified, some small holes between facades are closed, creating close polygons.
# there are no scans done in there, so by having closed polygons, these inside parts can be removed
bag_polygons = ops.unary_union(bag_polygons)
unified_polygons = []

# now create negative distance buffers
for polygon in bag_polygons:
    unified_polygon = Polygon(polygon.exterior).buffer(-6, cap_style=3)
    if unified_polygon != 'POLYGON EMPTY':
        unified_polygons.append(unified_polygon)

# and remove these polygons from the positive distance buffers, so that only parts around facade boundaries are left
unified_polygons_difference = bag_polygons.difference(ops.unary_union(unified_polygons))


# crop the cloud by the created polygons
json = """
{
    "pipeline":
    [
        "MLS_pmf_and_bag_filtered.las",
        {
            "type":"filters.crop",
            "polygon":%s
        },
        {
            "type":"writers.las",
            "filename":"MLS_pmf_and_bag_inside_filtered.las"
        }
    ]
}
""" %json.dumps(unified_polygons_difference.wkt)

pipeline = pdal.Pipeline(json)
pipeline.validate() # check if our JSON and options were good
pipeline.loglevel = 8 #really noisy
count = pipeline.execute()
arrays = pipeline.arrays
metadata = pipeline.metadata
log = pipeline.log
