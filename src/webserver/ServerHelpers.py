import json
import logging
import os
import tornado
from random import randint

logger = logging.getLogger(__name__)

################################################################################
# CONSTANTS
SERVER_COOKIE_NAME = "AC-3"
SERVER_FILE_ROOT = os.path.normpath(os.path.dirname(__file__) + "/static")
DOC_PATH = os.path.join(SERVER_FILE_ROOT, "../../../")
README_DOC_PATH = os.path.join(SERVER_FILE_ROOT, "../../../README.md")
SERVER_PORT = 8888
ENCRYPTED_PASSWORD = None
################################################################################



class BaseHandler(tornado.web.RequestHandler):
    '''
    This allows us to do cross-domain talking with Javascript
    '''
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", str(self.request.headers.get('Origin')))
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, DELETE, OPTIONS, GET')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()



def loadEncryptedPassword( ):
    '''
    PASSWORD
    To update the password, run this in the directory with password.txt and it will ask you to do a new password
    python -c "import hashlib; import getpass; print(hashlib.sha512(getpass.getpass())).hexdigest()" > password.txt
    '''
    with open(os.path.join(SERVER_FILE_ROOT + "/../../../parameters", "password.txt")) as in_file:
        PASSWORD = in_file.read().strip()

    return PASSWORD

ENCRYPTED_PASSWORD = loadEncryptedPassword()


def setServerCookie( self ):
    '''
    Helper to set our custom cookie allowing us to parse it
    '''
    cookie = {"token": str(randint(100000,1000000))}    
    self.set_secure_cookie(SERVER_COOKIE_NAME, json.dumps(cookie))



def clearServerCookie( self ):
    '''
    Removes the cookie if we had one
    '''
    self.clear_cookie(SERVER_COOKIE_NAME)



def getServerCookie( self ):
    '''
    Returns None if there is no cookie or it is not parsable.

    Returns JSON object with "token" and other elements if it
    exists.
    '''
    cookie = self.get_secure_cookie(SERVER_COOKIE_NAME)



    try:
        cookie = json.loads(cookie)    
    # If it is blank or not JSON, return none for cookie
    except: 
        return None

    if not type(cookie) == dict:
        return None

    # If when it was decrypted it didn't have 'token', return none
    if not ('token' in cookie):
        return None

    return cookie



def isLoggedIn(*params):
    """
    Cookie security decorator for HTTP methods(get, post, put,etc)
    Usage:
        @CookieSecurity.auth('grpA','grpB')  #only allow users who are in 'grpA'&'grpB' to access
        def get(self):
            pass
    """
    def __auth(func):

        #@wraps(func)
        def __decorator(self, *args, **kwargs):

            displayRequestDetails( self )

            cookie = getServerCookie( self )

            if cookie is None:
                self.set_header("Content-Type", "application/json") 
                self.set_status(401)
                docURL = self.request.protocol + "://" + self.request.host + "/docs/api"
                message = "Please access the api documentation to learn how to log in"
                self.write( json.dumps({'error':"not logged in", "api_docs": docURL, "message": message}))
                return

            return func(self, *args, **kwargs)

        return __decorator
    return __auth



def displayRequestDetails( self ):
    '''
    Pretty prints each of our API request to the logger with correct details
    '''
    logger.debug("")
    logger.debug("## ------------------------------  " + str(self.__class__.__name__))
    logger.debug("  host:       " + self.request.host)
    logger.debug("  uri:        " + self.request.uri)
    logger.debug("  method:     " + self.request.method)
    if 'Cookie' in self.request.headers:
        cookie = self.request.headers['Cookie']
        logger.debug("  auth:       " + str( len(cookie) > 20 ))
    else:
        logger.debug("  auth:       false")
       