import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")

class DisplayHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("results.html", username=self.current_user.replace('\"',''))

class DisplayOneHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        name = self.get_argument("path")
        title = self.get_argument("title")
        print name, title
        #self.render("results2.html", myimage=name)
        #error_msg = u"?name=" + tornado.escape.url_escape(name)
        #self.redirect(self.get_argument("next", "/results3/"+ error_msg))

class DisplayOneBigHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = self.get_argument("name")
        self.render("results2.html", myimage=name)