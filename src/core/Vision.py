import os
import time
import logging
import copy
import json
import subprocess
from threading import Thread

import cv2 as cv
from vision.FaceDetector import FaceDetector
from vision.FaceRecognizer import FaceRecognizer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

isRaspberryPi = 'Linux' in os.uname()[0]

    
class Vision( ):
    '''
    The Eyes class accesses the cameras and sets them up with callbacks
    so that people can access teh data from them
    '''

    # OpenCV VideoCapture objects
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

    # List of objects which are currently in view as of the last frame
    visualObjects = {}

    faceDetector = None
    faceRecognizer = None

    AC3 = None

    # Update at a max of 5 hz for our data, not 30 hz
    MIN_TIME_FOR_COMPUTING_VISION = 1 / 5


    def __init__ ( self, AC3 ):
        '''
        Creates and connects to as many capture devices as possible
        '''

        self.faceDetector = FaceDetector()
        self.faceRecognizer = FaceRecognizer()
        self.registerEnvironmentFrameListener( self.computeCoreEnvironment )
        self.AC3 = AC3

        self.___environmentCameraFOV = {'x':70, 'y':50}
        self.___focusCameraFOV = {'x':50, 'y':30}

        self.timeOfLastVisualUpdate = time.time()
        self.isComputingCoreEnvironment = False
        
        if isRaspberryPi:
            enablePiCamForOpenCVOnRaspPi()



    def enable( self ):
        '''
        Starts a listening thread for the cameras which were found
        on initialization.
        '''

        if self._isEnabled:
            return

        self._isEnabled = True


        if isRaspberryPi:
            logger.info("Setting up cameras for Raspberry Pi")
            devices = getCameraNamesOnRaspPi()
            
            if len(devices) == 0:
                raise Exception("No cameras found on system")
            elif len(devices) == 1:
                logger.info("\tOne camera found so setting as environment: " + str(devices))
                self.environmentCamera = cv.VideoCapture(devices.keys()[0])
            elif len(devices) > 2:
                raise Exception("Too many cameras found in system: " + str(devices))
            else:
                for i in devices:
                    # We are using a USB camera for the narrow focus one and picam for the higher
                    # width one
                    if 'usb' in  devices[i].lower():
                        logger.info("Focus Camera Found: " + devices[i])
                        self.focusCamera = cv.VideoCapture(i)
                    else:
                        logger.info("Environment Camera Found: " + devices[i])
                        self.environmentCamera = cv.VideoCapture(i)
                
        else:
            logger.info("Setting up cameras for Mac")
            self.environmentCamera = cv.VideoCapture(0)
            self.focusCamera = None
            


        if self.focusCamera != None and self.focusCamera.isOpened():
            
            self.focusCamera.set(cv.cv.CV_CAP_PROP_FPS, Vision.FRAME_RATE )
            # Create our thread for updating the focus camera
            updateThread = Thread(target=self.__updateFocusLoop)
            updateThread.setDaemon(True)
            updateThread.start()
        else:
            logger.warning("No focus camera found")
            self.AC3.speech.say("WARNING: No focus camera found.")
            

        if self.environmentCamera != None and self.environmentCamera.isOpened():

            self.environmentCamera.set(cv.cv.CV_CAP_PROP_FPS, Vision.FRAME_RATE )
            # Create our thread for updating the environment camera
            updateThread = Thread(target=self.__updateEnvironmentLoop)
            updateThread.setDaemon(True)
            updateThread.start()
        else:
            logger.warning("No environment camera found")
            self.AC3.speech.say("Vision disabled. No environment camera found.")

        logger.info("Enabled Vision")



    def disable( self ):
        '''
        Disables the cameras and waits enough time that the loop for
        updating them will have completed
        '''
        self._isEnabled = False

        # Wait until the thread is fully done before returning
        time.sleep( 1 / self.FRAME_RATE + 0.25 )

        if self.focusCamera != None:
            self.focusCamera.release()

        if self.environmentCamera != None:
            self.environmentCamera.release()



    def isEnabled( self ):
        '''
        Returns true if vision is currently enabled with the update
        loop running. If it returns false it is either because the
        system was never enabled or there was an error which made the
        loop cancel
        '''
        return self._isEnabled


    def registerFocusFrameListener( self, listener ):
        '''
        Register a listener method who will be called each time
        a new focus frame is received. It should then call
        AC3.vision.getLatestFocusFrame( ) to get the frame

        '''
        self.focusListeners.append( listener )



    def unRegisterFocusFrameListener( self, listener ):
        '''
        Removes the specified listener method if it is currently
        registered or does nothing if it is not.
        
        '''
        self.focusListeners.remove( listener )



    def registerEnvironmentFrameListener( self, listener ):
        '''
        Register a listener method who will be called each time
        a new environment frame is received. It should then call
        AC3.vision.getLatestEnvironmentFrame( ) to get the frame
        
        '''
        self.environmentListeners.append( listener )



    def unRegisterEnvironmentFrameListener( self, listener ):
        '''
        Removes the specified listener method if it is currently
        registered or does nothing if it is not.

        '''
        if listener in self.environmentListeners:
            self.environmentListeners.remove( listener )



    def getLatestFocusFrame( self ):
        '''
        Returns a reference to the latest focus frame. Note that
        this is the real frame so please do not mutate it.

        If there is no frame yet or it is not enabled, then None
        is returned. This should always be checked before use.

        '''
        if not self.isEnabled( ):
            return None
        return self.latestFocusFrame



    def getLatestEnvironmentFrame( self ):
        '''
        Returns a reference to the latest environment frame. Note that
        this is the real frame so please do not mutate it.

        If there is no frame yet or it is not enabled, then None
        is returned. This should always be checked before use.
        
        '''

        if not self.isEnabled( ):
            return None
        return self.latestEnvironmentFrame


    def getEnvironmentCameraFOV( self ):
        '''
        returns a dictionary of x and y field of view (angle width)
        for the specific hardware
        '''
        return self.___environmentCameraFOV



    def getFocusCameraFOV( self ):
        '''
        returns a dictionary of x and y field of view (angle width)
        for the specific hardware
        '''
        return self.___focusCameraFOV



    def getVisibleObjects( self ):
        '''
        This is the list of all the objects which are
        visible currently and their bounds.
        '''
        return copy.deepcopy( self.visualObjects )



    def computeCoreEnvironment( self ):
        '''
        This computes faces, recognition and other visual elements
        on each frame it is triggered on. It is a heavy duty method

        '''

        if self.isComputingCoreEnvironment:
            logger.debug("computingCoreEnvironment: still computing last so skipping: " + str(round(time.time() - self.timeOfLastVisualUpdate, 2)) + ' sec')
            return

        # If we let it go too fast, we will run out of processor on the machine
        if time.time() - self.timeOfLastVisualUpdate < Vision.MIN_TIME_FOR_COMPUTING_VISION:
            logger.debug("computingCoreEnvironment: too fast so skipping")
            return

        self.isComputingCoreEnvironment = True
        self.timeOfLastVisualUpdate = time.time()

        visualObjects = {}

        img = self.getLatestEnvironmentFrame()

        if img is None or img.shape[0] == 0:
            logger.debug("Skipping analysis. No image yet.")
            return

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

        self.isComputingCoreEnvironment = False

        #logger.debug("computeCoreEnvironment: execution time: " + str(round(time.time() - self.timeOfLastVisualUpdate, 2) ) + ' sec.')



    def __updateEnvironmentLoop( self ):
        '''
        Loop which waits for each frame and updates everything
        when the next frame comes in
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
                
                #logger.debug("EndTime: " + str(time.time() - startTime))
    
                # It probably took some time to update, so schedule the next update to be minus
                # that time
                #sleepAmount = nextUpdate - time.time()
    
                # This is just a protection that should never be triggered. If it takes us
                # waay too long, we need to log it and stop or we will crash the stack
                #if( sleepAmount < -2*interval ):
                #    raise Exception( "Camera update loop took more time to update than the allowed interval: " + str(interval) + " " +str(sleepAmount) + " " )
                #    self.disable()
                #if sleepAmount < 0: sleepAmount = 1 / 30

                #time.sleep( sleepAmount )
        except Exception as e:
            self._isEnabled = False
            self.AC3.reportFatalError( )



    def __updateFocusLoop( self ):
        '''
        Loop which waits for each frame and updates everything
        when the next frame comes in

        '''
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
                #sleepAmount = nextUpdate - time.time()
    
                # This is just a protection that should never be triggered. If it takes us
                # waay too long, we need to log it and stop or we will crash the stack
                #if( sleepAmount < 0 ):
                #    raise Exception( "Camera update loop took more time to update than the allowed interval: " + str(interval) + " " +str(sleepAmount) + " " )
                #    self.disable()
                #if sleepAmount < 0: sleepAmount = 1 / 30


                #time.sleep( sleepAmount )
        except Exception as e:
            self._isEnabled = False
            self.AC3.reportFatalError( )




    def __updateFocusFrame( self ):
        '''
        Calls all the listeners on a copy of the latest frame

        '''
        if self.focusCamera != None:
            ret, fullFrame = self.focusCamera.read()
            if (fullFrame is not None) and (fullFrame.shape[0] > 0):
                self.latestFocusFrame = fullFrame.copy()
    
                for fn in self.focusListeners:
                    # We don't want our callbacks to get stuck where
                    # things can get backed up so need to call them
                    # as a thread instead. It might be better to do it
                    # as a thread pool, but not sure...

                    # Create our thread
                    updateThread = Thread(target=fn)
                    # Make sure it dies if the whole app dies
                    updateThread.setDaemon(True)
                    # Need to actually start it running where it calls the update function
                    updateThread.start()



    def __updateEnvironmentFrame( self ):
        '''
        Calls all the listeners on a copy of the latest frame
        
        '''

        if self.environmentCamera != None:
            ret, fullFrame = self.environmentCamera.read()
            if (fullFrame is not None) and (fullFrame.shape[0] > 0):
                self.latestEnvironmentFrame = fullFrame.copy()

                for fn in self.environmentListeners:
                    # We don't want our callbacks to get stuck where
                    # things can get backed up so need to call them
                    # as a thread instead. It might be better to do it
                    # as a thread pool, but not sure...

                    # Create our thread
                    updateThread = Thread(target=fn)
                    # Make sure it dies if the whole app dies
                    updateThread.setDaemon(True)
                    # Need to actually start it running where it calls the update function
                    updateThread.start()



def enablePiCamForOpenCVOnRaspPi( ):
    '''
    The raspberry pi camera is not visible to our system so need to do a hack
    to add it. Calling this makes it happen.
    '''

    try:
        lines = subprocess.check_output('sudo modprobe bcm2835-v4l2'.split() )
        logger.debug("Enabling raspberry pi camera with ModProbe: " + str(lines))
    except subprocess.CalledProcessError as e:
        raise Exception("Could not set up raspberry pi camera with modprobe: " + str(e))



def getCameraNamesOnRaspPi( ):
    '''
    Lists out all of the video devices and parses their names out. Check for USB, etc.
    
    Returns a dictionary from device index to human name
    '''
    
    lines = subprocess.Popen('v4l2-ctl --list-devices'.split(), stdout=subprocess.PIPE).communicate()[0]

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
        
    return devices
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
