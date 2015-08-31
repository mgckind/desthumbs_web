import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import Settings
import cx_Oracle
import os


dbConfig = Settings.dbConfig()
ddbb= "dessci"
class BaseHandler(tornado.web.RequestHandler):
 
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = tornado.escape.xhtml_escape(self.current_user)
        self.render("main.html", name=self.current_user.replace('\"',''), db=ddbb)

class AuthLoginHandler(BaseHandler):
    global ddbb
    def get(self):
        try:
            errormessage = self.get_argument("error")
        except:
            errormessage = ""
        self.render("login.html", errormessage = errormessage)

    def check_permission(self, password, username, database):
        kwargs = {'host': dbConfig.host, 'port': dbConfig.port, 'service_name': database}
        dsn = cx_Oracle.makedsn(**kwargs)
        try:
            dbh = cx_Oracle.connect(username, password, dsn=dsn)
            dbh.close()
            return True,""
        except Exception as e:
            error = str(e).strip()
            return False,error


    def post(self):
        global ddbb
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        ddbb = self.get_argument("database", "")
        auth,err = self.check_permission(password, username, ddbb)
        if auth:
            self.set_current_user(username)
            newfolder = os.path.join(Settings.UPLOADS,username)
            if not os.path.exists(newfolder):
                os.mkdir(newfolder)
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape(err)
            self.redirect(u"/auth/login/" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")



class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))



