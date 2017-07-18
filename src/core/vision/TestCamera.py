
from picamera import PiCamera
from time import sleep

'''
camera = PiCamera()

camera.framerate = 10
#camera.resolution = (1920,1080)
camera.start_preview()
sleep(1)
camera.stop_preview()


import cv2 as cv
import os
environmentCamera = cv.VideoCapture(0)
#print( environmentCamera.isOpened( ) )


environmentCamera = cv.VideoCapture(1)
#print( environmentCamera.isOpened( ) )
'''
import subprocess

lines = subprocess.Popen('v4l2-ctl --list-devices'.split(), stdout=subprocess.PIPE).communicate()[0]

print(lines)
print("----")
lines=lines.split('\n')
lines.reverse()

devices = {}
deviceID = None
name = None

for l in lines:
    
    # Some lines have tabs in them
    l = l.strip()

    # Remove the empty lines
    if len(l) == 0:
        continue

    # The first line is the ID of the device. Strip it out
    if '/dev/video' in l:
        print("Found video device: " + l)
        # If we have an old device, write it away as it is done
        if deviceID != None:
            devices[deviceID] = name
        # Extract out the ID of this device to store
        deviceID = int(l.replace('/dev/video',''))
        # Reset the name
        name = ''
    # We got a sub-line for this device with name details
    else:
        name = name + " " + l

# Once we have looped through all of them, we need toremember the final one
if deviceID != None:
    devices[deviceID] = name
         
        
    

    
print( devices )

'''
try:
    lines = subprocess.check_output('sudo modprobe bcm2835-v4l2'.split() )#, stdout=subprocess.PIPE,  stderr=subprocess.PIPE).communicate()[0]
except subprocess.CalledProcessError as e:
    raise Exception("Could not set up raspberry pi camera with modprobe: " + str(e))
print("Enabling raspberry pi camera with ModProbe: " + str(lines))

'''