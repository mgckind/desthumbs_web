import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import pandas as pd
import os, uuid
import Settings
import time
import glob
import json

class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")

class DownloadHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        title = self.get_argument("title")
        print '+-+-+-+-',title
        user_folder=os.path.join(Settings.UPLOADS,self.current_user.replace('\"','')) + '/'

        filegz=user_folder+'results/%s.tar.gz' % title
        if os.path.exists(filegz):
            self.set_status(200)
            self.flush()
        else:
            os.chdir(user_folder+'results/')
            os.system("tar -zcf %s %s*" % (filegz, title)) 
            os.chdir(os.path.dirname(__file__))
        
            self.set_status(200)
            self.flush()
        self.finish()