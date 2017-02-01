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

print os.name
if 'arm' in os.name or 'posix' in os.name:
    import Adafruit_PCA9685
    adafruitServoController = Adafruit_PCA9685.PCA9685()
    time.sleep(2)
    #adafruitServoController.set_pwm_freq(50)
    isRaspberryPi = True
else:
    isRaspberryPi = False


def set_servo_angle(index, angle):
    '''
    Converts our servo angle into a pulse for the PWM
    '''

    if angle > 180: angle = 180
    if angle < 0: angle = 0

    pulse = int( 4095 * angle / 180 )

    print( str( index) + ": angle = " + str( angle) + " position = " + str(pulse) + " / 4096" )

    if isRaspberryPi:
        adafruitServoController.set_pwm(index, 0, pulse)



# Helper function to make setting a servo pulse width simpler.
def __set_servo_pulse(channel, pulse):
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
    adafruitServoController.set_pwm(channel, 0, int(pulse) )
    
while True:

    adafruitServoController.set_pwm_freq(50)

    print( "left" ) 
    adafruitServoController.set_pwm(0, 0, 544)
    time.sleep(2)

    print( "Center" )
    adafruitServoController.set_pwm(0, 0, 2400)
    time.sleep(2)

    print( "right" )
    adafruitServoController.set_pwm(0, 0, 1500)
    time.sleep(2)
