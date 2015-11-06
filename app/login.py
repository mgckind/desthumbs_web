import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import Settings
import cx_Oracle
import os
from Settings import mysession


dbConfig0 = Settings.dbConfig()
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
        kwargs = {'host': dbConfig0.host, 'port': dbConfig0.port, 'service_name': database}
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
            self.set_current_user(username, password)
            newfolder = os.path.join(Settings.UPLOADS,username)
            if not os.path.exists(newfolder):
                os.mkdir(newfolder)
            self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape(err)
            self.redirect(u"/auth/login/" + error_msg)

    def set_current_user(self, user, passwd):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user), expires_days = None)
            self.set_secure_cookie("pass", tornado.escape.json_encode(passwd), expires_days = None)
        else:
            self.clear_cookie("user")
            self.clear_cookie("pass")



class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("pass")
        self.redirect(self.get_argument("next", "/"))



