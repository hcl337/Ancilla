import time
import sys
import copy
import logging
from random import randint
from threading import Thread
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

    def programmedMoveRobot( self ):
        # Create our thread
        updateThread = Thread(target=self.__programmedMoveRobot)
        # Make sure it dies if the whole app dies
        updateThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        updateThread.start()
        

    def __programmedMoveRobot( self ):
        
        
        print("PROGRAMMED MOVE ROBOT")
        
        '''
        # Rotate Head left right
        self.AC3.movement.setServoAngle('neck_rotate', -90, 30)
        self.AC3.movement.setServoAngle("head_tilt",-50,50)
        self.AC3.movement.setServoAngle("eye_rotate",-50,10)
        time.sleep(3)
        
        self.AC3.movement.setServoAngle('neck_rotate', 90, 90)
        self.AC3.movement.setServoAngle("head_tilt",-50,50)
        self.AC3.movement.setServoAngle("eye_rotate",50,20)
        time.sleep(2)

        self.AC3.movement.setServoAngle('neck_rotate', 0, 90)
        self.AC3.movement.setServoAngle("head_tilt",0,90)
        self.AC3.movement.setServoAngle("eye_rotate",10,30)
        
        # Test Neck - Look Engaged
        self.AC3.movement.setServoAngle("head_lean",50,50)
        self.AC3.movement.setServoAngle("neck_lean", 35.50)
        time.sleep(1)

        # Look around a bit
        self.AC3.movement.setServoAngle("eye_rotate",5,50)
        time.sleep(1)
        self.AC3.movement.setServoAngle("eye_rotate",-15,90)
        time.sleep(.5)
        self.AC3.movement.setServoAngle("eye_rotate",20,90)
        
        time.sleep(1)

        self.AC3.movement.setServoAngle("eye_rotate",0,90)
        
        # Test Neck - Look Scared / worred
        self.AC3.movement.setServoAngle("head_lean",-50,50)
        self.AC3.movement.setServoAngle("neck_lean", -50.50)
        time.sleep(2)

        time.sleep(1)
        

        self.AC3.movement.setServoAngle("head_lean",50,30)
        self.AC3.movement.setServoAngle("neck_lean", 45.30)
        time.sleep(3)

        # Test Eyes
        self.AC3.movement.setServoAngle("head_tilt",-50,50)
        self.AC3.movement.setServoAngle("eye_rotate",-50,50)
        time.sleep(1)
        self.AC3.movement.setServoAngle("head_tilt", 50.50)
        self.AC3.movement.setServoAngle("eye_rotate",0,50)
        time.sleep(1)
        self.AC3.movement.setServoAngle("head_tilt",0,50)
        '''
        
        for i in range(0, 50):
            

            
            # x angle
            x = randint(-90,90)

            #
            interest = randint( -20, 20)
            
            # Really make it disengage sometimes
            if interest < -5:
                interest -= 30
            if interest > 5:
                interest += 30

            # y angle
            y = randint( -20, 30)
            

            # speed
            speed = randint(40, 70)
            
            # time
            duration = randint(1,10)
            
            logger.info("Moving head: " + str(x) + " " + str(y) + " " + str(interest) + " " + str(speed) + " " + str(duration))
            
            
            # Get everything moving
            self.AC3.movement.setServoAngle("neck_rotate", x/2, speed)
            self.AC3.movement.setServoAngle("eye_rotate", -x/2, 90)
            self.AC3.movement.setServoAngle("head_lean", y + interest, speed)
            self.AC3.movement.setServoAngle("neck_lean", interest, speed)
            self.AC3.movement.setServoAngle("head_tilt", randint(-10,10), 50)
            time.sleep(1)

            self.AC3.movement.setServoAngle("eye_rotate", x/2 + randint(-25,25), 7)
            self.AC3.movement.setServoAngle("head_tilt", randint(-30,30),32)

            if duration > 6:
                time.sleep( 4 )
                duration -= 4
                self.AC3.movement.setServoAngle("head_tilt", randint(-30,30),20)
                self.AC3.movement.setServoAngle("eye_rotate", x/2 + randint(-25,25), 20)
                time.sleep( 2 )
                self.AC3.movement.setServoAngle("head_tilt", randint(-30,30),10)
                self.AC3.movement.setServoAngle("eye_rotate", x/2 + randint(-25,25), 7)

            time.sleep(duration)