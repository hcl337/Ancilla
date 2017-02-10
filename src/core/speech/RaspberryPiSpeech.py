import time
import sys
import os


class RaspberryPiSpeech:

    def __init__(self):
        pass


    def sayAndWait( self, phrase ):
        print("Should say: " + phrase)
        #print "flite"
        #os.popen('flite -t "' + phrase + '"').read()
        #print "festival"
        #os.popen('echo "speech" | festival --tts').read()
        #print "espeak"
        # NOTE: Adding 2>/dev/null to the end hides a set of error messages
        # which don't seem to matter about the ALSA pulse sound stuff
        os.system('espeak -ven+f3 -k5 "' + phrase + '" 2>/dev/null' )
        
