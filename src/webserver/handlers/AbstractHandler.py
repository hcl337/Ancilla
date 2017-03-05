import logging
logger = logging.getLogger(__name__)


class AbstractHandler( object ):

    AC3 = None
    websocketHandler = None

    def __init__(self, websocketHandler, AC3 ):
        self.AC3 = AC3
        self.websocketHandler = websocketHandler

        logger.debug("Added New Handler: " + self.__class__.__name__ + " for WebSocket: " + websocketHandler.handlerToken + " for client: " + websocketHandler.uniqueClientToken )

    def canHandle( self, message ):
        raise Exception( "Must subclass AbstractHandler.canHandle( ) ")


    def handle( self, message, websocketHandler, AC3 ):
        raise Exception( "Must subclass AbstractHandler.handle( ) ")

    def stopHandling( self ):
        raise Exception("Must subclass AbstractHandler.stopHandling( ) ")