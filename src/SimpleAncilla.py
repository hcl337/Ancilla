from Movement import Movement
import time, logging
logging.basicConfig(level=logging.DEBUG)

movement = Movement( "../parameters/singleservo.json" )
movement.enable()

movement.setServoAngle('neck_rotate', 90)

time.sleep(5)

movement.setServoAngle('neck_rotate', -90)

time.sleep(5)

movement.setServoAngle('neck_rotate', 0)

time.sleep(5)