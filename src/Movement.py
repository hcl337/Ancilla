from __future__ import division
import logging
import json
import time
import os
import copy
from threading import Timer, Thread

logger = logging.getLogger(__name__)

# Allow us to run this on other systems for programming by not enabling the hardware
# components and libraries.
if 'arm' in os.name:
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



    def __init__(self, servoParamsFilePath, adafruitServoController=None):
        '''
        Constructor

        Initializes the servos, loads the parameters and sets everything up.
        To start the motors, call enable( ).
        '''

        logger.info('Initializing muscles...')

        # Load all the parameters for the servos from our setup file. This is a JSON
        # file which describes all the parameters and has values for each of them
        with open(servoParamsFilePath) as f:
            self.servoState = json.loads(f.read())

        servos = self.servoState['servos']

        logger.info("Loaded " + str(len(servos)) + " servos and their parameters.")

        # Set the starting position for each servo to our specified resting position
        # to minimize the jerking of the system. We use the resting_angle which is
        # set for each servo to make this happen
        for servo in servos:
            logger.info(self.servoState['servos'][servo])
            servos[servo]['requested_angle'] = servos[servo]['resting_angle']
            servos[servo]['current_angle'] = servos[servo]['resting_angle']
            servos[servo]['requested_speed'] = 0
            servos[servo]['current_speed'] = 0

        logger.info("Set initial positions and speed for servos..")

        # We want to be able to run this on other systems for debugging purposes so
        # if it is not a raspberry pi, we won't load the controller boards but will
        # do everything else.
        if isRaspberryPi:

            logger.info("Instantiation starting: Adafruit PCA9685 16 Servo Board")

            # let someone send in an already constructed controller object if 
            # we are passing it in from somewhere else. If not, we should create
            # it ourselves.
            if adafruitServoController != None:
                self.adafruitServoController = Adafruit_PCA9685.PCA9685()
            
            # Set frequency to 60hz, good for servos. (From AdaFruit - not sure why)
            self.adafruitServoController.set_pwm_freq(self.servoState['params']['pwm_frequency'])

            logger.info("Instantiation complete: Adafruit PCA9685 16 Servo Board")
        # This allows us to run on Mac for testing

        else:
            logger.info("Not on Raspberry Pi so skipping Servo Board Instantiation")



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

        self.updateLoopActive = True

        # Create our thread
        updateThread = Thread(target=self.__updateLoop)
        # Make sure it dies if the whole app dies
        updateThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        updateThread.start()



    def disable( self ):
        '''
        Stops all servo updates by killing the update loop

        '''
        if not self.updateLoopActive:
            raise Exception("Trying to stop the muscles but they are already stopped.")

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



    def setServoAngle( self, name, angle, speed=None ):
        '''
        name  = The name of the servo
        angle = the requested servo angle to go to
        speed = the requested speed to use
        '''

        if not (name in self.servoState['servos']):
            raise Exception("Servo does not exist so can not setServoAngle for " + str(name))

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

        logger.debug("Set servo:     " + name + " angle = " + str(servo['requested_angle']) + " speed = " + str(servo['requested_speed']))



    def __updateLoop( self ):
        '''
        Loop through all of our specified PWMs and update them with our position/speed data. This 
        creates a thread which loops at our defined rate to update them
        '''

        # Set the PWM update interval based on our parameters
        interval = 1.0 / self.servoState['params']['angle_update_rate_hz']
        logger.info("Setting servo angle Update Interval to " + str(round(1/interval)) + " hz.")


        # If we have stopped this loop then de-activate the servos before we do anything else
        while( self.updateLoopActive ):

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
                raise Exception( "Servo update loop took more time to update than the allowed interval: " +  str(lastStartTime) + " " + str(interval) + " " +str(sleepAmount) + " " + str(time.time()) + " " + str(nextUpdate)) 
                self.disable()

            time.sleep( sleepAmount )


    def __updateServos( self, interval ):
        '''
        Do the actual work for each servo to interpolate its position
        '''

        # Loop through and update every servo
        for servoName in self.servoState['servos']:
            servo = self.servoState['servos'][servoName]

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

            servo['current_angle'] = round(servo['current_angle'] + increment, 3)
            servo['current_speed'] = abs( round(increment / interval, 2))

            # If we are really close, don't let little numbers creep in. Just set it to the correct one.
            if abs(servo['current_angle'] - servo['requested_angle']) < 0.01:
                servo['current_angle'] = servo['requested_angle']

            # Only update if we are actually moving somewhere. Otherwise it can keep its old location
            # we will just let it be there and will also not output ant other elements
            if servo['current_speed'] == 0: continue

            logger.info("Moving " + servoName + " from " + str(servo['current_angle']) + " to " + str(servo['requested_angle']) + " deg at " + str(servo['current_speed']) + " deg / sec "  )
            
            '''
            logger.debug("\t\tmax_distance_to_increment:        " + str(max_distance_to_increment))
            logger.debug("\t\ttotal_distance_to_increment:      " + str(total_distance_to_increment))
            logger.debug("\t\tIncrement:                        " + str(increment))
            logger.debug("\t\tIncrement:                        " + str(increment))
            logger.debug("\t\tTotal Distance:                   " + str(distance_to_increment))
            logger.debug("\t\tIncrement:                        " + str(increment))
            logger.debug("\t\tRequested Angle:                  " + str(servo['requested_angle']))
            logger.debug("\t\tRequested Speed:                  " + str(servo['requested_speed']))
            logger.debug("\t\tCurrent Angle:                    " + str(servo['current_angle']))
            logger.debug("\t\tCurrent Speed:                    " + str(servo['current_speed']))
            '''
            set_servo_angle(servo, servo['current_angle'])


def set_servo_angle(servo, angle):
    '''
    Converts our servo angle into a pulse for the PWM
    '''
    pulse = int( 4096 * (angle + servo['zero_offset']) / 180 )
    if isRaspberryPi:
        set_servo_pulse(servo['servo_index'], pulse)
    else:
        pass
        #logger.debug( str( servo['servo_index'] ) + ": angle = " + str( angle) + " speed = " + str(servo['current_speed']) + " pulse = " + str(pulse) + " / 4096" )


# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    '''
    Low level code from Adafruit to control the pwm
    '''
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    #print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    #print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    adafruitServoController.set_pwm(channel, 0, pulse)

