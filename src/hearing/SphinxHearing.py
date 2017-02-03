import os, json
import subprocess
import updatesphinxvocabulary
import logging
import time
import signal
from threading import Timer, Thread

logger = logging.getLogger(__name__)


HEARING_FILE_ROOT = os.path.normpath(os.path.dirname(__file__) )

vocab_path = HEARING_FILE_ROOT + "/sphinx_vocabulary"

MIN_TIME_AFTER_I_SPEAK_TO_LISTEN = 3


class SphinxHearing( ):

    hearingProcess = None
    callbacks = []
    speech = None


    def __init__( self, speech ):

        logger.info("Updating vocabulary files...")

        # Update our vocabulary with the latest version if possible
        updatesphinxvocabulary.updateVocabulary()

        self.speech = speech



    def isEnabled( self ):
        return self.hearingProcess != None and self.hearingProcess.poll()



    def enable( self ):

        logger.info("Enabling SphinxHearing")
        # Create our thread
        updateThread = Thread(target=self.__loop)
        # Make sure it dies if the whole app dies
        updateThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        updateThread.start()



    def disable( self ):

        if self.hearingProcess:
            #self.hearingProcess.kill()
            os.killpg(os.getpgid(self.hearingProcess.pid), signal.SIGTERM)
            self.hearingProcess = None



    def registerListener( self, listener ):
        self.callbacks.append(listener)



    def __loop( self ):

        logger.info("Starting speech loop")

        hmmLocation = "/usr/local/share/pocketsphinx/model/en-us/en-us"
        lmLocation = vocab_path + "/vocab.lm"
        dictLocation = vocab_path + "/vocab.dic"

        command = "pocketsphinx_continuous -hmm " + \
            hmmLocation + " -lm " + lmLocation + " -dict " + \
            dictLocation + " -samprate 16000/8000/4000 -inmic yes -logfn /dev/null"

        command = command.split(" ")

        self.hearingProcess = subprocess.Popen(command, stdout=subprocess.PIPE, preexec_fn=os.setsid)
        # Grab stdout line by line as it becomes available.  This will loop until 
        # p terminates.
        while self.hearingProcess and self.hearingProcess.poll():

            # This waits for each line to come in
            phrase = self.hearingProcess.stdout.readline() # This blocks until it receives a newline.

            # We get a lot of garbage back from the system so don't 
            phrase = phrase.strip()
            if phrase.startswith("INFO: ") or len( phrase ) == 0:
                continue

            # We have a problem that we could be listening to our selves. We don't want to do that! 
            # Therefore there is a gap between when it speaks and when we will say we heard something
            if time.time() - self.speech.timeSinceLastSpoke() < MIN_TIME_AFTER_I_SPEAK_TO_LISTEN:
                logger.info("Not reporting words because AC3 just spoke: " + str(self.speech.timeSinceLastSpoke()))
                continue

            # Send the event out to all of our listeners
            for fn in self.callbacks:
                fn(phrase)     

        # When the subprocess terminates there might be unconsumed output 
        # that still needs to be processed.
        self.hearingProcess.stdout.read()        

