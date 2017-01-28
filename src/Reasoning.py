import time
import sys


class Reasoning:

    speech = None;
    movement = None;
    expression = None;
    vision = None;
    hearing = None;


    def __init__(self, speech, movement, expression, vision, hearing):
        self.speech = speech
        self.movement = movement
        self.expression = expression
        self.vision = vision
        self.hearing = hearing


        #self.hearing.addImportantWord( "emmaline" )
        #self.hearing.addImportantWord( "courtney" )
        #self.hearing.addImportantWord( "court" )
        #self.hearing.addImportantWord( "hans" )
        #self.hearing.addImportantWord( "charlotte" )
        #self.hearing.addImportantWord( "emmaline" )
        #self.hearing.addImportantWord( "lilibeth" )
        self.hearing.addImportantWord( "AC-3" )
        self.hearing.addImportantWord( "your name" )
        self.hearing.addImportantWord( "hello" )



    def heardPhrase( self, phrase ):
        print("heard this phrase: " + phrase)

        if 'your name' in phrase:
            self.speech.say( "My name is AC-3. Nice to meet you.")
        elif 'thank you' in phrase:
            self.speech.say( "You are welcome!")
        elif 'good night' in phrase:
            self.speech.say( "Sleep well. I will be waiting for you to return")
        elif 'good morning' in phrase:
            self.speech.say( "It is a good morning!")
        elif 'spoon' in phrase:
            self.speech.say( "Woof. Woof. I would like to play with spoon.")
        elif 'wife' in phrase:
            self.speech.say( "Courtney is the best wife in the world!")
        elif 'court' in phrase:
            self.speech.say( "I like courtney.")
        elif 'hans' in phrase:
            self.speech.say( "Hans made me.")
        elif 'charlotte' in phrase:
            self.speech.say( "I can't wait to meet charlotte.")
        elif 'emmaline' in phrase:
            self.speech.say( "I can't wait to meet emmaline.")
        elif 'lilibeth' in phrase:
            self.speech.say( "I can't wait to meet lilibeth.")
        elif 'hello' in phrase:
            self.speech.say( "Hi there! It is nice to talk to a human.")
        else:
        	pass#self.speech.say( "uh huh.")

