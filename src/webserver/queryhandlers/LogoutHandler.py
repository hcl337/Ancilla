import os
import logging
import urllib2
import httplib
#import socket
#import base64
#import hashlib
import json
#import misaka
#import gfm
#from threading import Thread
#import tornado.web
#import tornado.websocket
#from random import randint
#from tornado.ioloop import PeriodicCallback
#from tornado.websocket import WebSocketClosedError
import time
import BaseHandler

logger = logging.getLogger(__name__)

from .. import ServerHelpers

class LogoutHandler(BaseHandler.BaseHandler):

    @ServerHelpers.isLoggedIn() 
    def get(self):

        cookie = ServerHelpers.getServerCookie( self )
        token = cookie['token']

        logger.info("Logging user out of server: " + token)

        # Close all websocket connections with this token
        numClosed = 0
        for client in clients:
            if token in client:
                logger.info("Closed websocket connection: " + client)
                try:
                    clients[client].close()
                except Exception as e: 
                    logger.info("Failed to close web socket client: " + str(e))
                numClosed += 1

        # Finally clear the cookie
        ServerHelpers.clearServerCookie(self)

        self.write({'status':'successfully logged out', 'websocket_connections_closed': str(numClosed)})

