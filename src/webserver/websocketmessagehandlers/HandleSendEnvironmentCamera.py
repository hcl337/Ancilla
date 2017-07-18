from AbstractHandler import AbstractHandler
from tornado.ioloop import PeriodicCallback
from tornado.websocket import WebSocketClosedError
import logging
import cv2 as cv
import base64
logger = logging.getLogger(__name__)


class HandleSendEnvironmentCamera( AbstractHandler ):
    '''
    Sends the environment frame at the specified interval
    '''

    def __init__(self, websocketHandler, AC3 ):
        super(HandleSendEnvironmentCamera, self).__init__(websocketHandler, AC3)
        self.camera_loop = None

    def canHandle( self, message ):
        return message['type'].upper() == 'SEND_ENVIRONMENT_CAMERA'


    def handle( self, message ):

        if not ('fps' in message and 'enable' in message):
            raise Exception("send_environment_camera message must contain 'fps' and 'enable' variables. See documentation.")

        fps = message['fps']
        enable = message['enable']

        if fps < 1 or fps > 30:
            raise Exception("fps variable for update rate must be between 1 and 30")


        # We want to make sure to cancel any old ones which were around
        self.stopHandling()

        if self.AC3.vision == None or not self.AC3.vision.isEnabled():
            error_message = {"type":"error","type":"Exception","description":"Vision not enabled so can not return frames."}
            self.websocketHandler.write_message(error_message )
            return

        # If they  want to enable, then do so.
        if enable:
            self.camera_loop = PeriodicCallback(self.__loop, 1000 / fps )
            self.camera_loop.start()
            logger.debug("Enabling broadcast environment camera")
        else:
            logger.debug("Disabling broadcast environment camera")



    def stopHandling( self ):
        if self.camera_loop is not None:
            self.camera_loop.stop( )
            self.camera_loop = None



    def __loop( self ):

        #logger.debug("Sending env frame")
        try:
            im = self.AC3.vision.getLatestEnvironmentFrame( )

            if im is None:
                logger.debug("No env frame to send")
                return

            cnt = cv.imencode('.jpg',im)[1]
            b64 = base64.encodestring(cnt)

            message = {
                "type": "ENVIRONMENT_CAMERA_FRAME",
                "image_data": b64,
                "data_type":"image/jpg",
                "width":im.shape[1],
                "height":im.shape[0],
                "fov": self.AC3.vision.getEnvironmentCameraFOV()
            }

            self.websocketHandler.write_message( message )
        except WebSocketClosedError:
            logger.error("Websocket connection disconnected")
            self.stopHandling()
        except:
            self.AC3.reportFatalError()


