import logging, time

# Our imports
from Movement import Movement
from Vision import Vision
from Expression import Expression
from Speech import Speech
from Hearing import Hearing
from Reasoning import Reasoning

# Set the minimum level we log. DEBUG will show everything.
# INFO will show a lot less.
logging.basicConfig(level=logging.DEBUG)


################################################################################
# Initialize everything before we turn it on because this is a physical system
# so we want to find errors first
################################################################################

startTime = time.time( )
speech = Speech( )
speech.enable( )
#speech.say( "Booting AC-3 Operating system." )
#speech.say( "Speech" )

movement = Movement( "../parameters/servos.json" )
movement.enable( )
#speech.say( "Movement")

expression = Expression( )
expression.enable( )
#speech.say( "Expressions")

vision = Vision( )
vision.enable( )
#speech.say( "Vision")

hearing = Hearing( )
#speech.say( "Hearing")

reasoning = Reasoning( speech, movement, expression, vision, hearing )
hearing.subscribe( reasoning.heardPhrase )
#speech.say( "Reasoning")

while( speech.isTalking() ):
	time.sleep(1)

endTime = time.time()
speech.say( "AC-3 Ready for duty.")
hearing.enable( )



################################################################################
# Turn on all of the systems because initialization was complete
################################################################################


#time.sleep(60)
################################################################################
# Run the sysetm
################################################################################


movement.setServoAngle('head_tilt', 163, 20)
time.sleep(6)
movement.setServoAngle('head_tilt', 0, 90)
time.sleep(5)
movement.setServoAngle('head_tilt', 45, 30)
time.sleep(10)
