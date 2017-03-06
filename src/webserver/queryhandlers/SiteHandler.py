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


class SiteHandler(BaseHandler.BaseHandler):
    '''
    Returns the legacy site for controlling things
    '''
    @ServerHelpers.isLoggedIn() 
    def get(self):
        '''
        Returns the main web page or makes people log in.
        '''
        logger.debug("IndexHandler: GET")
        self.render("static/index.html", port=SERVER_PORT)

