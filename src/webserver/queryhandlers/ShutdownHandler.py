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

logger = logging.getLogger(__name__)

class ShutdownHandler(BaseHandler.BaseHandler):
    '''
    Shuts down robot if people are logged in
    '''
    def initialize( self, AC3 ):
        self.AC3 = AC3

    @ServerHelpers.isLoggedIn() 
    def get(self):
        logger.debug("ShutdownHandler: GET")
        self.write({'status':'shutting down'})
        self.finish()
        self.AC3.shutdown( )


