import os
import time
import logging
import copy
import json
from threading import Thread

import cv2 as cv
from vision.FaceDetector import FaceDetector
from vision.FaceRecognizer import FaceRecognizer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Vision( ):
    '''
    The Eyes class accesses the cameras and sets them up with callbacks
    so that people can access teh data from them
    '''

    focusCamera = None
    environmentCamera = None

    # Store the latest frames so that other people can request them
    latestFocusFrame = None
    latestEnvironmentFrame = None

    # Private variable specifying if everythign is working
    _isEnabled = False

    # Output update rate. Because we are on a Raspberry Pi, we can't output
    # at a really high rate and expect to process everything
    FRAME_RATE = 5

    # Store all the functions registered as listeners for us
    focusListeners = []
    environmentListeners = []

    visualObjects = {}

    faceDetector = None
    faceRecognizer = None

    AC3 = None


    def __init__ ( self, AC3 ):
        '''
        Creates and connects to as many capture devices as possible
        '''

        

        self.faceDetector = FaceDetector()
        self.faceRecognizer = FaceRecognizer()
        self.registerEnvironmentFrameListener( self.computeCoreEnvironment )
        self.AC3 = AC3




    def enable( self ):
        '''
        Starts a listening thread for the cameras which were found
        on initialization.
        '''

        if self._isEnabled:
            return

        self._isEnabled = True

        self.environmentCamera = cv.VideoCapture(0)

        if not self.environmentCamera.isOpened( ):
            raise Exception("Could not open environment camera.")

        '''
        self.focusCamera = cv.VideoCapture(0)

        if not self.focusCamera.isOpened( ):
            raise Exception("Could not open focus camera.")
        '''

        if self.focusCamera != None:
            # Create our thread for updating the focus camera
            updateThread = Thread(target=self.__updateFocusLoop)
            updateThread.setDaemon(True)
            updateThread.start()

        if self.environmentCamera != None:
            # Create our thread for updating the environment camera
            updateThread = Thread(target=self.__updateEnvironmentLoop)
            updateThread.setDaemon(True)
            updateThread.start()

        logger.info("Enabled Vision")



    def disable( self ):
        '''
        Disables the cameras and waits enough time that the loop for
        updating them will have completed
        '''
        self._isEnabled = False

        # This may seem like a hack, but basically what it is doing
        # is just waiting for this loop of vision to complete fully
        # so we don't have to worry about partial frames being
        # processed
        time.sleep( 0.5 )

        # Wait until the thread is fully done before returning
        time.sleep( 1 / self.FRAME_RATE + 0.1 )

        if self.focusCamera != None:
            self.focusCamera.release()

        if self.environmentCamera != None:
            self.environmentCamera.release()



    def isEnabled( self ):
        return self._isEnabled



    def registerFocusFrameListener( self, listener ):
        self.focusListeners.append( listener )



    def registerEnvironmentFrameListener( self, listener ):
        self.environmentListeners.append( listener )

    def unregisterEnvironmentFrameListener( self, listener ):
        if listener in self.environmentListeners:
            self.environmentListeners.remove( listener )



    def getLatestFocusFrame( self ):

        if not self.isEnabled( ):
            return None
        return self.latestFocusFrame



    def getLatestEnvironmentFrame( self ):

        if not self.isEnabled( ):
            return None
        return self.latestEnvironmentFrame


    def getVisibleObjects( self ):
        '''
        This is the list of all the objects which are
        visible currently
        '''
        return copy.deepcopy( self.visualObjects )



    def computeCoreEnvironment( self ):

        visualObjects = {}

        img = self.getLatestEnvironmentFrame()

        if img == None or img.shape[0] == 0:
            logger.debug("Skipping analysis. No image yet.")

        ##############################
        # FACE DETECTION
        visualObjects['faces'] = self.faceDetector.detect( img )

        ##############################
        # FACE RECOGNITION
        for f in visualObjects['faces']:
            regionOfInterest = img[f['y']: f['y'] + f['height'], f['x']: f['x'] + f['width']]
            # Try to figure out who this is...
            name = self.faceRecognizer.identifyFace( regionOfInterest )
            #logger.debug("NAME: " + str(name))
            f['name'] = name


        self.visualObjects = visualObjects



    def __updateEnvironmentLoop( self ):
        '''
        '''

        interval = 1.0 / self.FRAME_RATE
        logger.info("Setting environment camera Update Interval to " + str(round(1/interval)) + " hz.")

        logger.debug(self._isEnabled)
        try:
            # Set the PWM update interval based on our parameters
            # If we have stopped this loop then de-activate the cameras before we do anything else
            while( self._isEnabled ):

                #logger.debug("Loop for Environment camera")
                # Calculate the start time so we know how much time has happened before we trigger
                # this again
                startTime = time.time()
                nextUpdate = startTime + interval
    
                # Active the actual work for updating
                self.__updateEnvironmentFrame( )
    
                # It probably took some time to update, so schedule the next update to be minus
                # that time
                sleepAmount = nextUpdate - time.time()
    
                # This is just a protection that should never be triggered. If it takes us
                # waay too long, we need to log it and stop or we will crash the stack
                #if( sleepAmount < -2*interval ):
                #    raise Exception( "Camera update loop took more time to update than the allowed interval: " + str(interval) + " " +str(sleepAmount) + " " )
                #    self.disable()
                if sleepAmount < 0: sleepAmount = 1 / 30

                time.sleep( sleepAmount )
        except Exception as e:
            self._isEnabled = False
            self.AC3.reportFatalError( )




    def __updateFocusLoop( self ):
        '''
        '''
        #print("Update loop")

        interval = 1.0 / self.FRAME_RATE
        logger.info("Setting focus camera Update Interval to " + str(round(1/interval)) + " hz.")

        try:
    
            # If we have stopped this loop then de-activate the cameras before we do anything else
            while( self._isEnabled ):

                # Calculate the start time so we know how much time has happened before we trigger
                # this again
                startTime = time.time()
                nextUpdate = startTime + interval
    
                # Active the actual work for updating
                self.__updateFocusFrame( )
    
                # It probably took some time to update, so schedule the next update to be minus
                # that time
                sleepAmount = nextUpdate - time.time()
    
                # This is just a protection that should never be triggered. If it takes us
                # waay too long, we need to log it and stop or we will crash the stack
                if( sleepAmount < 0 ):
                    raise Exception( "Camera update loop took more time to update than the allowed interval: " + str(interval) + " " +str(sleepAmount) + " " )
                    self.disable()


                time.sleep( sleepAmount )
        except Exception as e:
            self._isEnabled = False
            self.AC3.reportFatalError( )



    def __updateFocusFrame( self ):

        if self.focusCamera != None:
            ret, fullFrame = self.focusCamera.read()
            if (fullFrame != None) and (fullFrame.shape[0] > 0):
                self.latestFocusFrame = fullFrame.copy()
    
                for fn in self.focusListeners:
                    fn()



    def __updateEnvironmentFrame( self ):

        #logger.debug("Updating env frame. Listeners: " + str(len(self.environmentListeners)))

        if self.environmentCamera != None:
            ret, fullFrame = self.environmentCamera.read()
            if (fullFrame != None) and (fullFrame.shape[0] > 0):
                self.latestEnvironmentFrame = fullFrame.copy()

                for fn in self.environmentListeners:
                    fn()


'''
logging.basicConfig(level=logging.DEBUG)
vision = Vision( )
vision.enable( )

startTime = time.time()
while time.time() - startTime < 20:
    time.sleep(1/5)
    if vision.getLatestEnvironmentFrame() != None:
        cv.imshow('Environment',vision.getLatestEnvironmentFrame())
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

vision.disable()
cv.destroyAllWindows()

'''
