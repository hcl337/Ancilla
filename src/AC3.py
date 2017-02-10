import logging, time, webbrowser
import inspect
import sys
import traceback
import inflection

# Our imports
from core.Movement import Movement
from core.Vision import Vision
from core.Expression import Expression
from core.Speech import Speech
from core.Hearing import Hearing
from core.Reasoning import Reasoning
from webserver.WebServer import AC3Server

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

        logger.info("################################################################################")
        logger.info("################################################################################")
        logger.info("")
        logger.info("                              Ancilla|Three")
        logger.info("")
        logger.info("################################################################################")
        logger.info("################################################################################")
        logger.info("")

        try:
            startTime = time.time( )
    
            logger.info("")
            logger.info("")
            logger.info("######################################## SPEECH")
            self.speech = Speech( self )
            self.speech.enable( )
            #self.speech.say( "Speech Enabled" )
            #self.speech.say( "Booting AC-3 Operating system." )
    
            logger.info("")
            logger.info("")
            logger.info("######################################## EXPRESSION")
            self.expression = Expression( self )
            self.expression.enable( )
            #self.speech.say( "Expressions")
    
            logger.info("")
            logger.info("")
            logger.info("######################################## VISION")
            self.vision = Vision( self )
            #self.vision.enable( )
            #self.speech.say( "Vision")
    
            logger.info("")
            logger.info("")
            logger.info("######################################## HEARING")
            self.hearing = Hearing( self )
            #self.hearing.enable( )
    
            logger.info("")
            logger.info("")
            logger.info("######################################## MOVEMENT")
            self.movement = Movement( self, "../parameters/servos.json" )
            self.movement.enable( )
            #self.speech.say( "Movement")
    
            logger.info("")
            logger.info("")
            logger.info("######################################## REASONING")
            self.reasoning = Reasoning( self )
    
            logger.info("")
            logger.info("")
            logger.info("######################################## WEB SERVER")
            self.server = AC3Server( self )
            self.server.enable()
        except:
            self.reportFatalError( )

        # We want to wait if it is still talking before we say
        # everything is done.
        while( self.speech.isTalking() ):
            time.sleep(0.1)

        endTime = time.time()


        # If we didn't crash, report that we are ready to go
        if self.isRunning( ):
            self.speech.say( "Ready in " + str(round(endTime-startTime, 2 )) + " seconds.")
                
            logger.info("Completed initializing AC3")
            logger.info("")
            logger.info("")
            logger.info("################################################################################")
            logger.info("################################################################################")
            logger.info("")
            logger.info("##                   Initialization fully complete")
            logger.info("")
            logger.info("################################################################################")
            logger.info("################################################################################")
            logger.info("")
            logger.info("")


    # This makes sure we don't try to shut down multiple times
    __isRunningNow = True

    def isRunning( self ):
        return self.__isRunningNow



    reportedFatalException = False

    def reportFatalError( self ):
        '''
        Logs and reports the exception which was thrown
        '''

        if self.reportedFatalException:
            logger.error("Got another fatal exception but disregarding...")
            return

        ex_type, ex, tb = sys.exc_info()

        # Try to get the name of the module we are
        try:
            frm = inspect.stack()[1]
            mod = inspect.getmodule(frm[0])
            #Make the module name easy for a human to understand if there are
            # multiple words in it camel case or underscores
            moduleName = inflection.humanize( mod.__name__ )
        except:
            moduleName = "Unknown"

        try:
            logger.error( "" )
            logger.error( "" )
            logger.error( "################################################################################")
            logger.error( "################################################################################")
            logger.error( "" )
            logger.error( "                            FATAL ERROR REPORTED" )
            logger.error( "" )
            logger.error( "################################################################################")
            logger.error( "################################################################################")
            logger.error( "" )
            logger.error( "TYPE:   " + str(ex_type.__name__) )
            logger.error( "" )
            logger.error( "REASON: " + str(ex))
            logger.error( "" )
            logger.error( "TRACE:")
            logger.error( "" )
            for l in traceback.format_exc(tb).split('\n'):
                logger.error( l )
            logger.error( "" )
            logger.error( "################################################################################")
            logger.error( "################################################################################")
            logger.error( "" )
            logger.error( "" )

            errorString = "Fatal Exception experienced in " + str(moduleName) + " module: Reason Specified is " + str(ex)
            if self.speech.isEnabled( ):
                self.speech.say(errorString)
                # Give it some time to say it before we trigger shutdown
                time.sleep(3)


        except Exception as e:
            logger.error( "Error reporting fatal error: " + str(ex_type) + " " + str(ex))
            logger.error( traceback.format_exc(tb))
        finally:
            self.shutdown( )



    def shutdown( self ):
        '''
        Shuts down all the elements of the system then exits. This is a defensive
        function which try to do everyting and protect against an multiple elements
        failing to shut down or throwing exceptions

        '''

        if not self.__isRunningNow:
            return

        startTime = time.time()

        logger.info( "" )
        logger.info( "" )
        logger.info( "################################################################################")
        logger.info( "" )
        logger.info( "SHUTTING DOWN EVERYTHING" )
        logger.info( "" )
        logger.info( "################################################################################")
        logger.info( "" )
        try:
            if self.reasoning is not None:
                self.reasoning.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling reasoning: " + str(ex) + " \n" + traceback.format_exc(tb))

        try:
            if self.movement is not None:
                self.movement.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling movement: " + str(ex) + " \n" + traceback.format_exc(tb))

        try:
            if self.expression is not None:
                self.expression.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling expression: " + str(ex) + " \n" + traceback.format_exc(tb))

        try:
            if self.vision is not None:
                self.vision.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling vision: " + str(ex) + " \n" + traceback.format_exc(tb))

        try:
            if self.hearing is not None:
                self.hearing.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling hearing: " + str(ex) + " \n" + traceback.format_exc(tb))

        try:
            if self.server is not None:
                self.server.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling server: " + str(ex) + " \n" + traceback.format_exc(tb))

        endTime = time.time()

        # Say something as we end...
        try:
            self.speech.say( "Shut down complete in " + str(round(endTime-startTime, 2)) + " seconds.")
            while self.speech.isTalking( ):
                time.sleep( 0.1 )
        except:
            pass

        # Disable speech last so we can speak through all of it.
        try:
            if self.speech is not None:
                self.speech.disable( )
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.error("Exception disabling speech: " + str(ex) + " \n" + traceback.format_exc(tb))

        
        time.sleep( 1 )
        logger.info( "" )
        logger.info( "################################################################################")
        logger.info( "################################################################################")
        logger.info( "" )
        logger.info("Shutdown complete.")
        logger.info( "" )
        logger.info( "################################################################################")
        logger.info( "################################################################################")
        logger.info( "" )

        self.__isRunningNow = False


ac3 = AC3( )


if ac3.isRunning( ):
    # new=0 means open in old tab if possible
    # autoraise=True means make it come to the forefront
    webbrowser.open("http://localhost:8888", new=0, autoraise=True)


################################################################################
# Turn on all of the systems because initialization was complete
################################################################################


#time.sleep(60)
################################################################################
# Run the sysetm
################################################################################


ac3.movement.setServoAngle('neck_rotate', -10, 20)
time.sleep(3)
ac3.movement.setServoAngle('neck_rotate', 10, 20)
time.sleep(5)
ac3.movement.setServoAngle('neck_rotate', 0, 20)
time.sleep(3)

#ac3.shutdown()

# Keep it going forever unless we shut down. This must be done in the main
# thread so we guarantee that it will exit. If we did this in a sub-thread
# or called exit() from it, we would just raise an exception.
while ac3.isRunning( ):
    time.sleep(1)

exit( 0 )
