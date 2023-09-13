#!/usr/bin/env python3

import cv2
import numpy as np
import argparse
import time
import io

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=2, help="Video Device number")
args = parser.parse_args()

if args.device:
    dev = args.device
else:
    dev = 2

cp = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)

cap.set(cv.CAP_PROP_CONVERT_RGB, 0.0)

width = 256
height = 192

cv2.namedWindow('Thermal Camera', cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Thermal Camera', width, height)

#Set the coordinates of the pixel that you want to read the data from
pix = [96,128]

def rec():
	now = time.strftime("%Y%m%d--%H%M%S")
	videoOut = cv2.VideoWriter(now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'),25, (newWidth,newHeight))
	return(videoOut)

def snapshot(heatmap):
	now = time.strftime("%Y%m%d-%H%M%S") 
	snaptime = time.strftime("%H:%M:%S")
	cv2.imwrite("TC001"+now+".png", heatmap)
	return snaptime

while cap.isOpened():
	ret, frame = cap.read()
	if ret==True:
		idata, tdata = np.array_split(frame, 2)

		hi = tdata[pix[0]][pix[1]][0]
		lo = tdata[pix[0]][pix[1]][1]
		lo = lo*256
		rawtemp = hi+lo
		tempC = (rawtemp/64)-273.15
		tempC = round(tempC,2)
		tempK = (rawtemp/64)
		tempk = round(tempK)

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
		himin = thdata[lcol][lrow][0]
		lomin=lomin*256
		mintemp = himin+lomin
		mintemp = (mintemp/64)-273.15
		mintemp = round(mintemp,2)

		#find the average temperature in the frame
		loavg = thdata[...,1].mean()
		hiavg = thdata[...,0].mean()
		loavg=loavg*256
		avgtemp = loavg+hiavg
		avgtemp = (avgtemp/64)-273.15
		avgtemp = round(avgtemp,2)

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
		
		# draw crosshairs
		cv2.line(heatmap,(pix[0],pix[1]+20),\
		(pix[0],pix[1]-20),(255,255,255),2) #vline
		cv2.line(heatmap,(pix[0]+20,pix[1]),\
		(pix[0]-20,pix[1]),(255,255,255),2) #hline

		cv2.line(heatmap,(pix[0],pix[1]+20),\
		(pix[0],pix[1]-20),(0,0,0),1) #vline
		cv2.line(heatmap,(pix[0]+20,pix[1]),\
		(pix[0]-20,pix[1]),(0,0,0),1) #hline
		#show temp
		cv2.putText(heatmap,str(tempC)+' C', (pix[0]+10, pix[1]-10),\
		cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 0, 0), 2, cv2.LINE_AA)
		cv2.putText(heatmap,str(tempC)+' C', (pix[0]+10, pix[1]-10),\
		cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

		cv2.imshow('Thermal',heatmap)

		if keyPress == ord('m'): #m to cycle through color maps
			colormap += 1
			if colormap == 11:
				colormap = 0
		
		if keyPress == ord('p'): #f to finish reording
			snaptime = snapshot(heatmap)

		if keyPress == ord('q'):
			break
			capture.release()
			cv2.destroyAllWindows()

#To-Do - Add graphing with matplotlib for the pix temp, high temp, low temp, and average temp