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

    isEnabled = False
    currentlySpeaking = False

    # This will hold all of our phrases so they are said in order
    phraseQueue = Queue()

    # This holds the reference to our speech engine for Mac, Raspberry Pi, etc
    engine = None


    def __init__(self):
    	logger.info("Creating Speech...")

        if isRaspberryPi:
            self.engine = RaspberryPiSpeech()
        else:
            self.engine = MacSpeech()



    def enable( self ):

        logger.info( "Enabling speech")

        if self.isEnabled:
            raise Exception("Speeking is already enabled")

        self.isEnabled = True

        speechThread = Thread(target=self.__speechLoop)
        # Make sure it dies if the whole app dies
        speechThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        speechThread.start()



    def disable( self ):
    	self.isEnabled = False



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

        while self.isEnabled:

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
                logger.error("Exception in Speech loop: " + str(e) )
                logger.info("Speech loop exiting")
                break

