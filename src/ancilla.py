import logging, time

# Our imports
from Movement import Movement
from Vision import Vision
from Expression import Expression
from Speech import Speech
from Hearing import Hearing

# Set the minimum level we log. DEBUG will show everything.
# INFO will show a lot less.
logging.basicConfig(level=logging.DEBUG)


################################################################################
# Initialize everything before we turn it on because this is a physical system
# so we want to find errors first
################################################################################

movement = Movement( "../parameters/servos.json" )

vision = Vision( )

hearing = Hearing( )

speech = Speech( )

expression = Expression( )



################################################################################
# Turn on all of the systems because initialization was complete
################################################################################

speech.enable( )

speech.say( "Waking up now")

movement.enable( )

speech.say( "Activated movement")

expression.enable( )

speech.say( "Activated expression")

vision.enable( )

speech.say( "Activated vision")

speech.say( "Initialization Complete")


################################################################################
# Run the sysetm
################################################################################

movement.setServoAngle('head_tilt', 163, 20)
time.sleep(6)
movement.setServoAngle('head_tilt', 0, 90)
time.sleep(5)
movement.setServoAngle('head_tilt', 45, 30)
time.sleep(10)