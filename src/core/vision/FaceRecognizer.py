import os
import json
import cv2 as cv

import logging
logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
recogPath = os.path.join(dir_path, "resources/recognizedfaces.xml")
recogDescPath = os.path.join(dir_path, "resources/recognizedfacesNames.json")

class FaceRecognizer( ):

    alg = None
    faceRecognitionNameArray = []

    def __init__( self ):
        # Set up the face recognition
        if not os.path.isfile(recogPath):
            raise Exception("Can' not find face recognizer descriptor! File: " + recogPath )

        if not os.path.isfile(recogDescPath):
            raise Exception("Can' not find face recognizer descriptor! File: " + recogPath )

        # Load the face recognizer
        self.alg = cv.face.createLBPHFaceRecognizer()
        self.alg.load(recogPath)

        # Load the file which correlates the index of the face to the name
        with open( recogDescPath ) as f:
            self.faceRecognitionNameArray = json.loads(f.read())



    def identifyFace( self, regionOfInterest):

        if regionOfInterest is None or regionOfInterest.shape[0] == 0:
            raise Exception("Empty region of interest sent to Face Recognizer.")

        gray = cv.cvtColor(regionOfInterest, cv.COLOR_BGR2GRAY)

        result = cv.face.MinDistancePredictCollector( )
        self.alg.predict(gray)
        nbr_predicted = result.getLabel()
        conf = result.getDist()
        
        # If we don't have concidence, don't tell us who it is... we don't know
        if conf > 40:
            return None

        name = self.__nameFromIndex( nbr_predicted )

        return name



    def __indexFromName( self, name ):
        name = name.lower()

        if not( name in self.faceRecognitionNameArray):
            self.faceRecognitionNameArray.append( name )
        i = 0
        for n in self.faceRecognitionNameArray:
            if n == name:
                return i
            i+=1
        raise Exception("Requested indexFromName not found: " + name)



    def __nameFromIndex( self, index ):
        if index < 0 or index > len(self.faceRecognitionNameArray):
            raise Exception("Requested nameFromIndex not found: " + index)
        return self.faceRecognitionNameArray[index]


