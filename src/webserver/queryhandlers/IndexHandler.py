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
from .. import ServerHelpers
#from ServerHelpers import (BaseHandler, displayRequestDetails, SERVER_COOKIE_NAME, 
#    isLoggedIn, getServerCookie, setServerCookie, clearServerCookie,
#    SERVER_PORT, SERVER_FILE_ROOT, DOC_PATH, README_DOC_PATH, ENCRYPTED_PASSWORD )
from .. import RobotWebSocket

logger = logging.getLogger(__name__)

startupTime = str(time.strftime("%Y-%m-%d %H:%M"))
startTime = time.time()


class IndexHandler(BaseHandler.BaseHandler):
    '''
    Return status=logged in if user has been logged in or 401 if they 
    are not logged in.
    '''
    @ServerHelpers.isLoggedIn()
    def get(self):

        global numConnections
        global clients

        cookie = ServerHelpers.getServerCookie( self )
        token = cookie['token']

        # Dynamically create the link to the API docs
        docURL = self.request.protocol + "://" + self.request.host + "/docs/api"

        # Calculate uptime
        elapsed_time = int(time.time() - startTime)
        elapsed_sec = int(round(elapsed_time) % 60)
        elapsed_min = int(round(elapsed_time/60) % 60)
        elapsed_hours = int(round(elapsed_time/60/60))

        # Calculate how many websocket connections exist for this
        numConnectionsForCookie = 0
        for client in RobotWebSocket.clients:
            if token in client:
                numConnectionsForCookie += 1

        timeAlive = str(elapsed_hours) + "h " + str(elapsed_min) + "m " + str(elapsed_sec) + "s"
        s = {"status":"logged in", "docs":docURL, "booted": startupTime, "uptime": timeAlive, 'your_connections': numConnectionsForCookie, 'total_connections':len(RobotWebSocket.clients)}
        self.write(s)
