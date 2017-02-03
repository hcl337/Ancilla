from __future__ import division

import logging
import json
import time
import os
import copy
from threading import Timer, Thread

logger = logging.getLogger(__name__)

if 'raspberrypi' in os.uname()[1]:
    isRaspberryPi = True
else:
    isRaspberryPi = False

class Vision:
    '''
    The main class which represents camera-based elements

    '''

    isEnabled = False

    def __init__(self):
    	logger.info("Creating Vision...")



    def enable( self ):
    	isEnabled = True



    def disable( self ):
    	isEnabled = False


    def getLatestPeripheralImage( ):
        '''
        Returns the latest image received by the wide angle camera on the base
        '''
        pass


    def getLastestFocusImage( ):
        '''
        Returns the latest image received by the narrow angle camera on the robot
        '''


    def __ProcessPeripheralFrame( image ):
        pass


    def __ProcessFocusFrame( image ):
        pass




