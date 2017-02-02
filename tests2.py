# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

import logging
logging.basicConfig(level=logging.DEBUG)
# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 542  # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000.0    # 1,000,000 us per second
    pulse_length /= 50.       # 50 Hz
    print(str(pulse_length) + ' us per period')
    pulse_length /= 4096.     # 12 bits of resolution
    print(str(round(pulse_length)) + ' us per bit')
    pulse *= 1000
    pulse //= pulse_length
    print "pulse: " + str(pulse)
    pwm.set_pwm(channel, 0, int(pulse))

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(50)


print('Moving servo on channel 0, press Ctrl-C to quit...')
#while True:
# Move servo on channel O between extremes.
#set_servo_pulse(0, 0.5)
pwm.set_pwm(0, 0, 102)
time.sleep(1)
#set_servo_pulse(0, 2.5)
pwm.set_pwm(0, 0, 512)
time.sleep(1)
#set_servo_pulse(0, 1.5)
pwm.set_pwm(0, 0, 312)
time.sleep(2)

for i in range(1,4):
  pwm.set_pwm(i, 0, 350)
  time.sleep(1)
  pwm.set_pwm(i, 0, 250)
  time.sleep(1)
  pwm.set_pwm(i, 0, 312)
  time.sleep(1)
  # 521, 104, 312