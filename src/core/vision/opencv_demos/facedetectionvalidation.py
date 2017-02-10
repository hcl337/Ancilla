import cv2 as cv
import sys
import os, inspect
import scipy.misc
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Faces import Faces

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

cascPath = "../resources/haarcascade_frontalface_default.xml"
eye_cascade = cv.CascadeClassifier("../resources/haarcascade_eye.xml")

faceCascade = cv.CascadeClassifier(cascPath)

video_capture = cv.VideoCapture(0)

div = 0.25

faw = False

faceCalculation = Faces( )

while True:
    # Capture frame-by-frame
    ret, fullFrame = video_capture.read()


    if faw:
        frame = fullFrame
        #frame = cv.resize(fullFrame, (fullFrame.shape[1]/div, fullFrame.shape[0]/div))

        frame = cv.resize(fullFrame,None,fx=div, fy=div, interpolation = cv.INTER_LINEAR)

        print("Full: " + str(fullFrame.shape))
        print("Small: " + str(frame.shape))

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        
        rawFaces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25),
            flags=cv.cv.CV_HAAR_SCALE_IMAGE
        )
        faces = []
        for (x, y, w, h ) in rawFaces:
            faces.append((int(x/div), int(y/div), int(w/div), int(h/div)))
    else:
        rawFaces = faceCalculation.detect( fullFrame )

        faces = []
        # Draw a rectangle around the faces
        for f in rawFaces:
            x = f['x']
            y = f['y']
            w = f['width']
            h = f['height']
            logger.debug("Face: " + str((x, y, w, h)))
            faces.append( (x, y, w, h))

    for face in faces:
        logger.debug("Drawing face: " +str(face))
        cv.rectangle(fullFrame, (face[0],face[1]),(face[0]+face[2],face[1]+face[3]), (0, 255, 0), 4)

       

    # Display the resulting frame
    cv.imshow('Video', fullFrame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv.destroyAllWindows()