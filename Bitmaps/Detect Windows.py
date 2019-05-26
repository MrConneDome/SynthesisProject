"""
@author: Konrad Jarocki
#Finding the windows 
"""

import cv2
import numpy as np

def find_if_close(cnt1,cnt2):
    row1,row2 = cnt1.shape[0],cnt2.shape[0]
    for i in range(row1):
        for j in range(row2):
            dist = np.linalg.norm(cnt1[i]-cnt2[j])
            if abs(dist) < 16 :
                return True
            elif i==row1-1 and j==row2-1:
                return False
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
#   s print('area:',area)
    return area
            
            
   
    
img = cv2.imread('07rm5.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY) 
contours,hier = cv2.findContours(thresh,1,2)

LENGTH = len(contours)
status = np.zeros((LENGTH,1))
group_numbers = np.zeros((LENGTH,1))
cont_areas = np.zeros((LENGTH,1))
cont_w = np.zeros((LENGTH,1))
cont_h = np.zeros((LENGTH,1))

contours_saved = []
print(LENGTH)
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
height = 531
lenght = 616
area = 310939
unified = []
maximum = int(status.max())+1
groups_area = [0 for x in range(16)]
groups_h = [0 for x in range(16)]
groups_w = [0 for x in range(16)]
counter1 = 0
counter2 = 0
counter3 = 0
similarity = 0.4
similarity_d = 0.5
group_ratio = [0 for x in range(4)]
for i in range(maximum):
    pos = np.where(status==i)[0]
    if pos.size != 0:        
        cont = np.vstack(contours[i] for i in pos)        
        x,y,w,h = cv2.boundingRect(cont)        
        c_area = w*h
        if c_area<0.4*area and c_area>0.003*area and w>20 and h>20:

            cont_areas[counter3] = c_area
            cont_h[counter3] = h
            cont_w[counter3] = w
            counter1 = 1        
            for group_area in groups_area:
                if group_area >0:
                   
                    #if area is similar to the average of existing group
#                    print('iterating group', counter1)
                    if c_area>group_area*(1-similarity) and c_area<group_area*(1+similarity):
                        if w>groups_w[counter1]*(1-similarity_d) and w<groups_w[counter1]*(1+similarity_d):
                            if h>groups_h[counter1]*(1-similarity_d) and h<groups_h[counter1]*(1+similarity_d):
                                print('Found similar group, average area vs window:',group_area,c_area,'group number',counter1,groups_h[counter1],groups_w[counter1],'window number', counter3,h,w)
                                group_numbers[counter3] = counter1
                    counter1+=1
            #if non group assigned
            if group_numbers[counter3] == 0:
                counter2+=1
                group_numbers[counter3] = counter2
                print('Did not find similar group, window area, height, width:',c_area,h,w,' creating group number',counter2,'window number', counter3)
            groups_area[int(group_numbers[counter3])] = averagecounter(cont_areas, group_numbers, group_numbers[counter3])
            groups_w[int(group_numbers[counter3])] = averagecounter(cont_w, group_numbers, group_numbers[counter3])
            groups_h[int(group_numbers[counter3])] = averagecounter(cont_h, group_numbers, group_numbers[counter3])
            print('Group',group_numbers[counter3],'Updated area,height and width:', groups_area[int(group_numbers[counter3])],groups_h[int(group_numbers[counter3])],groups_w[int(group_numbers[counter3])])
            counter3+=1
       
counter = 0
for i in range(maximum):
    pos = np.where(status==i)[0]
    if pos.size != 0:        
        cont = np.vstack(contours[i] for i in pos)  
        x,y,w,h = cv2.boundingRect(cont)
        c_area = w*h
        if c_area<0.4*area and c_area>0.003*area and w>20 and h>20:
            group_n = int(group_numbers[counter])
            print(x,y,h,w)
            M = cv2.moments(cont)
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))
            x,y = cX-groups_w[group_n]/2, cY-groups_h[group_n]/2
            h,w = groups_h[group_n], groups_w[group_n]
           
            print(x,y,cX,cY,h,w,groups_h[group_n]/2)
            print('...')
            counter+=1
            ratio = round(int(w*h)/int(area),3)
            image = cv2.rectangle(img,(x,y),(x+w,y+h),(110,0,50),2)
            cv2.putText(image, '.', (cX, cY), 2,0.5, (0, 120, 255), 1)
            cv2.putText(image, str(ratio), (cX-h/2, cY+w/2), 2,0.5, (0, 120, 255), 1)
cv2.imshow('Windows Detection',image)
#        unified.append(hull)
counter = 0

for area in groups_area:

        
    if area!=0:

        print('Group nr', counter,'area', area)
        counter +=1


#cv2.drawContours(img,unified,-1,(0,255,0),2)
#cv2.drawContours(thresh,unified,-1,255,-1)
#cv2.imshow('Windows Detection',img)