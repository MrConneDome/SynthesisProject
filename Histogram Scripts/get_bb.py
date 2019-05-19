# -*- coding: utf-8 -*-
"""
small script to estimate smallest bounding box on given point_cloud
@author: Konrad Jarocki
"""

import psycopg2
#Connect to postgresql database with postGIS extension installed
def getbb(dbname, user, table):
    conn = psycopg2.connect("dbname={} user = {}".format(dbname, user))
    cur = conn.cursor()
    boundingbox= [0 for x in range(4)]
    #Query for bounding box
    cur.execute("select min(x) as x_min, min(y) as y_min, max(x) as x_max, max(y) as y_max from {};".format(table)) 
#Reaching the result
    for record in cur:
    
        boundingbox[0] = int(record[0])
        boundingbox[1] = int(record[2])
        boundingbox[2] = int(record[1])
        boundingbox[3] = int(record[3])
        
        print('bounding box: ', boundingbox)
    return boundingbox


    
    
