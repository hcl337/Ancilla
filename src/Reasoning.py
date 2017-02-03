import time
import sys
import copy


# Only let us remember a set of things
MAX_HEARING_MEMORY = 10

class Reasoning:

    ac3 = None

    __memory = {
        "hearing": [ ],
        "vision" : {}
    }



    def __init__(self, ac3):
        self.ac3 = ac3
        self.ac3.hearing.registerListener( self.heardPhrase )


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

        print("heard this phrase: " + phrase)

        phrase = phrase.lower()

        if not ( 'ac3' in phrase):
            return

        if 'your name' in phrase:
            self.ac3.speech.say( "My name is AC-3. Nice to meet you.")
        elif 'thank you' in phrase:
            self.ac3.speech.say( "You are welcome!")
        elif 'good night' in phrase:
            self.ac3.speech.say( "Sleep well. I will be waiting for you to return")
        elif 'good morning' in phrase:
            self.ac3.speech.say( "It is a good morning!")
        elif 'spoon' in phrase:
            self.ac3.speech.say( "Woof. Woof. I would like to play with spoon.")
        elif 'wife' in phrase:
            self.ac3.speech.say( "Courtney is the best wife in the world!")
        elif 'court' in phrase:
            self.ac3.speech.say( "I like courtney.")
        elif 'hans' in phrase:
            self.ac3.speech.say( "Hans made me.")
        elif 'charlotte' in phrase:
            self.ac3.speech.say( "I can't wait to meet charlotte.")
        elif 'emmaline' in phrase:
            self.ac3.speech.say( "I can't wait to meet emmaline.")
        elif 'lilibeth' in phrase:
            self.ac3.speech.say( "I can't wait to meet lilibeth.")
        elif 'hello' in phrase:
            self.ac3.speech.say( "Hi there! It is nice to talk to a human.")
        elif 'ac3 shut down' in phrase:
            self.ac3.speech.say( "Ask me nicely.")
        elif 'ac3 please shut down' in phrase:
            self.ac3.speech.say( "Initiating shutdown.")
            time.sleep(3)
            self.ac3.shutdown()
        else:
        	pass#self.speech.say( "uh huh.")

