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


class DocsHandler(BaseHandler.BaseHandler):
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
                self.set_status(404)
                self.write({"error":"no documentation file found with this name: " + str(fileName)})
                return

        self.write( self.docs[fileName] )

