import cv2
import numpy as np
import time

dev = 0

cap = cv2.VideoCapture(dev, cv2.CAP_ANY)

cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)

width = 1920
height = 1080
avg = False
l = []

cv2.namedWindow('Thermal')

if not cap.isOpened():
    print("Error establishing connection")

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        cv2.imshow('Thermal',frame)

        keypress = cv2.waitKey(1)
        if keypress == ord('q'):
            break
        if keypress == ord('s'):
            l = []
            avg = True
        
        if avg and len(l) < 10:
            l.append(frame.copy())
            time.sleep(1)
        if len(l) > 10:
            avg = False

av = np.mean(l,axis=0)
avi = np.round(av).astype(np.uint8)
cv2.imshow('Thermal',avi)
cap.release()
cv2.destroyAllWindows()

%matplotlib inline 
from matplotlib import pyplot as plt
plt.imshow(avi)
plt.show()

col = []
for i in range(avi.shape[2]):
    col.append(avi[:,:,i].copy())

col_means = []
col_stds = []
for i in col:
    col_means.append(int(np.mean(i)))
    col_stds.append(np.std(i))
