import os, os.path
import sys
import logging

import scipy.misc
import cv2

logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
FACE_CASCADE_PATH = os.path.join(dir_path, "resources/haarcascade_frontalface_default.xml")
FACE_PROFILE_CASCADE_PATH = os.path.join(dir_path, 'resources/haarcascade_profileface.xml')

logger.debug("Haar Cascade Path: " + FACE_CASCADE_PATH)


if not os.path.isfile(FACE_CASCADE_PATH): raise Exception("Can' not find frontal haarcascade! Dir: " + dir_path + " File: " + FACE_CASCADE_PATH )
if not os.path.isfile(FACE_PROFILE_CASCADE_PATH): raise Exception("Can' not find profile haarcascade! Dir: " + dir_path + " File: " + FACE_PROFILE_CASCADE_PATH )

# To speed this up, we are going to run face detection on a smaller version of the frame
# Number between 0 and 1. If the size is 0.25, then it will resize the image to be
# 1/4 the previous size. This is acceptable because the Haar classifier does not need
# all the detail of the face. It only needs the shadow and light areas.
SCALE = .25

# This is the minimum face size we will look for. If it is smaller than this, we will decide we
# can't see it. Number from 0.0 to 1.0 but should usually be smaller than the expected size
# of a face that exists within the frame. If the lens is wide or people are far away then
# it needs to be further away
MIN_FACE_FRAME_PERCENT = 0.1

class FaceDetector( ):

    # Store the detector Haar cascades for frontal and profile faces
    faceCascade = None
    profileFaceCascade = None

    def __init__( self ):
        self.faceCascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
        self.profileFaceCascade = cv2.CascadeClassifier(FACE_PROFILE_CASCADE_PATH)



    def detect( self, frame ):
        '''
        Returns an array of dictionaries where each element is a list of 
            'x': [0..frame width]
            'y': [0..frame height]
            'width': [0..height] - It detects a square bounding box so is limited
                by the smallest dimension which is height. It is also limited by
                the minimum frame percent. From upper left corner 'x' position.
            'height': [0..height] - Height from upper left corner 'y' position.
            'orientation': ['frontal', 'profile'] - the type of detector which
                found this face.
        '''

        # Resize the frame to be smaller
        smallFrame = cv2.resize(frame,None,fx=SCALE, fy=SCALE, interpolation = cv2.INTER_LINEAR)

        # Turn to greyscale so VIOLA JONES can work on it
        gray = cv2.cvtColor(smallFrame, cv2.COLOR_BGR2GRAY)

        # Calculate the smallest size to look for faces
        minSize = int(smallFrame.shape[1] * MIN_FACE_FRAME_PERCENT)

        # Find frontal faces
        facesFound = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(minSize, minSize),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        # Now see if we have any side "profile" faces we can find
        # if people are looking away to help us better understand
        facesProfiles = self.profileFaceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        # Now turn them into JSON and rescale them to the full size
        faceList = []
        for (x, y, w, h) in facesFound:
            faceList.append( {'x': int(x/SCALE), 'y': int(y/SCALE), 'width': int(w/SCALE), 'height': int(h/SCALE), 'orientation':'frontal'} )
        for (x, y, w, h) in facesProfiles:
            faceList.append( {'x': int(x/SCALE), 'y': int(y/SCALE), 'width': int(w/SCALE), 'height': int(h/SCALE), 'orientation':'profile'} )

        return faceList

