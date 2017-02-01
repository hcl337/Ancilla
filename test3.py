




# Helper function to make setting a servo pulse width simpler.
def __set_servo_pulse(channel, msecs, pwm_freq):
    '''
    Low level code from Adafruit to control the pwm
    '''
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    #print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    #print('{0}us per bit'.format(pulse_length))
    pulse = msecs * 1000
    pulse //= pulse_length
    print("msecs: " + str(msecs) + " pulse: " + str(pulse))
    #adafruitServoController.set_pwm(channel, 0, int(pulse) )


__set_servo_pulse( 0, 2.5, 50)