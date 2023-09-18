import cv2
import numpy as np
import time

dev = 0
cap = cv2.VideoCapture(dev, cv2.CAP_V4L)

width = 640
height = 480
fi = './'
cap.set(cv2.CAP_PROP_CONVERT_RGB,0.0)

scale = 2

newWidth = scale*width
newHeight = scale*height

alpha = 1.0
colormap = 0
font = cv2.FONT_HERSHEY_SIMPLEX
dispFullscreen = False
cv2.namedWindow('Test', cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('Test', newWidth, newHeight)

rad = 0
threshold = 2
hud = True
recording = False
elapsed = "00:00:00"
snaptime = "None"

def rec():
	now = time.strftime("%Y%m%d--%H%M%S")
	#do NOT use mp4 here, it is flakey!
	videoOut = cv2.VideoWriter(fi+now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'),25, (newWidth,newHeight))
	return(videoOut)

def snapshot(heatmap):
	#I would put colons in here, but it Win throws a fit if you try and open them!
	now = time.strftime("%Y%m%d-%H%M%S") 
	snaptime = time.strftime("%H:%M:%S")
	cv2.imwrite(fi+"TC001"+now+".png", heatmap)
	return snaptime

def drawData(coor,temp):
    global scale
    global heatmap
    #global width
    #global height
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
    imdata = frame
    if ret:
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

        if hud==True:
            # display black box for our data
            cv2.rectangle(heatmap, (0, 0),(160, 120), (0,0,0), -1)
            # put text in the box
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
        
        drawData([300,200],10)
        #display image
        cv2.imshow('Test',heatmap)

        keyPress = cv2.waitKey(1)

        if recording == True:
            elapsed = (time.time() - start)
            elapsed = time.strftime("%H:%M:%S", time.gmtime(elapsed)) 
            #print(elapsed)
            videoOut.write(heatmap)
        
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
            if dispFullscreen == False:
                cv2.resizeWindow('Test', newWidth,newHeight)
        if keyPress == ord('c'): #Decrease scale
            scale -= 1
            if scale <= 1:
                scale = 1
            newWidth = width*scale
            newHeight = height*scale
            if dispFullscreen == False:
                cv2.resizeWindow('Test', newWidth,newHeight)

        if keyPress == ord('q'): #enable fullscreen
            dispFullscreen = True
            cv2.namedWindow('Test',cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Test',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        if keyPress == ord('w'): #disable fullscreen
            dispFullscreen = False
            cv2.namedWindow('Test',cv2.WINDOW_GUI_NORMAL)
            cv2.setWindowProperty('Test',cv2.WND_PROP_AUTOSIZE,cv2.WINDOW_GUI_NORMAL)
            cv2.resizeWindow('Test', newWidth,newHeight)

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
            cap.release()
            cv2.destroyAllWindows()
            break
