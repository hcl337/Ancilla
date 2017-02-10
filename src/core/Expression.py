from __future__ import division

import logging
import json
import time
import os
import copy
from threading import Timer, Thread

logger = logging.getLogger(__name__)

if 'Linux' in os.uname()[0]:
    import Adafruit_PCA9685
    isRaspberryPi = True
else:
    isRaspberryPi = False

class Expression:
    '''
    The main class which represents the output of the system

    '''

    isEnabled = False

    def __init__(self, AC3):
    	logger.info("Creating Expression...")

    def enable( self ):
    	isEnabled = True

    def disable( self ):
    	isEnabled = False

    