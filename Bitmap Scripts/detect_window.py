"""
#Testing detection possibilities in OpenCV library 
@author: Konrad Jarocki

"""

import cv2
import numpy as np


def detectrectange(fn,size_factor_min,size_factor_max):
    #Opening the image
    img = cv2.imread(fn,0)
    height, width = img.shape[:2]
    
    #size of the windows for plot
    cv2.namedWindow('Windows Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Windows Detection', 1000,1000)
    
    #Creating the threshold array for contour detection
    ret,thresh = cv2.threshold(img,150,255,cv2.THRESH_BINARY) 
    #changing image to RGB to plot in colors
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)      
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    
    #Iterating every contour
    for cnt in contours: 
        
        #Finding parameters of bounding box 
        x,y,w,h = cv2.boundingRect(cnt)
        #Ratio compare to the whole facade
        ratio = round(int(w*h)/int(height*width),4)
        #Position for text
        M = cv2.moments(cnt)
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        
        #Condtion for too small and too big windows
        if w*h<size_factor_max*height*width and w*h>size_factor_min*height*width:
            #Plotting the results
            image = cv2.rectangle(img,(x,y),(x+w,y+h),(110,0,50),2)
            cv2.putText(image, 'R:'+str(ratio), (cX, cY), 2,0.5, (0, 120, 255), 1)
            cv2.imshow('Windows Detection',image)
        else:
            print('too big or too small')
    cv2.waitKey(0)
        
detectrectange('test2.jpg',0.009,0.4)