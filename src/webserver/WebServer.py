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
from tornado.ioloop import PeriodicCallback
from tornado.websocket import WebSocketClosedError

import cv2 as cv
logger = logging.getLogger(__name__)


SERVER_FILE_ROOT = os.path.normpath(os.path.dirname(__file__) + "/static")
DOC_PATH = os.path.join(SERVER_FILE_ROOT, "../../../API.md")

COOKIE_NAME = "AC-3"

port = 8888

# PASSWORD
# To update the password, run this in the directory with password.txt and it will ask you to do a new password
# python -c "import hashlib; import getpass; print(hashlib.sha512(getpass.getpass())).hexdigest()" > password.txt
with open(os.path.join(SERVER_FILE_ROOT + "/..", "password.txt")) as in_file:
    PASSWORD = in_file.read().strip()




class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        '''
        Returns the main web page or makes people log in.
        '''
        logger.debug("IndexHandler: GET")
        if not self.get_secure_cookie(COOKIE_NAME):
            self.redirect("/login")
        else:
            self.render("static/index.html", port=port)


class ShutdownHandler(tornado.web.RequestHandler):

    def initialize( self, AC3 ):
        self.AC3 = AC3

    def get(self):
        logger.debug("ShutdownHandler: GET")
        if not self.get_secure_cookie(COOKIE_NAME):
            self.redirect("/login")
        else:
            self.write("Shutting down AC3....")
            self.finish()
            self.AC3.shutdown( )


class Docs(tornado.web.RequestHandler):

    doc = ""

    def initialize( self ):
        with open( DOC_PATH ) as f:
            with open( os.path.join(SERVER_FILE_ROOT,'style/markdown-outer.html') ) as outer:
                words =  gfm.markdown( f.read() )

                # Make code format correctly
                words = words.replace('</code></p>', '</code></pre>')
                words = words.replace('<p><code>', '<pre><code>')
                # Get rid of the js tags on it
                words = words.replace('<code>js', '<code>')

                self.doc = outer.read().replace("{{MARKDOWN}}", words) 


    def get(self):
        if not self.get_secure_cookie(COOKIE_NAME):
            self.redirect("/login")
        else:
            self.write( self.doc )



class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        logger.debug("LoginHandler: GET")
        self.render("static/login.html")

    def post(self):
        password = self.get_argument("password", "")
        if hashlib.sha512(password).hexdigest() == PASSWORD:
            self.set_secure_cookie(COOKIE_NAME, str(time.time()))
            self.redirect("/")
        else:
            time.sleep(1)
            self.redirect(u"/login?error")


from handlers import *

class WebSocket(tornado.websocket.WebSocketHandler):

    # Reference to our movement object
    AC3 = None

    def initialize( self, AC3 ):
        self.AC3 = AC3

        try:
            # Add all of our websocket message handlers here
            self.__registerMessageHandler( SendEnvironmentCameraHandler.SendEnvironmentCameraHandler( self, AC3 ) )
            self.__registerMessageHandler( SendFocusCameraHandler.SendFocusCameraHandler( self, AC3 ) )
            self.__registerMessageHandler( SendStateHandler.SendStateHandler( self, AC3 ) )
            self.__registerMessageHandler( SetFocusCameraTrackingRegionOfInterestHandler.SetFocusCameraTrackingRegionOfInterestHandler( self, AC3 ) )
            self.__registerMessageHandler( SetServoPosition.SetServoPosition( self, AC3 ) )
            self.__registerMessageHandler( ShutdownHandler.ShutdownHandler( self, AC3 ) )

        except:
            AC3.reportFatalError( )



    def open(self):
        '''
        Only open if we are already signed in

        '''
        if not self.get_secure_cookie(COOKIE_NAME):
            return None



    messageHandlers = []

    def __registerMessageHandler( self, handler ):

        self.messageHandlers.append( handler )



    def on_close( self ):
        '''
        When they request a close or we are disconnected
        make sure that we stop all of the data which was
        coming in

        '''
        for handler in self.messageHandlers:
            handler.stopHandling( )



    def on_message(self, message):

        logger.debug("Received Websocket Message: " + str(message))
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



class AC3Server( ):

    AC3 = None

    def __init__( self, AC3 ):

        logger.info("Creating Web Server...")

        self.AC3 = AC3

        self.__tryToShutDownOldServer( )

        # Link up all the handlers 
        handlers = [
            (r"/", IndexHandler), \
            (r"/login", LoginHandler),\
            (r"/shutdown", ShutdownHandler, {'AC3': AC3}),\
            (r"/websocket", WebSocket, {'AC3': AC3}), \
            (r"/docs", Docs ), \
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': SERVER_FILE_ROOT})]

        self.application = tornado.web.Application(handlers, cookie_secret=PASSWORD)

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
                opener.addheaders.append(('Cookie', COOKIE_NAME + '=' + PASSWORD))
                f = opener.open("http://localhost:" + str(port) + "/shutdown")
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
        logger.info("Starting WebServer on port " + str(port))
        self.application.listen(port)
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
        tornado.ioloop.IOLoop.instance().stop()



