import cv2 as cv
import time
from threading import Thread
import logging

logger = logging.getLogger(__name__)

class Eyes( ):
    '''
    The Eyes class accesses the cameras and sets them up with callbacks
    so that people can access teh data from them
    '''

    focusCamera = None
    environmentCamera = None

    latestFocusFrame = None
    latestEnvironmentFrame = None

    _isEnabled = False

    FRAME_RATE = 5

    focusListeners = []
    environmentListeners = []


    def __init__ ( self ):

        try:
            self.environmentCamera = cv.VideoCapture(0)
        except Exception as e:
            logger.error("Can not connect to environment camera: " + str(e))

        try:
            self.focusCamera = cv.VideoCapture(1)
            print self.focusCamera
        except Exception as e:
            logger.error("Can not connect to focus camera: " + str(e))



    def enable( self ):
        '''
        Starts a listening thread for the cameras which were found
        on initialization.
        '''

        if self._isEnabled:
            return

        self._isEnabled = True

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

        logger.info("Enabled Eyes")



    def disable( self ):
        '''
        Disables the cameras and waits enough time that the loop for
        updating them will have completed
        '''
        self._isEnabled = False

        # Wait until the thread is fully done before returning
        time.sleep( 1 / FRAME_RATE + 0.1 )

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



    def getLatestFocusFrame( self ):

        if not self.isEnabled( ):
            return None
        return self.latestFocusFrame



    def getLatestEnvironmentFrame( self ):

        if not self.isEnabled( ):
            return None
        return self.latestEnvironmentFrame



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

                logger.debug("Loop for Environment camera")
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
                if( sleepAmount < 0 ):
                    raise Exception( "Camera update loop took more time to update than the allowed interval: " + str(interval) + " " +str(sleepAmount) + " " )
                    self.disable()
    
                time.sleep( sleepAmount )
        except Exception as e:
            self._isEnabled = False
            logger.error(e)


    def __updateFocusLoop( self ):
        '''
        '''
        print("Update loop")

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
            self.updateLoopActive = None
            logger.error(e)


    def __updateFocusFrame( self ):

        if self.focusCamera != None:
            ret, fullFrame = self.focusCamera.read()
            self.latestFocusFrame = fullFrame

            #cv.imshow('Focus',self.latestFocusFrame)

        for fn in self.focusListeners:
            fn(phrase)     

    def __updateEnvironmentFrame( self ):

        if self.environmentCamera != None:
            ret, fullFrame = self.environmentCamera.read()
            self.latestEnvironmentFrame = fullFrame

            print(str(self.latestEnvironmentFrame.shape))

        for fn in self.environmentListeners:
            fn(phrase)     


logging.basicConfig(level=logging.DEBUG)
eyes = Eyes( )
eyes.enable( )

startTime = time.time()
while time.time() - startTime < 10:
    time.sleep(1/5)
    if eyes.getLatestEnvironmentFrame() != None:
        cv.imshow('Environment',eyes.getLatestEnvironmentFrame())
        cv.waitKey(30)

cv.destroyAllWindows()