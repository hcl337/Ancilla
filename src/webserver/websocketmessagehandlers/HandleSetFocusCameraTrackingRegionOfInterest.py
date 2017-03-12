from AbstractHandler import AbstractHandler
import logging
logger = logging.getLogger(__name__)


class HandleSetFocusCameraTrackingRegionOfInterest( AbstractHandler ):


    def __init__(self, websocketHandler, AC3 ):
        super(HandleSetFocusCameraTrackingRegionOfInterest, self).__init__(websocketHandler, AC3)

    def canHandle( self, message ):
        return message['type'].upper() == 'SET_FOCUS_CAMERA_TRACKING_REGION_OF_INTEREST'


    def handle( self, message ):
        raise Exception( "Not implemented")


    def stopHandling( self ):
        pass
