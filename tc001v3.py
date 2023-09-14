#!/usr/bin/env python3

'''
Diptanuj Sarkar 14 September 2023

A python program that reads data from the Topdon TC001 Thermal camera.
The program reads raw temperature data from the camera, tabulates it, and generates graphs
of minimum, maximum and average temperature - along with any pixels that the user specifies
'''

import cv2
import numpy as np
import argparse
import time
import io
import matplotlib.pyplot as plt
import csv

# Gets the arguments required from the shell execution
parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help="Video Device number e.g. 0, use v4l2-ctl --list-devices")
args = parser.parse_args()

if args.device:
	dev = args.device
else:
	dev = 2

#init video
cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)

#pull in the video but do NOT automatically convert to RGB, else it breaks the temperature data!
#https://stackoverflow.com/questions/63108721/opencv-setting-videocap-property-to-cap-prop-convert-rgb-generates-weird-boolean
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)

#256x192 General settings
width = 256 #Sensor width
height = 192 #sensor height
scale = 3 #scale multiplier
newWidth = width*scale 
newHeight = height*scale
alpha = 1.0 # Contrast control (1.0-3.0)
colormap = 0
font=cv2.FONT_HERSHEY_SIMPLEX
dispFullscreen = False
cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal', newWidth,newHeight)
rad = 0 #blur radius
threshold = 2
hud = True
recording = False
elapsed = "00:00:00"
snaptime = "None"

# New variables
fi = './' # Path of the directory where the data will be written to
dataRec = False # Set to True when the experiment is started
pixels = [[96,128]] # List of the pixel coordinates to be monitored

# This list will hold all the temperature and time data for the user specified pixels
temps = []
for i in pixels:
	temps.append([])

t_avg = [] # List holds all the average temperature values as (K, C, mils from exp start, abs time)
t_min = [] # List holds all the minimum temperature values as (K, C, mils from exp start, abs time)
t_max = [] # List holds all the maximum temperature values as (K, C, mils from exp start, abs time)

def rec():
	now = time.strftime("%Y%m%d--%H%M%S")
	#do NOT use mp4 here, it is flakey!
	videoOut = cv2.VideoWriter(now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'),25, (newWidth,newHeight))
	return(videoOut)

def snapshot(heatmap):
	#I would put colons in here, but it Win throws a fit if you try and open them!
	now = time.strftime("%Y%m%d-%H%M%S") 
	snaptime = time.strftime("%H:%M:%S")
	cv2.imwrite("TC001"+now+".png", heatmap)
	return snaptime

def getTemp(tdata,coor):
	hi = tdata[coor[0]][coor[1]][0]
	lo = tdata[coor[0]][coor[1]][1]
	lo = lo*256
	rawtemp = hi+lo
	tempC = (rawtemp/64)-273.15
	tempC = round(tempC,2)
	tempK = (rawtemp/64)
	tempk = round(tempK)
	return (tempC, tempK)

def drawData(coor,temp):
    global scale
    global width
    global height
    x = coor[0]
    y = coor[1]
    print(x,y)
    # draw crosshairs
    cv2.line(heatmap,(x,y+20),\
    (x,y-20),(255,255,255),2) #vline
    cv2.line(heatmap,(x+20,y),\
    (x-20,y),(255,255,255),2) #hline

    cv2.line(heatmap,(x,y+20),\
    (x,y-20),(0,0,0),1) #vline
    cv2.line(heatmap,(x+20,y),\
    (x-20,y),(0,0,0),1) #hline
    #show temp
    cv2.putText(heatmap,str(temp)+' C', (x+10, y-10),\
    cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(heatmap,str(temp)+' C', (x+10, y-10),\
    cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)
    return True

while(cap.isOpened()):
    ret, frame = cap.read()
    if dataRec:
        stamp = time.time()
    
    if ret:
        imdata, thdata = np.array_split(frame,2)
        t = []
        #find the max temperature in the frame
        lomax = thdata[...,1].max()
        posmax = thdata[...,1].argmax()
        #since argmax returns a linear index, convert back to row and col
        mcol,mrow = divmod(posmax,width)
        himax = thdata[mcol][mrow][0]
        lomax=lomax*256
        maxtemp = himax+lomax
        maxtemp = (maxtemp/64)-273.15
        maxtemp = round(maxtemp,2)

        #find the lowest temperature in the frame
        lomin = thdata[...,1].min()
        posmin = thdata[...,1].argmin()
        #since argmax returns a linear index, convert back to row and col
        lcol,lrow = divmod(posmin,width)
        print(lcol)
        himin = thdata[lcol][lrow][0]
        lomin=lomin*256
        mintemp = himin+lomin
        mintemp = (mintemp/64)-273.15
        mintemp = round(mintemp,2)

        loavg = thdata[...,1].mean()
        hiavg = thdata[...,0].mean()
        loavg=loavg*256
        avgtemp = loavg+hiavg
        avgtemp = (avgtemp/64)-273.15
        avgtemp = round(avgtemp,2)

        for i in pixels:
            t.append(getTemp(thdata,i))
        
        if dataRec:
            interval = stamp - s
            for i in range(0,len(pixels)):
                temps[i].append((t[i][0],t[i][1],interval))
            t_max.append((maxtemp+273.15,maxtemp,interval))
            t_min.append((mintemp+273.15,mintemp,interval))
            t_avg.append((avgtemp+273.15,avgtemp,interval))
        
        # Convert the real image to RGB
        bgr = cv2.cvtColor(imdata,  cv2.COLOR_YUV2BGR_YUYV)
        #Contrast
        bgr = cv2.convertScaleAbs(bgr, alpha=alpha)#Contrast
        #bicubic interpolate, upscale and blur
        bgr = cv2.resize(bgr,(newWidth,newHeight),interpolation=cv2.INTER_CUBIC)#Scale up!
        if rad>0:
            bgr = cv2.blur(bgr,(rad,rad))

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
        
        for i in range(0,len(pixels)):
            drawData(pixels[i],t[i][0])

        if hud==True:
            # display black box for our data
            cv2.rectangle(heatmap, (0, 0),(160, 120), (0,0,0), -1)
            # put text in the box
            cv2.putText(heatmap,'Avg Temp: '+str(avgtemp)+' C', (10, 14),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(heatmap,'Label Threshold: '+str(threshold)+' C', (10, 28),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(heatmap,'Colormap: '+cmapText, (10, 42),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(heatmap,'Blur: '+str(rad)+' ', (10, 56),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(heatmap,'Scaling: '+str(scale)+' ', (10, 70),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(heatmap,'Contrast: '+str(alpha)+' ', (10, 84),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)


            cv2.putText(heatmap,'Snapshot: '+snaptime+' ', (10, 98),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

            if recording == False:
                cv2.putText(heatmap,'Recording: '+elapsed, (10, 112),\
                cv2.FONT_HERSHEY_SIMPLEX, 0.4,(200, 200, 200), 1, cv2.LINE_AA)
            if recording == True:
                cv2.putText(heatmap,'Recording: '+elapsed, (10, 112),\
                cv2.FONT_HERSHEY_SIMPLEX, 0.4,(40, 40, 255), 1, cv2.LINE_AA)

        #Yeah, this looks like we can probably do this next bit more efficiently!
        #display floating max temp
        if maxtemp > avgtemp+threshold:
            cv2.circle(heatmap, (mrow*scale, mcol*scale), 5, (0,0,0), 2)
            cv2.circle(heatmap, (mrow*scale, mcol*scale), 5, (0,0,255), -1)
            cv2.putText(heatmap,str(maxtemp)+' C', ((mrow*scale)+10, (mcol*scale)+5),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,0), 2, cv2.LINE_AA)
            cv2.putText(heatmap,str(maxtemp)+' C', ((mrow*scale)+10, (mcol*scale)+5),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

        #display floating min temp
        if mintemp < avgtemp-threshold:
            cv2.circle(heatmap, (lrow*scale, lcol*scale), 5, (0,0,0), 2)
            cv2.circle(heatmap, (lrow*scale, lcol*scale), 5, (255,0,0), -1)
            cv2.putText(heatmap,str(mintemp)+' C', ((lrow*scale)+10, (lcol*scale)+5),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,0), 2, cv2.LINE_AA)
            cv2.putText(heatmap,str(mintemp)+' C', ((lrow*scale)+10, (lcol*scale)+5),\
            cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

        #display image
        cv2.imshow('Thermal',heatmap)

        if recording == True:
            elapsed = (time.time() - start)
            elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed)) 
            #print(elapsed)
            videoOut.write(heatmap)

        keyPress = cv2.waitKey(1)
        if keyPress == ord('[') and dataRec == False: #Starts the data collection
            dataRec = True
            s = time.time()

        if keyPress == ord(']') and dataRec == True: #Starts the data collection
            dataRec = False
            s = time.time()
        
        if keyPress == ord('a'): #Increase blur radius
            rad += 1
        if keyPress == ord('z'): #Decrease blur radius
            rad -= 1
            if rad <= 0:
                rad = 0

        if keyPress == ord('s'): #Increase threshold
            threshold += 1
        if keyPress == ord('x'): #Decrease threashold
            threshold -= 1
            if threshold <= 0:
                threshold = 0

        if keyPress == ord('d'): #Increase scale
            scale += 1
            if scale >=5:
                scale = 5
            newWidth = width*scale
            newHeight = height*scale
            if dispFullscreen == False and isPi == False:
                cv2.resizeWindow('Thermal', newWidth,newHeight)
        if keyPress == ord('c'): #Decrease scale
            scale -= 1
            if scale <= 1:
                scale = 1
            newWidth = width*scale
            newHeight = height*scale
            if dispFullscreen == False and isPi == False:
                cv2.resizeWindow('Thermal', newWidth,newHeight)

        if keyPress == ord('q'): #enable fullscreen
            dispFullscreen = True
            cv2.namedWindow('Thermal',cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Thermal',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        if keyPress == ord('w'): #disable fullscreen
            dispFullscreen = False
            cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
            cv2.setWindowProperty('Thermal',cv2.WND_PROP_AUTOSIZE,cv2.WINDOW_GUI_NORMAL)
            cv2.resizeWindow('Thermal', newWidth,newHeight)

        if keyPress == ord('f'): #contrast+
            alpha += 0.1
            alpha = round(alpha,1)#fix round error
            if alpha >= 3.0:
                alpha=3.0
        if keyPress == ord('v'): #contrast-
            alpha -= 0.1
            alpha = round(alpha,1)#fix round error
            if alpha<=0:
                alpha = 0.0


        if keyPress == ord('h'):
            if hud==True:
                hud=False
            elif hud==False:
                hud=True

        if keyPress == ord('m'): #m to cycle through color maps
            colormap += 1
            if colormap == 11:
                colormap = 0

        if keyPress == ord('r') and recording == False: #r to start reording
            videoOut = rec()
            recording = True
            start = time.time()
        if keyPress == ord('t'): #f to finish reording
            recording = False
            elapsed = "00:00:00"

        if keyPress == ord('p'): #f to finish reording
            snaptime = snapshot(heatmap)

        if keyPress == ord('q'):
            break
            capture.release()
            cv2.destroyAllWindows()

if len(temps[0]) > 1:
    fields = ['Temp (C)', 'Temp (K)', 'Timestamp (ms)']
    for i in range(0,len(pixels)):
        fn = fi+str(i)+'-pixeldata.csv'
        with open(fn, 'w') as csvfile:
        # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the fields
            csvwriter.writerow(fields)
            # writing the data rows
            for j in temps[i]:
                csvwriter.writerow(j)
            

x = []
y = []
for i in temps[0]:
    y.append(i[0])
    x.append(i[-1])
plt.plot(x,y)
plt.show()
