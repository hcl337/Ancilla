import time
import sys
import copy
import logging
logger = logging.getLogger(__name__)


# Only let us remember a set of things
MAX_HEARING_MEMORY = 10

class Reasoning:

    AC3 = None

    __memory = {
        "hearing": [ ],
        "vision" : {}
    }



    def __init__(self, AC3):
        self.AC3 = AC3
        self.AC3.hearing.registerListener( self.heardPhrase )


    def enable( self ):
        pass


    def disable( self ):
        pass



    def getMemory( self ):
        return copy.deepcopy( self.__memory )



    def heardPhrase( self, phrase ):

        self.__memory['hearing'].append(phrase)
        if len(self.__memory['hearing']) > MAX_HEARING_MEMORY:
            self.__memory['hearing'].pop(0)

        logger.debug("Heard this phrase: " + phrase)

        phrase = phrase.lower()

        if not ( 'ac3' in phrase):
            logger.debug("Was not talking to me...: " + str( phrase))
            return

        logger.debug("Was talking to me...: " + str( phrase))
        #self.AC3.speech.say("You said " + phrase)

        if 'what is your name' in phrase:
            self.AC3.speech.say( "My name is AC-3. Nice to meet you.")
        elif 'thank you' in phrase:
            self.AC3.speech.say( "You are welcome!")
        elif 'good night' in phrase:
            self.AC3.speech.say( "Sleep well. I will be waiting for you to return.")
        elif 'look left' in phrase:
            self.AC3.movement.setServoAngle('neck_rotate', -60, 60)
        elif 'look right' in phrase:
            self.AC3.movement.setServoAngle('neck_rotate', 60, 60)
        elif 'look up' in phrase:
            self.AC3.movement.setServoAngle('head_tilt', 20, 60)
        elif 'look down' in phrase:
            self.AC3.movement.setServoAngle('head_tilt', -20, 60)
        elif ' do you see' in phrase or 'do you see anyone' in phrase:
            objs = self.AC3.vision.getVisibleObjects( )['faces']

            s = "I see " + str(len(objs)) + " faces."

            if len(objs) == 1:
                s = s.replace( "faces.", "face.")

            for o in objs:
                if o['name'] != None:
                    s += "I think I see " + o['name'] +".\n\n"
                else:
                    s += "I don't know who it is.\n\n"

                if o['orientation'] == "frontal":
                    s += "They are looking at me.\n\n"
                else:
                    s += "They are not looking at me.\n\n"
            self.AC3.speech.say(s)
        elif 'good morning' in phrase:
            self.AC3.speech.say( "It is a good morning!")
        elif 'wife' in phrase:
            self.AC3.speech.say( "Courtney is the best wife in the world!")
        elif 'court' in phrase:
            self.AC3.speech.say( "I like courtney.")
        elif 'hans' in phrase:
            self.AC3.speech.say( "Hans made me.")
        elif 'jim' in phrase:
            self.AC3.speech.say( "Hi Jim. I heard you like shocktop beer.")
        elif 'charlotte' in phrase:
            self.AC3.speech.say( "I can't wait to meet charlotte.")
        elif 'emmaline' in phrase:
            self.AC3.speech.say( "I can't wait to meet emmaline.")
        elif 'lilibeth' in phrase:
            self.AC3.speech.say( "I can't wait to meet lilibeth.")
        elif 'hello' in phrase:
            self.AC3.speech.say( "Hi there! It is nice to talk to a human.")
        elif 'ac3 shut down' in phrase:
            self.AC3.speech.say( "Ask me nicely.")
        elif 'ac3 please shut down' in phrase:
            self.AC3.speech.say( "Initiating shutdown.")
            time.sleep(3)
            self.AC3.shutdown()
        else:
        	self.AC3.speech.say( "uh huh.")

