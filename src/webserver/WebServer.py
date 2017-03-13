import os
import logging
import urllib2
import httplib
import socket
import base64
import hashlib
import time
import json
import gfm
from threading import Thread
import tornado.web
import tornado.websocket
from random import randint
from tornado.ioloop import PeriodicCallback
from tornado.websocket import WebSocketClosedError
import cv2 as cv

#from RobotWebSocket import RobotWebSocket
import RobotWebSocket

# import ServerHelpers which has abstracted out all of our detail stuff to support
# the web server
from ServerHelpers import (BaseHandler, displayRequestDetails, SERVER_COOKIE_NAME,
    isLoggedIn, getServerCookie, setServerCookie, clearServerCookie,
    SERVER_PORT, SERVER_FILE_ROOT, DOC_PATH, README_DOC_PATH, ENCRYPTED_PASSWORD )


from queryhandlers import IndexHandler
from queryhandlers import DocsHandler
from queryhandlers import LoginHandler
from queryhandlers import LogoutHandler
from queryhandlers import ShutdownHandler
from queryhandlers import SiteHandler


logger = logging.getLogger(__name__)




class AC3Server( ):
    '''
    Main web server which controls all handlers, websocket, etc
    '''

    AC3 = None

    def __init__( self, AC3 ):

        logger.info("Creating Web Server...")

        self.AC3 = AC3

        self.__tryToShutDownOldServer( )

        # Link up all the handlers
        self.handlers = [
            (r"/", IndexHandler.IndexHandler), \
            (r"/site", SiteHandler.SiteHandler),\
            (r"/login", LoginHandler.LoginHandler),\
            (r"/logout", LogoutHandler.LogoutHandler),\
            (r"/shutdown", ShutdownHandler, {'AC3': AC3}),\
            (r"/websocket", RobotWebSocket.RobotWebSocket, {'AC3': AC3}), \
            (r"/docs/([^/]+)$", DocsHandler.DocsHandler), \
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': SERVER_FILE_ROOT})]

        self.application = tornado.web.Application(self.handlers, cookie_secret=ENCRYPTED_PASSWORD)

        logger.info("Web Server creation complete...")


    def __tryToShutDownOldServer( self ):
        '''
        Pings the old server on this port to see if it exists and tell it to shut down
        so that we don't have multiple trying...

        Because we are multi-threaded, we could accidentally have this happen a lot.
        
        '''
        try:
            serverAlive = True
            while serverAlive:
                logger.info("\tTesting for old server...")
                opener = urllib2.build_opener()
                opener.addheaders.append(('Cookie', SERVER_COOKIE_NAME + '=' + ENCRYPTED_PASSWORD))
                f = opener.open("http://localhost:" + str(SERVER_PORT) + "/shutdown")
                logger.info("\tWaiting for old server to exit...")
                time.sleep(5)
        except urllib2.HTTPError as e:
            logger.info("\tHTTP: " + str(e))
        except urllib2.URLError as e:
            logger.info("\tNo old server found" + str(e))
        except socket.error as e:
            logger.info("\tOld server disconnected")
        except httplib.BadStatusLine as e:
            logger.info("\tOld server disconnected")

        time.sleep(1)




    def __ioloop( self ):
        logger.info("Starting WebServer on port " + str(SERVER_PORT))
        self.application.listen(SERVER_PORT)
        tornado.ioloop.IOLoop.instance().start()



    def enable( self ):
        logger.info("Enabling web server")

        serverThread = Thread(target=self.__ioloop)
        # Make sure it dies if the whole app dies
        serverThread.setDaemon(True)
        # Need to actually start it running where it calls the update function
        serverThread.start()

        logger.info("Completed enabling web server")



    def disable( self ):

        logger.debug("Disabling Web Server. " + str(len(RobotWebSocket.clients)) + " clients connected.")


        for clientName in RobotWebSocket.clients:
            client = RobotWebSocket.clients[clientName]
            logger.debug("Shutting down handlers for: " + client.uniqueClientToken)
            client.stopHandlingMessages()
            try:
                message = { "type": "SHUTDOWN", "reason": "server disabled"}
                RobotWebSocket.client.write_message( message )
            except: pass

        tornado.ioloop.IOLoop.instance().stop()



