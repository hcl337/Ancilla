import json
from AbstractHandler import AbstractHandler
import logging
logger = logging.getLogger(__name__)

class SetServoPosition( AbstractHandler ):

    def canHandle( self, message ):
        return 'set_servo_position' == message['message']


    def handle( self, message ):
        if not ('servo_name' in message and 'angle' in message and 'speed' in message):
            raise Exception("set_servo_position message must have 'servo_name', 'angle' and 'speed'. Not: " + json.dumps(message))
        self.AC3.movement.setServoAngle(message['servo_name'], message['angle'], message['speed'])

    def stopHandling( self ):
        pass