import tornado

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

