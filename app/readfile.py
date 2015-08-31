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

class FileHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        id1 = self.get_argument("id")
        print '+-+-+-+-',id1
        print self.current_user
        fileinfo = self.request.files["csvfile"][0]
        print fileinfo['filename']
        fname = fileinfo['filename']
        print fileinfo['content_type']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        user_folder=os.path.join(Settings.UPLOADS,self.current_user.replace('\"','')) + '/'
        fh = open( user_folder + cname, 'w')
        fh.write(fileinfo['body'])
        fh.close()
        #RUN DESTHUMBS
        comm = "makeDESthumbs  %s --user demo_user --password user_demo --MP --outdir=%s" % (user_folder + cname, user_folder)
        print comm
        os.system(comm)
        mypath = '/static/uploads/'+self.current_user.replace('\"','')+'/'

        tiffiles=glob.glob(user_folder+'*.tif')
        titles=[]
        pngfiles=[]
        for f in tiffiles:
            title=f.split('/')[-1][:-4]
            os.system("convert %s %s.png" % (f,f))
            titles.append(title)
            pngfiles.append(mypath+title+'.tif.png')
        
        with open(user_folder+"list.json","w") as outfile:
            json.dump([dict(name=pngfiles[i],title=titles[i]) for i in range(len(pngfiles))], outfile, indent=4)

        self.set_status(200)
        #self.redirect(self.get_argument("next", u"/results/"))
        #self.render("results.html")
        self.flush()
        self.finish()
