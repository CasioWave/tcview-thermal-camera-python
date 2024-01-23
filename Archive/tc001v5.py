#!/usr/bin/env python3

'''
Diptanuj Sarkar 14 September 2023

A python program that reads data from the Topdon TC001 Thermal camera.
The program reads raw temperature data from the camera, tabulates it, and generates graphs
of minimum, maximum and average temperature - along with any pixels that the user specifies.
'''

#Library imports
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import csv
import pyvisa

# Pyvisa stuff (setup)
rm = pyvisa.ResourceManager()
rm.list_resources()
inst = rm.open_resource('GPIB0::15::INSTR')
#print(inst.query("*IDN?"))
#P=inst.query("Out2.Value?")

cmdString="Out2.PID.Ramp"
setValue=0.033
inst.write(cmdString + ' ' + str(setValue))

cmdString="Out2.PID.setpoint"
setValue=310
inst.write(cmdString + ' ' + str(setValue))

dev = 0 #Set the device id
#init video
cap = cv2.VideoCapture(dev, cv2.CAP_V4L) # OpenCV video capture object
#pull in the video but do NOT automatically convert to RGB, else it breaks the temperature data!
#https://stackoverflow.com/questions/63108721/opencv-setting-videocap-property-to-cap-prop-convert-rgb-generates-weird-boolean
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
flTemp = True

#256x192 General settings
width = 256 #Sensor width
height = 192 #sensor height
scale = 3 #scale multiplier
newWidth = width*scale 
newHeight = height*scale
alpha = 1.0 # Contrast control (1.0-3.0)
colormap = 0 #This variable stores the id of the color map that is to be applied to the image
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
pixels = [[96,128],[1,1]] # List of the pixel coordinates to be monitored

# This list will hold all the temperature and time data for the user specified pixels
temps = []
for i in pixels:
	temps.append([])

#PID Temp read
pidT = []

t_avg = [] # List holds all the average temperature values as (K, C, mils from exp start)
t_min = [] # List holds all the minimum temperature values as (K, C, mils from exp start)
t_max = [] # List holds all the maximum temperature values as (K, C, mils from exp start)

def rec():
	now = time.strftime("%Y%m%d--%H%M%S")
	#Do not use mp4
	videoOut = cv2.VideoWriter(fi+now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'),25, (newWidth,newHeight))
	return(videoOut)

def snapshot(heatmap):
    now = time.strftime("%Y%m%d-%H%M%S") 
    snaptime = time.strftime("%H:%M:%S")
    cv2.imwrite(fi+"TC001"+now+".png", heatmap)
    return snaptime

def getTemp(tdata,coor):
    hi = tdata[coor[0]][coor[1]][0]
    lo = tdata[coor[0]][coor[1]][1]
    lo = lo*256
    rawtemp = hi+lo
    tempC = (rawtemp/64)-273.15
    tempc = round(tempC,2)
    tempK = (rawtemp/64)
    tempk = round(tempK)
    #print('Coor ->'+str(coor)+' T>'+str(tempc))
    return (tempc, tempk)

def drawData(coor,temp):
    global heatmap # It is the image that the data will be drawn on
    global scale # Scale of the interpolated image so that the coordinates can be shifted
    x = coor[0]*scale
    y = coor[1]*scale
    #print(x,y)
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
    T=inst.query("In2.Value?")
    time.sleep(1)
    if ret:
        imdata, thdata = np.array_split(frame,2)
        s = time.time()
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
        #print(lcol)
        himin = thdata[lcol][lrow][0]
        lomin=lomin*256
        mintemp = himin+lomin
        mintemp = (mintemp/64)-273.15
        mintemp = round(mintemp,2)

        #Calculate average temperature of the scene
        loavg = thdata[...,1].mean()
        hiavg = thdata[...,0].mean()
        loavg=loavg*256
        avgtemp = loavg+hiavg
        avgtemp = (avgtemp/64)-273.15
        avgtemp = round(avgtemp,2)

        #For each of the pixels tracked, find the temperature and store ir
        for i in range(0,len(pixels)):
            tC, tK = getTemp(thdata, pixels[i])
            if dataRec:
                interval = abs(stamp-s)
                pidT.append((T, interval))
                temps[i].append((tC,tK,interval))
            t.append((tC, tK))
        
        #Data for the average, min, and max temperatures will only be recorded if dataRec is on
        if dataRec:
            t_max.append((maxtemp,maxtemp+273.15,interval))
            t_min.append((mintemp,mintemp+273.15,interval))
            t_avg.append((avgtemp,avgtemp+273.15,interval))
        
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
        
        #Draws the cursor for each of the pixels being tracked, and draws temperature of the point in C
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

        #display floating max temp
        if flTemp:
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

        #Continue recording the video if the condition is true
        if recording == True:
            elapsed = (time.time() - start)
            elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed)) 
            #print(elapsed)
            videoOut.write(heatmap)

        keyPress = cv2.waitKey(1)
        if keyPress == ord('[') and dataRec == False: #Starts the data collection
            dataRec = True
            stamp = time.time()

        if keyPress == ord(']') and dataRec == True: #Ends the data collection
            dataRec = False
            s = time.time()
        
        if keyPress == ord('a'): #Increase blur radius
            rad += 1
        if keyPress == ord('z'): #Decrease blur radius
            rad -= 1
            if rad <= 0:
                rad = 0
        
        #Turn on or off the Floating temperature drawing for max and min temp
        if keyPress == ord(','):
            flTemp = True
        if keyPress == ord('.'):
            flTemp = False

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
            if dispFullscreen == False:
                cv2.resizeWindow('Thermal', newWidth,newHeight)
        if keyPress == ord('c'): #Decrease scale
            scale -= 1
            if scale <= 1:
                scale = 1
            newWidth = width*scale
            newHeight = height*scale
            if dispFullscreen == False:
                cv2.resizeWindow('Thermal', newWidth,newHeight)

        if keyPress == ord('i'): #enable fullscreen
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

        #Hide or display the HUD on the screen
        if keyPress == ord('h'):
            if hud==True:
                hud=False
            elif hud==False:
                hud=True

        if keyPress == ord('m'): #m to cycle through color maps
            colormap += 1
            if colormap == 11:
                colormap = 0

        if keyPress == ord('r') and recording == False: #r to start recording
            videoOut = rec()
            recording = True
            start = time.time()
        if keyPress == ord('t'): #t to finish recording
            recording = False
            elapsed = "00:00:00"

        if keyPress == ord('p'): #p to take a snapshot of the current screen
            snaptime = snapshot(heatmap)

        if keyPress == ord('q'): #q to QUIT the application
            cap.release()
            cv2.destroyAllWindows()
            break

'''
#Store the tracked temperature data of all the pixels that were being tracked, and draw + save the graphs of pixels, max, min and avg temp
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
    fn = fi+'average.csv'
    csvfile = open(fn, 'w')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for i in t_avg:
        csvwriter.writerow(i)
    
    fn = fi+'max.csv'
    csvfile = open(fn, 'w')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for i in t_max:
        csvwriter.writerow(i)

    fn = fi+'min.csv'
    csvfile = open(fn, 'w')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for i in t_min:
        csvwriter.writerow(i)
    for j in range(0,len(temps)):
        x = []
        y = []
        for i in temps[j]:
            y.append(i[1])
            x.append(i[-1])
        plt.plot(x,y)
        plt.savefig(fi+str(j)+'-pixelGraph.jpg')
        plt.clf()
    
    x = []
    y = []
    for i in t_max:
        y.append(i[1])
        x.append(i[-1])
    plt.plot(x,y)
    plt.savefig(fi+'maxGraph.jpg')
    plt.clf()

    x = []
    y = []
    for i in t_min:
        y.append(i[1])
        x.append(i[-1])
    plt.plot(x,y)
    plt.savefig(fi+'minGraph.jpg')
    plt.clf()

    x = []
    y = []
    for i in t_avg:
        y.append(i[1])
        x.append(i[-1])
    plt.plot(x,y)
    plt.savefig(fi+'avgGraph.jpg')

    plt.show()

with open(fi+'PIDdata.csv') as f:
    csvwriter = csv.writer(f)
    # writing the fields
    fields = ['Time (ms)','Temp (K) from Camera', 'Temp (K) from PID']
    csvwriter.writerow(fields)
    # writing the data rows
    for j in range(0,len(temps[0])):
        a = [float(temps[0][j][-1]), float(temps[0][j][-2]), T[j][0]]
        csvwriter.writerow(a)
'''

if len(temps[0])>1:
    fields = ['Index', 'Interval (ms)', 'Temp (K) - PID']
    for i in range(len(pixels)):
        fields.append('Temp (K) - Pixel '+str(i))
    fn = fi+'data'+str(time.strftime('%Y-%m-%d_%H-%M-%S'))+'.csv'
    csvfile = open(fn,'w')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for i in range(len(temps[0])):
        wr = []
        wr.append(str(i))
        wr.append(str(temps[0][i][-1]))
        wr.append(str(pidT[i][0]))
        for o in range(len(temps)):
            wr.append(str(temps[o][i][2]))
        csvwriter.writerow(wr)
    csvfile.close()

print('Goodbye')
