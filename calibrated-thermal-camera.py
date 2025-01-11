import cv2
import numpy as np
import time

dev = 0
pixels = []

cap = cv2.VideoCapture(dev,cv2.CAP_ANY)
#print(cap.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT))
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
calib = np.load('CALIBRATION-DATA.npy')
D = []

width = 256
height = 192
scale = 1

colormap = 0
font = cv2.FONT_HERSHEY_SIMPLEX

cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal', width,height)
hud = True

def getTemp(thdata,coords):
    global calib
    a = calib[coords[0],coords[1],0]
    b = calib[coords[0],coords[1],1]
    hi = thdata[coords[0]][coords[1]][0]
    lo = thdata[coords[0]][coords[1]][1]
    lo *= 256
    rawtemp = hi+lo
    temp = a*rawtemp + b #With calibration
    #temp = rawtemp/64 #Without calibration
    temp = round(temp,2)
    return temp

def tempsmooth(tdata,coor):
    l = [getTemp(tdata,(coor[0]-1,coor[1]-1)),
         getTemp(tdata,(coor[0],coor[1]-1)),
        getTemp(tdata,(coor[0]+1,coor[1]-1)),
        getTemp(tdata,(coor[0]-1,coor[1])),
        getTemp(tdata,(coor[0],coor[1])),
        getTemp(tdata,(coor[0]+1,coor[1])),
        getTemp(tdata,(coor[0]-1,coor[1]+1)),
        getTemp(tdata,(coor[0],coor[1]+1)),
        getTemp(tdata,(coor[0]+1,coor[1]+1))]
    avg = 0
    for i in l:
        avg += i
    return round(avg/len(l),2)

def drawData(coor,temp):
    #global heatmap # It is the image that the data will be drawn on
    global scale # Scale of the interpolated image so that the coordinates can be shifted
    y = coor[0]*scale
    x = coor[1]*scale
    global imdata
    # draw crosshairs
    cv2.line(imdata,(x,y+20),\
    (x,y-20),(255,255,255),2) #vline
    cv2.line(imdata,(x+20,y),\
    (x-20,y),(255,255,255),2) #hline

    cv2.line(imdata,(x,y+20),\
    (x,y-20),(0,0,0),1) #vline
    cv2.line(imdata,(x+20,y),\
    (x-20,y),(0,0,0),1) #hline
    #show temp
    cv2.putText(imdata,str(temp)+' K', (x+10, y-10),\
    cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(imdata,str(temp)+' K', (x+10, y-10),\
    cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)
    return True

#Set up for the clicking top select pixel functionality
def click_event(event, x, y, flags, params):
    global pixels
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'({x},{y})')
        pixels.append([y,x])

cv2.setMouseCallback('Thermal', click_event)

if not cap.isOpened():
    print("Error establishing connection")

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        frame = frame.flatten()
        frame = frame.reshape((384,256,-1))
        imdata,thdata = np.array_split(frame, 2)
        print(thdata[0][0])
        # Convert the real image to RGB
        bgr = cv2.cvtColor(imdata,  cv2.COLOR_YUV2BGR_YUYV)
        #bgr = imdata.copy()
        #apply colormap
        if colormap == 0:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_JET)
            cmapText = 'Jet'
        if colormap == 1:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_HOT)
            cmapText = 'Hot'
        if colormap == 2:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_MAGMA)
            cmapText = 'Magma'
        if colormap == 3:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_INFERNO)
            cmapText = 'Inferno'
        if colormap == 4:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PLASMA)
            cmapText = 'Plasma'
        if colormap == 5:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_BONE)
            cmapText = 'Bone'
        if colormap == 6:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_SPRING)
            cmapText = 'Spring'
        if colormap == 7:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_AUTUMN)
            cmapText = 'Autumn'
        if colormap == 8:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_VIRIDIS)
            cmapText = 'Viridis'
        if colormap == 9:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PARULA)
            cmapText = 'Parula'
        if colormap == 10:
            heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_RAINBOW)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            cmapText = 'Inv Rainbow'

        imdata = heatmap
        #Draw data
        for x in pixels:
            t = getTemp(thdata,x)
            drawData(x, t)
            D.append((t,time.time()))
		#display image
        cv2.imshow('Thermal',heatmap)

        keyPress = cv2.waitKey(1)
        if keyPress == ord('m'): #m to cycle through color maps
            colormap += 1
            if colormap == 11:
                colormap = 0


        if keyPress == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

import matplotlib.pyplot as plt
x = [i[1] for i in D]
y = [i[0] for i in D]
plt.plot(x,y)
plt.show()
		
