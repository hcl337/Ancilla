import os, json
import subprocess
from hearing import updatesphinxvocabulary
import logging
import time
import signal
import atexit
import psutil
from threading import Timer, Thread

logger = logging.getLogger(__name__)


HEARING_FILE_ROOT = os.path.normpath(os.path.dirname(__file__) )
vocab_path = HEARING_FILE_ROOT + "/hearing/sphinx_vocabulary"

# This is a delay so that we don't "hear" a sentence that the
# robot said. We have to hear a sentence which ended more than 3 seconds
# after we stop speaking
MIN_TIME_AFTER_I_SPEAK_TO_LISTEN = 3


class Hearing( ):



    def __init__( self, AC3 ):

        logger.info("Updating vocabulary files...")

        # Update our vocabulary with the latest version if possible
        updatesphinxvocabulary.updateVocabulary()

        self.AC3 = AC3
        self.hearingProcess = None
        self.callbacks = []

        # Register so if we exit for any reason, this will disable the
        # thread and try to guarantee an exit
        atexit.register(self.disable)

        # If we accidentally leave open pocket sphinx we need to
        # close it so we don't keep multiple around.
        PROCNAME = "pocketsphinx_continuous"
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME: proc.kill()




    def isEnabled( self ):
        return self.hearingProcess != None and self.hearingProcess.poll() == None



    def enable( self ):

        logger.info("Enabling SphinxHearing")
        # Create our thread
        updateThread = Thread(target=self.__loop)
        # Make sure it dies if the whole app dies
        updateThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        updateThread.start()



    def disable( self ):

        if self.hearingProcess != None:
            #self.hearingProcess.kill()
            pid = self.hearingProcess.pid
            self.hearingProcess = None
            
            if self.__checkIfProcessExists( pid ):
                logger.debug("PID for hearing process to shut down: " + str( pid ))
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                time.sleep( 3 )


    def __checkIfProcessExists( self, pid ):
        try:
            # This doesn't actually kill the process. It just
            # tests if it is there.
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True
        
        
        
    def registerListener( self, listener ):
        self.callbacks.append(listener)



    def __loop( self ):

        try:
            logger.info("Starting speech loop")

            hmmLocation = "/usr/local/share/pocketsphinx/model/en-us/en-us"
            lmLocation = vocab_path + "/vocab.lm"
            dictLocation = vocab_path + "/vocab.dic"

            command = "pocketsphinx_continuous -hmm " + \
                hmmLocation + " -lm " + lmLocation + " -dict " + \
                dictLocation + " -samprate 16000/8000/4000 -inmic yes -logfn /dev/null"

            logger.debug("Command for sphinx: " + command )

            command = command.split(" ")

            # Kick off the actual process so we can wait
            self.hearingProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

            # Grab stdout line by line as it becomes available.  This will loop until
            # p terminates.
            while self.hearingProcess and self.hearingProcess.poll() == None:

                # This waits for each line to come in
                phrase = self.hearingProcess.stdout.readline() # This blocks until it receives a newline.

                # We get a lot of garbage back from the system so don't report it
                phrase = phrase.strip()

                if 'Error opening audio device' in phrase:
                    raise Exception("Could not connect to microphone: " + phrase )
                
                if phrase.startswith("INFO: ") or len( phrase ) == 0:
                    continue

                # We have a problem that we could be listening to ourselves. We don't want to do that!
                # Therefore there is a gap between when it speaks and when we will say we heard something
                if time.time() - self.AC3.speech.timeSinceLastSpoke() < MIN_TIME_AFTER_I_SPEAK_TO_LISTEN:
                    #logger.info("Not reporting words because AC3 just spoke: " + str(self.AC3.speech.timeSinceLastSpoke()))
                    continue

                # Send the event out to all of our listeners
                for fn in self.callbacks:
                    #fn(phrase)

                    # We don't want our callbacks to get stuck where
                    # things can get backed up so need to call them
                    # as a thread instead. It might be better to do it
                    # as a thread pool, but not sure...

                    logger.debug(">>>>> " + phrase)
                    # Create our thread
                    updateThread = Thread(target=fn,  args=[phrase])
                    # Make sure it dies if the whole app dies
                    updateThread.setDaemon(True)
                    # Need to actually start it running where it calls the update function
                    updateThread.start()

            # When the subprocess terminates there might be unconsumed output
            # that still needs to be processed.
            if self.hearingProcess != None:
                self.hearingProcess.stdout.read()
            
                # Also see if we had any errors. This could be the reason we shut down so raise an exception
                # if we saw one
                error = self.hearingProcess.stderr.read( )
                if len(error) != 0:
                    if 'Error opening audio device' in error:
                        self.AC3.speech.say("Hearing disabled. No microphone found.")
                        #raise Exception("Hearing process could not find a microphone")
                    else:
                        raise Exception("Hearing process crashed. Reason specified is " + str(error) )
            
        except:
            self.AC3.reportFatalError()
