from __future__ import division
import json
import time
import os
import copy
from threading import Timer, Thread

import logging
logger = logging.getLogger(__name__)


# Allow us to run this on other systems for programming by not enabling the hardware
# components and libraries.
if 'Linux' in os.uname()[0]:
    import Adafruit_PCA9685
    isRaspberryPi = True
else:
    isRaspberryPi = False


class Movement:
    '''
    The main class which controls the angle, speed and path of all the motors. It
    reads the parameters for each motor from the setup JSON file and takes care
    of end constraints, maximum velocity, automatic updates, etc.

    '''

    # The state for the servos is loaded from the properties file and stored here
    # where it is accessed privately by this class. It stores the current and requested
    # angle and other things.
    servoState  = None;

    # Variable identifying if the servo update loop is enabled
    updateLoopActive = False;

    # The servo controller board library
    adafruitServoController = None;

    AC3 = None

    def __init__(self, AC3, servoParamsFilePath, adafruitServoController=None):
        '''
        Constructor

        Initializes the servos, loads the parameters and sets everything up.
        To start the motors, call enable( ).
        '''

        self.AC3 = AC3

        logger.info('Initializing muscles...')

        if not isRaspberryPi:
            self.AC3.speech.say("Movement disabled on OSX.")

        # Load all the parameters for the servos from our setup file. This is a JSON
        # file which describes all the parameters and has values for each of them
        with open(servoParamsFilePath) as f:
            self.servoState = json.loads(f.read())

        servos = self.servoState['servos']

        logger.info("\tLoaded " + str(len(servos)) + " servos and their parameters.")

        # Set the starting position for each servo to our specified resting position
        # to minimize the jerking of the system. We use the resting_angle which is
        # set for each servo to make this happen
        for servo in servos:
            logger.info(self.servoState['servos'][servo])
            servos[servo]['requested_angle'] = servos[servo]['resting_angle']
            # We have to tell the system we have a little ways to go so it
            # moves us
            servos[servo]['current_angle'] = servos[servo]['resting_angle'] - 0.1
            servos[servo]['requested_speed'] = 10
            servos[servo]['current_speed'] = 10

        logger.info("\tSet initial positions and speed for servos..")

        # We want to be able to run this on other systems for debugging purposes so
        # if it is not a raspberry pi, we won't load the controller boards but will
        # do everything else.
        if isRaspberryPi:

            logger.info("\tInstantiation starting: Adafruit PCA9685 16 Servo Board")

            # let someone send in an already constructed controller object if
            # we are passing it in from somewhere else. If not, we should create
            # it ourselves.
            if adafruitServoController == None:
                self.adafruitServoController = Adafruit_PCA9685.PCA9685()

            else:
                self.adafruitServoController = adafruitServoController

            # Set it to the right frequency
            self.adafruitServoController.set_pwm_freq( Movement.PWM_FREQUENCY )


            logger.info("\tInstantiation complete: Adafruit PCA9685 16 PWM Servo Board")
        # This allows us to run on Mac for testing

        else:
            logger.info("\tNot on Raspberry Pi so skipping Servo Board Instantiation")



    def isEnabled( self ):
        '''
        Returns true if the servo control loop is actively controlling the position
        of the servos
        '''
        return self.updateLoopActive



    def enable( self ):
        '''
        Creates a threaded daemon update loop for triggering position changes
        in the servos. This must be called to turn everything on
        '''
        logger.info("Enabling muscles controllers")
        if self.updateLoopActive:
            raise Exception("Trying to start the muscles but they are already started.")

        logger.info("Enabling movement (Servo motors)")
        self.updateLoopActive = True

        # Create our thread
        updateThread = Thread(target=self.__updateLoop)
        # Make sure it dies if the whole app dies
        updateThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        updateThread.start()

        for servo in self.servoState['servos']:
          self.setServoAngle(servo, self.servoState['servos'][servo]['resting_angle'], 10)


    isShuttingDown = False
    
    def disable( self ):
        '''
        Stops all servo updates by killing the update loop

        '''
        
        self.isShuttingDown = True
        servos = self.servoState['servos']
        for servo in servos:
            servos[servo]['requested_angle'] = servos[servo]['resting_angle']
            servos[servo]['requested_speed'] = servos[servo]['max_speed']
        
        time.sleep(1.5)
        
        self.isShuttingDown = False
        self.updateLoopActive = False



    def getservoState( self, name ):
        '''
        returns the servo parameters for a specific servo
        '''
        if name in self.servoState['servos']:
            # Return a clone of the data so we don't mess ours up by letting someone
            # accidentally edit it.
            return copy.deepcopy( self.servoState['servos']['name'] )
        else:
            raise Exception("Can not return servo parameters. Servo does not exist: " + str(name))



    def getState( self ):
        '''
        returns all the current params of the system
        '''
        # Return a clone of the data so we don't mess ours up by letting someone
        # accidentally edit it.
        return copy.deepcopy( self.servoState )



    def setServoAngle( self, name, angle, speed=None ):
        '''
        name  = The name of the servo
        angle = the requested servo angle to go to
        speed = the requested speed to use
        '''

        if not (name in self.servoState['servos']):
            raise Exception("Servo does not exist so can not setServoAngle for " + str(name))

        # Don't let us update if we are shutting down
        if self.isShuttingDown:
            return
        
        servo = self.servoState['servos'][name]

        # Keep things in bounds for our requested position
        if angle > servo['max_angle']:
            servo['requested_angle'] = servo['max_angle']
        elif angle < servo['min_angle']:
            servo['requested_angle'] = servo['min_angle']
        else:
            servo['requested_angle'] = angle

        # If they just specified a position then go there at the maximum  speed allowed
        if speed == None:
            speed = servo['max_speed']
        elif speed > servo['max_speed']:
            servo['requested_speed'] = servo['max_speed']
        else:
            servo['requested_speed'] = speed

        #logger.debug("Set servo:     " + name + " angle = " + str(servo['requested_angle']) + " speed = " + str(servo['requested_speed']))



    def __updateLoop( self ):
        '''
        Loop through all of our specified PWMs and update them with our position/speed data. This
        creates a thread which loops at our defined rate to update them
        '''
        #print("Update loop")
        try:
            # Set the PWM update interval based on our parameters
            interval = 1.0 / self.servoState['params']['servo_position_update_rate_hz']
            #logger.info("Setting servo angle Update Interval to " + str(round(1/interval)) + " hz.")
    
    
            # If we have stopped this loop then de-activate the servos before we do anything else
            while( self.updateLoopActive ):

                # Calculate the start time so we know how much time has happened before we trigger
                # this again
                startTime = time.time()
                nextUpdate = startTime + interval
    
                # Active the actual work for updating
                self.__updateServos( interval )
    
                # It probably took some time to update, so schedule the next update to be minus
                # that time
                sleepAmount = nextUpdate - time.time()
    
                # This is just a protection that should never be triggered. If it takes us
                # waay too long, we need to log it and stop or we will crash the stack
                if( sleepAmount < 0 ):
                    sleepAmount = 0
                #    raise Exception( "Servo update loop took more time to update than the allowed interval: " + str(interval) + " " +str(sleepAmount) + " " )
                #    self.disable()
    
                time.sleep( sleepAmount )
        except Exception as e:
            self.updateLoopActive = None
            self.AC3.reportFatalError( )

        print("Update end")


    def __updateServos( self, interval ):
        '''
        Do the actual work for each servo to interpolate its position
        '''

        # Loop through and update every servo
        for servoName in self.servoState['servos']:
            servo = self.servoState['servos'][servoName]
            
            #print("\t\tUpdating Servo: " + servoName )

            # Max distance we can travel in this tick due to the servo constraints
            max_distance_to_increment = servo['requested_speed'] * interval

            # This is the total amount we want to go to get where we want
            # to be in the end
            total_distance_to_increment = servo['requested_angle'] - servo['current_angle']

            # Bound it by the maximum speed for this time period
            if total_distance_to_increment > max_distance_to_increment:
                distance_to_increment = max_distance_to_increment
            elif total_distance_to_increment < -max_distance_to_increment:
                distance_to_increment = -max_distance_to_increment
            else:
                distance_to_increment = total_distance_to_increment

            # When we get really close, we don't want to jump at the end, so this
            # makes it where we slow down in the last few degrees. This will slow
            # it down to 1/4 the speed once close
            if abs(total_distance_to_increment) < servo['precision_threshold_angle']:
                increment = distance_to_increment/4 + distance_to_increment * abs(total_distance_to_increment / servo['precision_threshold_angle']) * 3 / 4
            else:
                increment = distance_to_increment

            servo['current_angle'] = round(servo['current_angle'] + increment, 4)
            servo['current_speed'] = abs( round(increment / interval, 4))

            # If we are really close, don't let little numbers creep in. Just set it to the correct one.
            if abs(servo['current_angle'] - servo['requested_angle']) < 0.01:
                servo['current_angle'] = servo['requested_angle']

            # Only update if we are actually moving somewhere. Otherwise it can keep its old location
            # we will just let it be there and will also not output ant other elements
            if servo['current_speed'] == 0:
                #print("\t\t Servo not moving: " )
                continue

            #logger.info("Moving " + servoName + " from " + str(servo['current_angle']) + " to " + str(servo['requested_angle']) + " deg at " + str(servo['current_speed']) + " deg / sec "  )


            # At the end, we add in the zero-offset so we are in the correct range for the servo
            # This shifts the angle to be the correct one based on the specific servo so we give
            # it the correct offsets. All servos go from 0 to 180 degrees. But if we want
            # to center the head, we set a zero_offset of 90 degrees so when we use it, it goes
            # from -90 to 90 degrees
            self.__set_servo_pwm_pulse(servo, servo['current_angle'] - servo['hardware_zero_offset'])



    # These are a set of constants that have to do with the actual driver board and
    # the spec for hobby servos so they are not changable. Also, because these are
    # used so much, we don't want to do a lookup in a dictionary or other slow
    # element
    MIN_ANGLE = 0                               # Servo physical angle
    MAX_ANGLE = 180                             # Servo physical angle
    MIN_PULSE_LENGTH_MSECS = 0.5                # 0 degrees
    MAX_PULSE_LENGTH_MSECS = 2.5                # 180 degrees
    PULSE_LENGTH_RANGE_MSECS = MAX_PULSE_LENGTH_MSECS - MIN_PULSE_LENGTH_MSECS
    PWM_FREQUENCY = 50                          # A standard we can't change
    TICKS_PER_SECOND = (2**12)*PWM_FREQUENCY     # 12-bit at PWM frequency
    TICKS_PER_MSEC = TICKS_PER_SECOND / 1000.0

    def __set_servo_pwm_pulse(self, servo, angle):
        '''
        Converts our servo angle into a pulse for the PWM. The PWM is 12 bits so itis 0..4095 but
        servos expect a 50 hz update and uses only a subset of the data

        First it needs a frequency that results in a 20 msec cycle time by using the formula 1 / Cycle Time = Frequency.
        So, 1 divided by .020 results in 50 Hz, which is one input needed by our program.

        Next let's divide our 20 msec cycle by 4096 units, and we get 4.8 usec per unit. Now we can divide
        the pulse widths needed by a typical servo by the resolution of our controlling device.

        Results:
        * 0.5 ms / 4.8 usec = 102 the number required by our program to position the servo at 0 degrees
        * 1.5 msec / 4.8 usec = 307 the number required by our program to position the servo at 90 degrees
        * 2.5 msec / 4.8 usec = 512 the number required by our program to position the servo at 180 degrees
        '''

        #
        #pulse = int( 4096 * (angle + servo['zero_offset']) / 180 )

        # Bound the signal so we don't command something impossible
        if angle > Movement.MAX_ANGLE: angle = Movement.MAX_ANGLE
        if angle < Movement.MIN_ANGLE: angle = Movement.MIN_ANGLE

        # The hobby servo spec says it defaults to 0.5ms to 2.5ms with the center being 1.5ms
        # for the middle of the servo. So we do the calculation here
        msecPulse = Movement.MIN_PULSE_LENGTH_MSECS + Movement.PULSE_LENGTH_RANGE_MSECS * angle / Movement.MAX_ANGLE

        # Convert to ticks which equal the number of milliseconds we need
        pulseInTicks = int( round( msecPulse * Movement.TICKS_PER_MSEC) )

        #logger.debug( str( servo['servo_index'] ) + ": servo_angle = " + str( angle) + " servo_speed = " + str(servo['current_speed']) + " pwm_pulse: " + str(round(msecPulse, 3) ) + " pwm_ticks = " + str(pulseInTicks) + " / 4096" )

        # Don't send out a command unless we are talking to a real raspberry pi
        if isRaspberryPi:
            self.adafruitServoController.set_pwm(servo['servo_index'], 0, pulseInTicks)
        else:
            pass

'''
logging.basicConfig(level=logging.DEBUG)


move = Movement( None, "../../parameters/servos.json" )
move.enable()
move.setServoAngle("head_tilt", -10, 60 )
time.sleep(5)
'''