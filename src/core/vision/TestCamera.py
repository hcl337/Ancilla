'''
from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 180
camera.framerate = 10
camera.resolution = (1920,1080)
camera.start_preview()
sleep(30)
camera.stop_preview()

'''
import cv2 as cv
environmentCamera = cv.VideoCapture(0)

print( environmentCamera.isOpened( ) )
