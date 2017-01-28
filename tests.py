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


def set_servo_angle(index, angle):
    '''
    Converts our servo angle into a pulse for the PWM
    '''
    pulse = int( 4096 * angle / 180 )

    print( str( index) + ": angle = " + str( angle) + " pulse = " + str(pulse) + " / 4096" )

    if isRaspberryPi:
        __set_servo_pulse(index, pulse)



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


set_servo_angle(1, 90)