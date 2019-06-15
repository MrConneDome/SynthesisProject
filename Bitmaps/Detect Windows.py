"""
@author: Konrad Jarocki
#Finding the windows 
"""

import cv2
import numpy as np

#short fuction to assign contours to same window basing on distance between them
def find_if_close(cnt1,cnt2):
    row1,row2 = cnt1.shape[0],cnt2.shape[0]
    for i in range(row1):
        for j in range(row2):
            dist = np.linalg.norm(cnt1[i]-cnt2[j])
            #distance condition
            x1,y1,w1,h1 = cv2.boundingRect(cnt1) 
            x2,y2,w2,h2 = cv2.boundingRect(cnt2) 
            c_area1 = w1*h1
            c_area2 = w2*h2
            if abs(dist) < 16 and  c_area1<100000 and c_area2<100000:
                return True            
            elif i==row1-1 and j==row2-1:
                return False
          
#Function to calculate average of value in the group            
def averagecounter(cont_areas, group_numbers, group_number):
    counter = 0
    counter2 = 0
    area = 0
    for i in group_numbers:       
        if i==group_number:
            
            area += cont_areas[counter2]
            counter +=1
            
        counter2+=1   
        
    area = area/counter
    return area
            
#Function to assign highest value among specific group member as group representative:
def maximumcounter(cont_areas, group_numbers, group_number):
    counter = 0
    counter2 = 0             
    area = 0
    for i in group_numbers:
        if i==group_number:
            if cont_areas[counter]>area:
                area = cont_areas[counter]
        counter+=1
                
    return area
#Importing the image    
img = cv2.imread('07rm5.jpg')

#Changing the type of data to fit the requirements of OpenCV
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY) 

#Finding all the contours and making arrays of proper size
contours,hier = cv2.findContours(thresh,1,2)
LENGTH = len(contours)
status = np.zeros((LENGTH,1))
group_numbers = np.zeros((LENGTH,1))
cont_areas = np.zeros((LENGTH,1))
cont_w = np.zeros((LENGTH,1))
cont_h = np.zeros((LENGTH,1))
contours_saved = []
print(LENGTH)

#assing the contours to windows
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
                    
#input parameters for facade calculation, to change later
height = 531
lenght = 616
area = 310939

similarity = 0.6
similarity_d = 0.8

#Some parameters
groups_area = [0 for x in range(16)]
groups_h = [0 for x in range(16)]
groups_w = [0 for x in range(16)]
group_ratio = [0 for x in range(4)]
counter1 = 0
counter2 = 0
counter3 = 0
unified = []
maximum = int(status.max())+1

#Iterating for every window
for i in range(maximum):
    pos = np.where(status==i)[0]
    
    if pos.size != 0:                
        
        cont = np.vstack(contours[i] for i in pos)        
        x,y,w,h = cv2.boundingRect(cont)        
        c_area = w*h
        
        #Condition for size and minimum height and width
        if c_area<0.4*area and c_area>0.002*area and w>20 and h>20:
            
            cont_areas[counter3] = c_area
            cont_h[counter3] = h
            cont_w[counter3] = w
            counter1 = 1        
            
            for group_area in groups_area:
                if group_area >0:
                   
                    #if area is similar to the group parameters (area, height, width)
                    if c_area>group_area*(1-similarity) and c_area<group_area*(1+similarity):
                        if w>groups_w[counter1]*(1-similarity_d/2) and w<groups_w[counter1]*(1+similarity_d):
                            if h>groups_h[counter1]*(1-similarity_d/2) and h<groups_h[counter1]*(1+similarity_d):
                                
                                print('Found similar group, average area vs window:',group_area,c_area,'group number',counter1,groups_h[counter1],groups_w[counter1],'window number', counter3,h,w)
                                group_numbers[counter3] = counter1
                                
                    counter1+=1
                    
            #if non group assigned
            if group_numbers[counter3] == 0:
                
                counter2+=1
                group_numbers[counter3] = counter2
                print('Did not find similar group, window area, height, width:',c_area,h,w,' creating group number',counter2,'window number', counter3)
                
            #calculate the parameters for the group after assignation
            groups_area[int(group_numbers[counter3])] = maximumcounter(cont_areas, group_numbers, group_numbers[counter3])
            groups_w[int(group_numbers[counter3])] = maximumcounter(cont_w, group_numbers, group_numbers[counter3])
            groups_h[int(group_numbers[counter3])] = maximumcounter(cont_h, group_numbers, group_numbers[counter3])
            print('Group',group_numbers[counter3],'Updated area,height and width:', groups_area[int(group_numbers[counter3])],groups_h[int(group_numbers[counter3])],groups_w[int(group_numbers[counter3])])
            
            counter3+=1
       
counter = 0


#Calculating the position of the windows and areas in respect to groups averages
for i in range(maximum):
    pos = np.where(status==i)[0]
    if pos.size != 0:        
        
        cont = np.vstack(contours[i] for i in pos) 
        
        x,y,w,h = cv2.boundingRect(cont)
        c_area = w*h
        
        if c_area<0.4*area and c_area>0.003*area and w>20 and h>20:
            
            #Values to calculate new positions
            group_n = int(group_numbers[counter])
            M = cv2.moments(cont)
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))
            
            #New parameters of windows
            x,y = cX-groups_w[group_n]/2, cY-groups_h[group_n]/2
            h,w = groups_h[group_n], groups_w[group_n]
           

            counter+=1
            ratio = round(int(w*h)/int(area),3)
            image = cv2.rectangle(img,(x,y),(x+w,y+h),(110,0,50),2)
            cv2.putText(image, '.', (cX, cY), 2,0.5, (0, 120, 255), 1)
            cv2.putText(image, str(ratio), (cX-h/2, cY+w/2), 2,0.5, (0, 120, 255), 1)
        
#Assessment
cv2.imshow('Windows Detection',image)
counter = 0
 
for area in groups_area:   

    if area!=0:
        print('Group nr', counter,'area', area, 'ratio:', groups_h[counter+1]/groups_w[counter+1], 'h:', groups_h[counter+1], 'w:', groups_w[counter+1])
        counter +=1