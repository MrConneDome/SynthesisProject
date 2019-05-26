# -*- coding: utf-8 -*-
"""
Created on Sun May 26 16:08:40 2019

@author: konra
"""

import cv2
import numpy as np

def find_if_close(cnt1,cnt2):
    row1,row2 = cnt1.shape[0],cnt2.shape[0]
    for i in range(row1):
        for j in range(row2):
            dist = np.linalg.norm(cnt1[i]-cnt2[j])
            if abs(dist) < 10 :
                return True
            elif i==row1-1 and j==row2-1:
                return False

img = cv2.imread('07rm7.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY) 
contours,hier = cv2.findContours(thresh,1,2)

LENGTH = len(contours)
status = np.zeros((LENGTH,1))

for i,cnt1 in enumerate(contours):
    x = i    
    if i != LENGTH-1:
        for j,cnt2 in enumerate(contours[i+1:]):
            x = x+1
            dist = find_if_close(cnt1,cnt2)
            if dist == True:
                val = min(status[i],status[x])
                status[x] = status[i] = val
            else:
                if status[x]==status[i]:
                    status[x] = i+1

unified = []
maximum = int(status.max())+1
for i in range(maximum):
    pos = np.where(status==i)[0]
    if pos.size != 0:
        cont = np.vstack(contours[i] for i in pos)
        x,y,w,h = cv2.boundingRect(cont)
        image = cv2.rectangle(img,(x,y),(x+w,y+h),(110,0,50),2)
        cv2.imshow('Windows Detection',image)
#        unified.append(hull)

#cv2.drawContours(img,unified,-1,(0,255,0),2)
#cv2.drawContours(thresh,unified,-1,255,-1)
cv2.imshow('Windows Detection',img)