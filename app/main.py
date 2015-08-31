#Main
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import Settings
from tornado.options import define, options
import login
import test
import readfile
import results

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
            (r"/", login.MainHandler),
            (r"/auth/login/", login.AuthLoginHandler),
            (r"/auth/logout/", login.AuthLogoutHandler),
            (r"/test/", test.TestHandler),
            (r"/list/", login.MainHandler),
            (r"/readfile/", readfile.FileHandler),
            (r"/results/", results.DisplayHandler),
            (r"/deslabs", tornado.web.RedirectHandler,
        dict(url="http://deslabs.ncsa.illinois.edu/")),
        ]
        settings = {
            "template_path":Settings.TEMPLATE_PATH,
            "static_path":Settings.STATIC_PATH,
            "debug":Settings.DEBUG,
            "cookie_secret": Settings.COOKIE_SECRET,
            "login_url": "/auth/login/"
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
