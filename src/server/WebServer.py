import os
import logging
import urllib2
import httplib
import socket
import base64
import hashlib
import time
import json
from threading import Thread
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback

logger = logging.getLogger(__name__)


SERVER_FILE_ROOT = os.path.normpath(os.path.dirname(__file__) + "/assets")

COOKIE_NAME = "AC-3"

port = 8888

# PASSWORD
# To update the password, run this in the directory with password.txt and it will ask you to do a new password
# python -c "import hashlib; import getpass; print(hashlib.sha512(getpass.getpass())).hexdigest()" > password.txt
with open(os.path.join(SERVER_FILE_ROOT + "/..", "password.txt")) as in_file:
    PASSWORD = in_file.read().strip()




class IndexHandler(tornado.web.RequestHandler):

    def get(self):

        logger.debug("IndexHandler: GET")
        if not self.get_secure_cookie(COOKIE_NAME):
            self.redirect("/login")
        else:
            self.render("assets/index.html", port=port)


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


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        logger.debug("LoginHandler: GET")
        self.render("assets/login.html")

    def post(self):
        password = self.get_argument("password", "")
        if hashlib.sha512(password).hexdigest() == PASSWORD:
            self.set_secure_cookie(COOKIE_NAME, str(time.time()))
            self.redirect("/")
        else:
            time.sleep(1)
            self.redirect(u"/login?error")


class WebSocket(tornado.websocket.WebSocketHandler):

    # Reference to our movement object
    AC3 = None

    def initialize( self, AC3 ):
        self.AC3 = AC3


    def on_message(self, message):
        logger.debug("WebSocket: on_message")
        """Evaluates the function pointed to by json-rpc."""

        if message == "read_state":
            self.state_loop = PeriodicCallback(self.stateLoop, 100)
            self.state_loop.start()
        # Start an infinite loop when this is called
        elif message == "read_camera":
            pass
            #self.camera_loop = PeriodicCallback(self.loop, 10)
            #self.camera_loop.start()

        # Extensibility for other methods
        else:
            print("Unsupported function: " + message)

    def stateLoop(self):
        try:
            data = {
                "movement": self.AC3.movement.getState(),
                "memory": self.AC3.reasoning.getMemory()
            }
            self.write_message(json.dumps(data, indent=4))
        except tornado.websocket.WebSocketClosedError as e:
            logger.error("WebsocketError in stateloop WebSocket: " + str(e))
            self.state_loop.stop()
        except Exception as e:
            self.state_loop.stop()
            logger.error("Error in stateloop WebSocket: " + str(e))



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
                time.sleep(1)
        except urllib2.HTTPError as e:
            logger.info("\tHTTP: " + str(e))
        except urllib2.URLError as e:
            logger.info("\tNo old server found" + str(e))
        except socket.error as e:
            logger.info("\tOld server disconnected")
        except httplib.BadStatusLine as e:
            logger.info("\tOld server disconnected: Bad status line")



    def __ioloop( self ):
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



