import os
import logging
import urllib2
import httplib
import socket
import base64
import hashlib
import time
import json
import misaka
import gfm
from threading import Thread
import tornado.web
import tornado.websocket
from random import randint
from tornado.ioloop import PeriodicCallback
from tornado.websocket import WebSocketClosedError
import cv2 as cv

# import ServerHelpers which has abstracted out all of our detail stuff to support
# the web server
from ServerHelpers import (BaseHandler, displayRequestDetails, SERVER_COOKIE_NAME, 
    isLoggedIn, loadEncryptedPassword, getServerCookie, setServerCookie, clearServerCookie,
    SERVER_PORT, SERVER_FILE_ROOT, DOC_PATH, README_DOC_PATH )
from handlers import *

logger = logging.getLogger(__name__)


clients = {}
numConnections = 0

class RobotWebSocket(tornado.websocket.WebSocketHandler):

    # Reference to our movement object
    AC3 = None



    def initialize( self, AC3 ):
        self.AC3 = AC3
        self.messageHandlers = []
        self.uniqueClientToken = "-1"
        self.handlerToken = "S"+str(randint(100000,1000000)) + "S"

        #self.initializeHandlers()
        '''
        try:
            # Add all of our websocket message handlers here
            self.__registerMessageHandler( HandleSendEnvironmentCamera.HandleSendEnvironmentCamera( self, AC3 ) )
            self.__registerMessageHandler( HandleSendFocusCamera.HandleSendFocusCamera( self, AC3 ) )
            self.__registerMessageHandler( HandleSendState.HandleSendState( self, AC3 ) )
            self.__registerMessageHandler( HandleSetFocusCameraTrackingRegionOfInterest.HandleSetFocusCameraTrackingRegionOfInterest( self, AC3 ) )
            self.__registerMessageHandler( HandleSetServoPosition.HandleSetServoPosition( self, AC3 ) )
            self.__registerMessageHandler( HandleShutdown.HandleShutdown( self, AC3 ) )

        except:
            AC3.reportFatalError( )
        '''


    def initializeHandlers( self ):

        logger.debug("Num handlers on start: " + str(len(self.messageHandlers)))
        try:
            # Add all of our websocket message handlers here
            self.__registerMessageHandler( HandleSendEnvironmentCamera.HandleSendEnvironmentCamera( self, self.AC3 ) )
            self.__registerMessageHandler( HandleSendFocusCamera.HandleSendFocusCamera( self, self.AC3 ) )
            self.__registerMessageHandler( HandleSendState.HandleSendState( self, self.AC3 ) )
            self.__registerMessageHandler( HandleSetFocusCameraTrackingRegionOfInterest.HandleSetFocusCameraTrackingRegionOfInterest( self, self.AC3 ) )
            self.__registerMessageHandler( HandleSetServoPosition.HandleSetServoPosition( self, self.AC3 ) )
            self.__registerMessageHandler( HandleShutdown.HandleShutdown( self, self.AC3 ) )

        except:
            self.AC3.reportFatalError( )

        logger.debug("Num handlers on end: " + str(len(self.messageHandlers)))


    # This deals with the new Tornado 4.0 blocking of cross domain web sockets
    # on default and lets it through
    def check_origin(self, origin):
        return True


    @isLoggedIn()
    def get(self):

        # Upgrade header should be present and should be equal to WebSocket
        if self.request.headers.get("Upgrade", "").lower() != 'websocket':
            self.set_status(400)
            log_msg = {"error": "can only GET /websocket endpoint with request to 'upgrade' to 'websocket' protocal"}
            self.finish(log_msg)
            #gen_log.debug(log_msg)
            return

        super(RobotWebSocket, self).get()



    def open(self):
        '''
        Only open if we are already signed in

        '''

        global numConnections
        global clients

        logger.info("New connection to web socket")

        displayRequestDetails( self )

        # Get the cookie, extract our session token and add a unique
        # element to it so we support multiple websocket logins, but 
        # can still track them back to the user.
        cookie = getServerCookie( self )
        token = cookie['token']
        numConnections += 1
        uniqueClientToken = self.handlerToken + "." + token + "." + str(numConnections)
        clients[uniqueClientToken] = self

        # Store it so we can reference it when we shut down
        self.uniqueClientToken = uniqueClientToken

        # We need new handlers for each instance
        self.initializeHandlers( )

        for client in clients:
            logger.debug(">>> " + clients[client].handlerToken)



    def __registerMessageHandler( self, handler ):

        self.messageHandlers.append( handler )



    def on_close( self ):
        '''
        When they request a close or we are disconnected
        make sure that we stop all of the data which was
        coming in

        '''

        global clients

        if self.uniqueClientToken in clients:
            del clients[self.uniqueClientToken]
        else:
            logger.error("Someone must have already deleted this user as the websocket connection is not a specified client: " + self.uniqueClientToken)

        for handler in self.messageHandlers:
            handler.stopHandling( )



    def on_message(self, message):

        logger.debug("Received Websocket Message from " + self.uniqueClientToken + ": " + str(message))
        try:
            try:
                message = json.loads( message )
            except:
                self.write_message(json.dumps)

            # First make sure it has the message tag in it we use
            if not 'message' in message:
                returnMessage = {"message": "error", "type": "UnsupportedMessage", "description":"Message must have 'message' element with name of message."}
                self.write_message( json.dumps(returnMessage))
                return False

            # Loop through all handlers and see if one of them can process it
            wasHandled = False
            for handler in self.messageHandlers:
                if handler.canHandle( message ):
                    handler.handle( message )
                    wasHandled = True
                    break

            # Handle error if no supported message handler exists
            if not wasHandled:
                returnMessage = {"message": "error", "type": "UnsupportedMessage", "description":"Unknown Message Type: " + message['message']}
                self.write_message( json.dumps(returnMessage))

        except ValueError as e:
            logger.error("Could not decode message: " + str(message))
            returnMessage = {"message": "error", "type": "ValueError", "description":"Could not parse incoming message. Must be a JSON dictionary with at least {'message':'name'}"}
            self.write_message( json.dumps(returnMessage))
        except WebSocketClosedError:
            logger.error("Websocket connection disconnected")
            raise
        except:
            self.AC3.reportFatalError()
