import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")

class TestHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("test3.html")

