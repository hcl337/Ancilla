import logging, time, webbrowser

# Our imports
from Movement import Movement
from Vision import Vision
from Expression import Expression
from Speech import Speech
from hearing.SphinxHearing import SphinxHearing
from Reasoning import Reasoning
from server.WebServer import AC3Server

# Set the minimum level we log. DEBUG will show everything.
# INFO will show a lot less.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AC3:
    '''
    Main class for the robot which is the glue for all the different parts. It should
    also be passed around for each sub-unit to use to reference the other units cleanly.
    '''

    speech = None
    movement = None
    expression = None
    vision = None
    hearing = None
    reasoning = None
    server = None

    def __init__( self ):
        ################################################################################
        # Initialize everything before we turn it on because this is a physical system
        # so we want to find errors first
        ################################################################################

        startTime = time.time( )

        self.speech = Speech( )
        self.speech.enable( )
        #self.speech.say( "Speech Enabled" )
        #self.speech.say( "Booting AC-3 Operating system." )

        self.movement = Movement( "../parameters/servos.json" )
        #self.movement.enable( )
        #self.speech.say( "Movement")

        self.expression = Expression( )
        self.expression.enable( )
        #self.speech.say( "Expressions")

        self.vision = Vision( )
        self.vision.enable( )
        #self.speech.say( "Vision")

        self.hearing = SphinxHearing( self.speech )
        self.hearing.enable( ) 

        self.reasoning = Reasoning( self )
        #self.hearing.subscribe( self.reasoning.heardPhrase )
        #speech.say( "Reasoning")

        self.server = AC3Server( self )
        self.server.enable()

        # We want to wait if it is still talking before we say
        # everything is done.
        while( self.speech.isTalking() ):
            time.sleep(1)

        endTime = time.time()
        self.speech.say( "Ready in " + str(round(endTime-startTime, 2 )) + " seconds.")
        #hearing.enable( )

        logger.info("Completed initializing AC3")
        logger.info("")
        logger.info("")
        logger.info("################################################################################")
        logger.info("##                   Initialization fully complete")
        logger.info("################################################################################")
        logger.info("")
        logger.info("")


    # This makes sure we don't try to shut down multiple times
    __isRunningNow = True

    def isRunning( self ):
        return self.__isRunningNow



    def shutdown( self ):
        '''
        Shuts down all the elements of the system then exits

        '''

        if not self.__isRunningNow:
            return

        self.__isRunningNow = False

        logger.info("Shutting down robot...")
        self.speech.disable( )
        self.movement.disable( )
        self.expression.disable( )
        self.vision.disable( )
        self.hearing.disable( )
        self.reasoning.disable( )
        self.server.disable( )
        
        time.sleep( 1 )
        logger.info("Shutdown complete.")
        exit( 0 )

ac3 = AC3( )

webbrowser.open("http://localhost:8888", new=2)


################################################################################
# Turn on all of the systems because initialization was complete
################################################################################


#time.sleep(60)
################################################################################
# Run the sysetm
################################################################################

'''
ac3.movement.setServoAngle('neck_rotate', -10, 20)
time.sleep(3)
ac3.movement.setServoAngle('neck_rotate', 10, 20)
time.sleep(5)
ac3.movement.setServoAngle('neck_rotate', 0, 20)
time.sleep(3)
'''
#ac3.shutdown()

# Keep it going forever unless we shut down
while ac3.isRunning( ):
    time.sleep(1)

