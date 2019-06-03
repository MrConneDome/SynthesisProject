from owslib.wfs import WebFeatureService
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from shapely import ops
import numpy as np, pdal, json
import shapely.wkt

# retrieve BAG features
wfs11 = WebFeatureService("https://geodata.nationaalgeoregister.nl/bag/wfs?", version="1.1.0")

wfs_response = wfs11.getfeature(typename="bag:pand", bbox=(93020, 436021, 94263, 436884))

bag_parse = ET.parse(wfs_response)
bag = bag_parse.getroot()

# parse BAG features into a list
bag_polygons = []
for geom in bag.iter("{http://www.opengis.net/gml}posList"):
    np_points = (np.array(geom.text.split())).astype(float)

    np_points = np_points[np_points != 0]
    
    np_points = np.split(np_points, len(np_points)/2)
    
    bag_polygon = Polygon(list(map(tuple, np_points)))
    
    bag_polygons.append(bag_polygon)

# for removing some BAG-features that we don't want
manual_bag_polygons = [shapely.wkt.loads("Polygon ((93906.07000000000698492 436824.16999999998370185, 93909.83000000000174623 436825.57000000000698492, 93910.96000000000640284 436822.53999999997904524, 93907.19999999999708962 436821.14000000001396984, 93906.07000000000698492 436824.16999999998370185))"),
                   shapely.wkt.loads("Polygon ((93771.34500000000116415 436774.28299999999580905, 93756.13499999999476131 436763.23200000001816079, 93752.30199999999604188 436768.50799999997252598, 93767.51200000000244472 436779.55699999997159466, 93771.34500000000116415 436774.28299999999580905))"),
                   shapely.wkt.loads("Polygon ((93792.85000000000582077 436744.68599999998696148, 93803.6190000000060536 436729.86499999999068677, 93788.32099999999627471 436718.92999999999301508, 93777.63300000000162981 436733.64199999999254942, 93792.85000000000582077 436744.68599999998696148))"),
                   shapely.wkt.loads("Polygon ((93604.28999999999359716 436622.40999999997438863, 93604.41000000000349246 436622.51000000000931323, 93603.08000000000174623 436624.02000000001862645, 93603.57000000000698492 436624.45000000001164153, 93602.97999999999592546 436625.10999999998603016, 93604.80000000000291038 436626.72999999998137355, 93605.43499999999767169 436626.00500000000465661, 93606.96199999999953434 436624.26199999998789281, 93608.55000000000291038 436622.45000000001164153, 93608.62900000000081491 436622.356000000028871, 93608.69800000000395812 436622.25400000001536682, 93608.7559999999939464 436622.14699999999720603, 93608.80400000000372529 436622.03399999998509884, 93608.84100000000034925 436621.91700000001583248, 93608.86599999999452848 436621.7970000000204891, 93608.87900000000081491 436621.67499999998835847, 93608.8809999999939464 436621.55200000002514571, 93608.86999999999534339 436621.42999999999301508, 93608.7480000000068685 436621.42399999999906868, 93608.62600000000384171 436621.43300000001909211, 93608.5059999999939464 436621.45699999999487773, 93608.38999999999941792 436621.4940000000060536, 93608.27899999999499414 436621.54599999997299165, 93608.17600000000675209 436621.60999999998603016, 93608.08000000000174623 436621.68599999998696148, 93607.99499999999534339 436621.77299999998649582, 93607.91999999999825377 436621.86999999999534339, 93607.74499999999534339 436621.71000000002095476, 93607.55400000000372529 436621.57000000000698492, 93607.34900000000197906 436621.45000000001164153, 93607.13300000000162981 436621.35200000001350418, 93606.90799999999580905 436621.27700000000186265, 93606.67699999999604188 436621.22600000002421439, 93606.44100000000617001 436621.19900000002235174, 93606.20399999999790452 436621.1969999999855645, 93605.96799999999348074 436621.21999999997206032, 93605.73600000000442378 436621.26699999999254942, 93605.50900000000547152 436621.33799999998882413, 93605.29200000000128057 436621.43199999997159466, 93605.08500000000640284 436621.54800000000977889, 93604.89200000000710133 436621.68499999999767169, 93604.71400000000721775 436621.84200000000419095, 93604.55299999999988358 436622.01600000000325963, 93604.41099999999278225 436622.20600000000558794, 93604.28999999999359716 436622.40999999997438863))"),
                   shapely.wkt.loads("Polygon ((93624.10000000000582077 436645.92999999999301508, 93624.86999999999534339 436646.59999999997671694, 93625.30000000000291038 436646.09999999997671694, 93625.78999999999359716 436646.53000000002793968, 93627.27000000000407454 436644.84000000002561137, 93627.38999999999941792 436644.94000000000232831, 93627.55499999999301508 436644.78000000002793968, 93627.70399999999790452 436644.60499999998137355, 93627.83599999999569263 436644.41800000000512227, 93627.95100000000093132 436644.21899999998277053, 93628.04700000000593718 436644.01000000000931323, 93628.12399999999615829 436643.79399999999441206, 93628.17999999999301508 436643.57099999999627471, 93628.21600000000034925 436643.34399999998277053, 93628.23099999999976717 436643.11499999999068677, 93628.22500000000582077 436642.88599999999860302, 93628.19800000000395812 436642.65799999999580905, 93628.14999999999417923 436642.43300000001909211, 93628.08100000000558794 436642.21399999997811392, 93627.99300000000221189 436642.00199999997857958, 93627.88599999999860302 436641.79899999999906868, 93627.76099999999860302 436641.606000000028871, 93627.61800000000221189 436641.42599999997764826, 93627.46000000000640284 436641.26000000000931323, 93627.53100000000267755 436641.16499999997904524, 93627.59299999999348074 436641.06300000002374873, 93627.64599999999336433 436640.95699999999487773, 93627.6889999999984866 436640.84600000001955777, 93627.72299999999813735 436640.73200000001816079, 93627.74499999999534339 436640.61599999997997656, 93627.75699999999778811 436640.49699999997392297, 93627.75900000000547152 436640.37900000001536682, 93627.75 436640.26000000000931323, 93627.69899999999324791 436640.26099999999860302, 93627.64699999999720603 436640.26400000002468005, 93627.59600000000500586 436640.27000000001862645, 93627.54600000000209548 436640.27799999999115244, 93627.49499999999534339 436640.28800000000046566, 93627.44599999999627471 436640.29999999998835847, 93627.39599999999336433 436640.31500000000232831, 93627.34799999999813735 436640.33100000000558794, 93627.30000000000291038 436640.34999999997671694, 93627.2470000000030268 436640.37400000001071021, 93627.19599999999627471 436640.40000000002328306, 93627.14599999999336433 436640.42900000000372529, 93627.09699999999429565 436640.46000000002095476, 93627.05000000000291038 436640.49300000001676381, 93627.00400000000081491 436640.52899999998044223, 93626.96099999999569263 436640.56800000002840534, 93626.91899999999441206 436640.60800000000745058, 93626.88000000000465661 436640.65000000002328306, 93625.31799999999930151 436642.43699999997625127, 93623.77800000000570435 436644.19799999997485429, 93623.05999999999767169 436645.02000000001862645, 93624.10000000000582077 436645.92999999999301508))"),
                   shapely.wkt.loads("Polygon ((93765 436361, 93765 436455, 93863 436455, 93863 436361, 93765 436361))"),
                   shapely.wkt.loads("Polygon ((93795 436230, 93795 436351, 93921 436351, 93921 436230, 93795 436230))"),
                   shapely.wkt.loads("Polygon ((93550.08900000000721775 436448.106000000028871, 93551.78399999999965075 436446.30200000002514571, 93547.32399999999324791 436442.1120000000228174, 93545.63899999999557622 436443.95400000002700835, 93550.08900000000721775 436448.106000000028871))"),
                   shapely.wkt.loads("Polygon ((93492.74599999999918509 436377.93599999998696148, 93494.11400000000139698 436379.106000000028871, 93495.3080000000045402 436377.71000000002095476, 93493.94000000000232831 436376.53999999997904524, 93492.74599999999918509 436377.93599999998696148))"),
                   shapely.wkt.loads("Polygon ((93472.72000000000116415 436376.19000000000232831, 93476.22999999999592546 436379.26000000000931323, 93478.52000000000407454 436376.64000000001396984, 93475 436373.57000000000698492, 93472.72000000000116415 436376.19000000000232831))"),
                   shapely.wkt.loads("Polygon ((93396.39999999999417923 436259.65000000002328306, 93396.27899999999499414 436259.48800000001210719, 93395.11000000000058208 436257.91999999998370185, 93392.80000000000291038 436259.64000000001396984, 93394.08999999999650754 436261.36999999999534339, 93396.39999999999417923 436259.65000000002328306))")                   
                   ]

# for removing other artefacts
manual_other_polygons = [shapely.wkt.loads("POLYGON ((93655.320313 436559.75, 93654.617188 436560.75, 93571.359375 436481.25, 93568.539063 436478.156250, 93655.320313 436559.75))"),
                         shapely.wkt.loads("POLYGON ((93923.23 436705.93, 93923.23 436741.5, 93954.78999999999 436741.5, 93954.78999999999 436741.18, 93946.78999999999 436741.18, 93946.78999999999 436732.37, 93954.78999999999 436732.37, 93954.78999999999 436693.44, 93934.95 436693.44, 93934.95 436705.93, 93923.23 436705.93))")]

# remove the unwanted parts that we have just defined from the original BAG
manual_bag_polygons = ops.unary_union(manual_bag_polygons)
manual_other_polygons = ops.unary_union(manual_other_polygons)
bag_polygons = ops.unary_union(bag_polygons)
bag_polygons = bag_polygons.difference(manual_bag_polygons)
bag_polygons = bag_polygons.buffer(1.8, cap_style=3)
bag_polygons = bag_polygons.difference(manual_other_polygons).wkt


# the filtering steps that are described in the report
json = """
{
    "pipeline":
    [
        "C:/Users/Jordi/Desktop/bag_test_full2.las",
        {
            "type":"filters.reprojection",
            "out_srs":"EPSG:28992"
        },
         {
          "type":"filters.assign",
          "assignment" : "NumberOfReturns[0:0]=1"
        },  
        {
            "type":"filters.pmf"
        },
        {
            "type":"filters.hag"
        },
        {
            "type":"filters.range",
            "limits":"HeightAboveGround[0.2:]"
        },
        {
            "type":"filters.crop",
            "polygon":%s
        },
        {
            "type":"writers.las",
            "filename":"bag_test_full3.las",
            "extra_dims":"all"
        }
    ]
}
""" %json.dumps(bag_polygons)

# PDAL performing the steps of the above defined pipeline
pipeline = pdal.Pipeline(json)
pipeline.validate() # check if our JSON and options were good
pipeline.loglevel = 8 #really noisy
count = pipeline.execute()
arrays = pipeline.arrays
metadata = pipeline.metadata
log = pipeline.log
