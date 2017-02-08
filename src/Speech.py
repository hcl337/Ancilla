from __future__ import division

import logging
import json
import time
import os
import copy
from Queue import Queue
from threading import Timer, Thread

logger = logging.getLogger(__name__)

print os.uname()[1]
if 'raspberrypi' in os.uname()[1]:
    from speech.RaspberryPiSpeech import RaspberryPiSpeech
    isRaspberryPi = True
else:
    from speech.MacSpeech import MacSpeech
    isRaspberryPi = False


class Speech:
    '''
    The main class which represents speech. It is different on Mac, Raspberry Pi,
    etc so subclassing to be effective

    '''

    __isEnabled = False
    currentlySpeaking = False

    # This will hold all of our phrases so they are said in order
    phraseQueue = Queue()

    # This holds the reference to our speech engine for Mac, Raspberry Pi, etc
    engine = None

    AC3 = None
    
    def __init__(self, AC3):
    	logger.info("Creating Speech...")

        self.AC3 = AC3

        if isRaspberryPi:
            self.engine = RaspberryPiSpeech()
        else:
            self.engine = MacSpeech()



    def enable( self ):

        logger.info( "Enabling speech")

        if self.__isEnabled:
            raise Exception("Speeking is already enabled")

        self.__isEnabled = True

        speechThread = Thread(target=self.__speechLoop)
        # Make sure it dies if the whole app dies
        speechThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        speechThread.start()



    def disable( self ):
        self.__isEnabled = False


    def isEnabled( self ):
        return self.__isEnabled



    def say( self, words ):
        logger.debug( "Adding sentence to queue: " + words)
        # Create our thread
        self.phraseQueue.put( words )



    def isTalking( self ):
        return self.phraseQueue.qsize() > 0 or self.currentlySpeaking



    def timeSinceLastSpoke( self ):
        if self.isTalking():
            return 0

        return round( time.time() - self.lastFinishedTalking, 2)


    lastFinishedTalking = time.time()

    def __speechLoop( self ):

        while self.__isEnabled:

            try:
                
                # While there is nothing, just sleep
                if  self.phraseQueue.qsize() == 0:
                    time.sleep(0.25)
                    continue

                self.currentlySpeaking = True
    
                phrase = self.phraseQueue.get( 0 )
    
                logger.debug( "Saying Sentence from Queue: " + phrase)
    
                self.engine.sayAndWait(phrase)
    
                logger.debug("Completed phrase: " + phrase )

                self.currentlySpeaking = False

                # Record when we end so we know how long it has been
                self.lastFinishedTalking = time.time()

                # Add in a human wait inbetween ideas
                #time.sleep( 0.2)
            except Exception as e:
                self._isEnabled = False
                self.AC3.reportFatalError( )            

