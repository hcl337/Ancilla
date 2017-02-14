from AbstractHandler import AbstractHandler
import logging
logger = logging.getLogger(__name__)


class SetFocusCameraTrackingRegionOfInterestHandler( AbstractHandler ):

    def canHandle( self, message ):
        return message['message'] == 'set_focus_camera_tracking_region_of_interest'


    def handle( self, message ):
        raise Exception( "Not implemented")


    def stopHandling( self ):
        pass
