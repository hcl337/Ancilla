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

class LoginHandler(BaseHandler.BaseHandler):


    def post(self):

        displayRequestDetails( self )

        # Load the password from the JSON body and deal with
        # errors if parts are missing
        password = ''
        try: 
            body = json.loads( self.request.body )
            logger.debug("Got body of login: " + str(body))
        except Exception as e: 
            logger.debug("Error parsing password: " + str(e))
            body = {}

        if 'password' in body:
            password = body['password']
        # Or take it from the URL if it isn't in the body
        else:
            password = self.get_argument("password", "")

        if len(password) == 0:
            self.set_status(401)
            self.write({'error':'no password specified'})
            return

        if hashlib.sha512(password).hexdigest() == ServerHelpers.ENCRYPTED_PASSWORD:
            setServerCookie(self)
            self.write({'status':'success'})
        else:
            clearServerCookie(self)
            self.set_status(401)
            self.write({'error':'incorrect password'})


    def put(self):
        return self.post()


    def get(self):
        return self.post()


