import json
from AbstractHandler import AbstractHandler
from tornado.ioloop import PeriodicCallback
from tornado.websocket import WebSocketClosedError
import tornado
import logging
logger = logging.getLogger(__name__)


class SendStateHandler( AbstractHandler ):
    '''

    '''
    state_loop = None

    def canHandle( self, message ):
        return message['message'] == 'send_state'


    def handle( self, message ):

        if not ('mps' in message and 'enable' in message):
            raise Exception("State message must contain 'mps' and 'enable' variables. See documentation. Not: " + json.dumps( message ))

        mps = message['mps']
        enable = message['enable']

        if mps < 1 or mps > 30:
            raise Exception("MPS variable for update rate must be between 1 and 30")

        # We want to make sure to cancel any old ones which were around
        self.stopHandling()

        # If they  want to enable, then do so.
        if enable:
            logger.debug("Starting to broadcast state")
            self.state_loop = PeriodicCallback(self.__stateLoop, 1000 / mps)
            self.state_loop.start()
            


    def stopHandling( self ):
        if self.state_loop is not None:
            self.state_loop.stop()
            self.state_loop = None



    def __stateLoop(self):
        try:
            message = {
            "message":"state",
            "data": {
                "movement": self.AC3.movement.getState(),
                "memory": self.AC3.reasoning.getMemory(),
                "vision": self.AC3.vision.getVisibleObjects()
                }
            }
            self.websocketHandler.write_message(message)
        except tornado.websocket.WebSocketClosedError as e:
            import traceback
            logger.error("WebsocketErrorClosed in stateloop WebSocket: '" + str(e) + "'")
            traceback.print_exc()
            self.stopHandling()
        except Exception as e:
            self.stopHandling()
            logger.error("Error in stateloop WebSocket: " + str(e))
