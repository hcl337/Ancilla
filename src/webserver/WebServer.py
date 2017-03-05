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

#from RobotWebSocket import RobotWebSocket
import RobotWebSocket

# import ServerHelpers which has abstracted out all of our detail stuff to support
# the web server
from ServerHelpers import (BaseHandler, displayRequestDetails, SERVER_COOKIE_NAME, 
    isLoggedIn, loadEncryptedPassword, getServerCookie, setServerCookie, clearServerCookie,
    SERVER_PORT, SERVER_FILE_ROOT, DOC_PATH, README_DOC_PATH )
from handlers import *

logger = logging.getLogger(__name__)

import time
startupTime = str(time.strftime("%Y-%m-%d %H:%M"))
startTime = time.time()

class IndexHandler(BaseHandler):
    '''
    Return status=logged in if user has been logged in or 401 if they 
    are not logged in.
    '''
    @isLoggedIn()
    def get(self):

        global numConnections
        global clients

        cookie = getServerCookie( self )
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



class SiteHandler(BaseHandler):
    '''
    Returns the legacy site for controlling things
    '''
    @isLoggedIn() 
    def get(self):
        '''
        Returns the main web page or makes people log in.
        '''
        logger.debug("IndexHandler: GET")
        self.render("static/index.html", port=SERVER_PORT)



class ShutdownHandler(BaseHandler):
    '''
    Shuts down robot if people are logged in
    '''
    def initialize( self, AC3 ):
        self.AC3 = AC3

    @isLoggedIn() 
    def get(self):
        logger.debug("ShutdownHandler: GET")
        self.write({'status':'shutting down'})
        self.finish()
        self.AC3.shutdown( )



class Docs(BaseHandler):
    '''
    Handles any .md file in the base directory of the project
    '''

    docs = {}

    def loadFile( self, fileName ):
        with open( fileName ) as f:
            with open( os.path.join(SERVER_FILE_ROOT,'style/markdown-outer.html') ) as outer:
                words =  gfm.markdown( f.read() )

                # We need to update the paths in the .md files when hosting
                # them on the API because we aren't accessing files directly
                # but are instead looking at them through the separate API 
                # endpoints.
                #words = words.replace('README.md', '/docs/readme')
                #words = words.replace('API.md', '/docs/api')
                #words = words.replace('SETUP.md', '/docs/setup')

                # Make code format correctly
                words = words.replace('</code></p>', '</code></pre>')
                words = words.replace('<p><code>', '<pre><code>')
                # Get rid of the tags on it
                words = words.replace('<code>js', '<code>')
                words = words.replace('<code>sh', '<code>')

                self.docs[fileName] = outer.read().replace("{{MARKDOWN}}", words) 


    def get(self, fileName):
        if not( fileName in self.docs ):
            try:

                if not (fileName.endswith(".md")):
                    fileName = fileName.upper() + ".md"

                fileName = DOC_PATH + fileName

                logger.debug("Doc file to look for: " + fileName)
                self.loadFile( fileName )
            except Exception as e:
                logger.error( e )
                self.write({"error":"no documentation file found with this name: " + str(fileName)})
                return

        self.write( self.docs[fileName] )



class LogoutHandler(BaseHandler):

    @isLoggedIn() 
    def get(self):

        cookie = getServerCookie( self )
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
        clearServerCookie(self)

        self.write({'status':'successfully logged out', 'websocket_connections_closed': str(numClosed)})



ENCRYPTED_PASSWORD = loadEncryptedPassword()

class LoginHandler(BaseHandler):


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

        if hashlib.sha512(password).hexdigest() == ENCRYPTED_PASSWORD:
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






class AC3Server( ):

    AC3 = None

    def __init__( self, AC3 ):

        logger.info("Creating Web Server...")

        self.AC3 = AC3

        self.__tryToShutDownOldServer( )

        # Link up all the handlers 
        handlers = [
            (r"/", IndexHandler), \
            (r"/site", SiteHandler),\
            (r"/login", LoginHandler),\
            (r"/logout", LogoutHandler),\
            (r"/shutdown", ShutdownHandler, {'AC3': AC3}),\
            (r"/websocket", RobotWebSocket.RobotWebSocket, {'AC3': AC3}), \
            (r"/docs/([^/]+)$", Docs), \
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': SERVER_FILE_ROOT})]

        self.application = tornado.web.Application(handlers, cookie_secret=ENCRYPTED_PASSWORD)

        logger.info("Web Server creation complete...")


    def __tryToShutDownOldServer( self ):
        '''
        Pings the old server on this port to see if it exists and tell it to shut down
        so that we don't have multiple trying...
        
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
            logger.info("\tOld server disconnected: Bad status line")

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

        message = { "message": "shutdown", "reason": "server disabled"}

        for client in RobotWebSocket.clients:
            try: RobotWebSocket.client.write_message( message )
            except: pass

        tornado.ioloop.IOLoop.instance().stop()



