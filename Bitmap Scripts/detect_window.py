"""
#Testing detection possibilities in OpenCV library 
@author: Konrad Jarocki

"""

import cv2
import numpy as np


def detectrectange(fn):
    
    img = cv2.imread(fn,0)
          
    ret,thresh = cv2.threshold(img,150,255,cv2.THRESH_BINARY)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)   
    contours,hierarchy = cv2.findContours(thresh, 1, 2)

    for cnt in contours:
        
        image2 = cv2.drawContours(img, [cnt],-1, (0,50,50) ,2)     
        x,y,w,h = cv2.boundingRect(cnt)
        image = cv2.rectangle(img,(x,y),(x+w,y+h),(110,0,50),2)
        
        cv2.imshow('sample image',image)
        cv2.waitKey(0)
        
detectrectange('test.jpg')