from AbstractHandler import AbstractHandler
from tornado.ioloop import PeriodicCallback
from tornado.websocket import WebSocketClosedError
import logging
import cv2 as cv
import base64

logger = logging.getLogger(__name__)


class SendFocusCameraHandler( AbstractHandler ):
    '''
    Sends the focus frame at the specified interval
    '''

    camera_loop = None

    def canHandle( self, message ):
        return message['message'] == 'send_focus_camera'


    def handle( self, message ):

        if not ('fps' in message and 'enable' in message):
            raise Exception("send_focus_camera message must contain 'fps' and 'enable' variables. See documentation.")

        fps = message['fps']
        enable = message['enable']

        if fps < 1 or fps > 30:
            raise Exception("fps variable for update rate must be between 1 and 30")


        # We want to make sure to cancel any old ones which were around
        self.stopHandling()

        if self.AC3.vision == None or not self.AC3.vision.isEnabled():
            error_message = {"message":"error","type":"Exception","description":"Vision not enabled so can not return frames."}
            self.websocketHandler.write_message(error_message )
            return

        # If they  want to enable, then do so.
        if enable:
            self.camera_loop = PeriodicCallback(self.__loop, 1000 / fps )
            self.camera_loop.start()
            logger.debug("Enabling broadcast focus camera")
        else:
            logger.debug("Disabling broadcast focus camera")


    def stopHandling( self ):
        if self.camera_loop is not None:
            self.camera_loop.stop( )
            self.camera_loop = None



    def __loop( self ):

        try:
            im = self.AC3.vision.getLatestFocusFrame( )

            if im is None:
                return

            cnt = cv.imencode('.jpg',im)[1]
            b64 = base64.encodestring(cnt)        

            message = {
                "message": "focus_camera_frame",
                "image_data": b64,
            }

            self.websocketHandler.write_message( message )
        except WebSocketClosedError:
            logger.error("Websocket connection disconnected")
            self.stopHandling()
        except:
            self.AC3.reportFatalError()


