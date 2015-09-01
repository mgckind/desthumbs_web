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
        xs = self.get_argument("xsize")
        print '+-+-+-+-',xs
        ys = self.get_argument("ysize")
        print '+-+-+-+-',ys
        check = self.get_argument("check")
        print '+-+-+-+-',check
        print self.current_user
        fileinfo = self.request.files["csvfile"][0]
        print fileinfo['filename']
        fname = fileinfo['filename']
        print fileinfo['content_type']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4()) + extn
        user_folder=os.path.join(Settings.UPLOADS,self.current_user.replace('\"','')) + '/'
        
        os.system('rm -f '+user_folder+'*.*')
        os.system('rm -rf '+user_folder+'results/')
        
        fh = open( user_folder + cname, 'w')
        fh.write(fileinfo['body'])
        fh.close()
        #RUN DESTHUMBS
        comm = "makeDESthumbs  %s --user demo_user --password user_demo --MP --outdir=%s" % (user_folder + cname, user_folder+'results/')
        if xs != "": comm += ' --xsize %s ' % xs
        if ys != "": comm += ' --ysize %s ' % ys
        print comm
        os.system(comm)
        mypath = '/static/uploads/'+self.current_user.replace('\"','')+'/results/'

        tiffiles=glob.glob(user_folder+'results/*.tif')
        titles=[]
        pngfiles=[]
        Ntiles = len(tiffiles)
        for f in tiffiles:
            title=f.split('/')[-1][:-4]
            os.system("convert %s %s.png" % (f,f))
            titles.append(title)
            pngfiles.append(mypath+title+'.tif.png')
       
        os.chdir(user_folder)
        os.system("tar -zcf results/all.tar.gz results/") 
        os.chdir(os.path.dirname(__file__))
        if os.path.exists(user_folder+"list.json"): os.remove(user_folder+"list.json")
        with open(user_folder+"list.json","w") as outfile:
            json.dump([dict(name=pngfiles[i],title=titles[i], size=Ntiles) for i in range(len(pngfiles))], outfile, indent=4)

        self.set_status(200)
        self.flush()
        self.finish()
