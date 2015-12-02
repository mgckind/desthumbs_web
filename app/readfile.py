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
import dtasks
import datetime
import stat


class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")

class infoP(object):
    def __init__(self, uu, pp):
        self._uu=uu
        self._pp=pp

class FileHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        user_folder=os.path.join(Settings.UPLOADS,self.current_user.replace('\"','')) + '/'
        #os.system('rm -f '+user_folder+'*.*')
        #os.system('rm -rf '+user_folder+'results/')
        check = self.get_argument("check")
        print '+-+-+-+-',check
        id1 = self.get_argument("id")
        print '+-+-+-+-',id1
        xs = self.get_argument("xsize")
        print '+-+-+-+-',xs
        ys = self.get_argument("ysize")
        print '+-+-+-+-',ys
        listonly = self.get_argument("listonly")
        print '+-+-+-+-',listonly

        sendemail = self.get_argument("sendemail")
        toemail = self.get_argument("toemail")
        if check == "file":
            fileinfo = self.request.files["csvfile"][0]
            print fileinfo['filename']
            fname = fileinfo['filename']
            print fileinfo['content_type']
            extn = os.path.splitext(fname)[1]
            cname = str(uuid.uuid4()) + extn
            fh = open( user_folder + cname, 'w')
            fh.write(fileinfo['body'])
            fh.close()
        if check == "manual":
            values = self.get_argument("values")
            cname = str(uuid.uuid4()) + '.csv'
            fh = open( user_folder + cname, 'w')
            fh.write("RA,DEC\n")
            fh.write(values)
            fh.close()
            print values
        
        
        #RUN DESTHUMBS
        loc_passw = self.get_secure_cookie("pass").replace('\"','')
        loc_user = self.get_secure_cookie("user").replace('\"','')
        infP=infoP(loc_user,loc_passw) 
        #comm = "makeDESthumbs  %s --user %s --password %s --MP --outdir=%s" % (user_folder + cname, loc_user, loc_passw, user_folder+'results/')
        #if xs != "": comm += ' --xsize %s ' % xs
        #if ys != "": comm += ' --ysize %s ' % ys
        #print comm
        #os.system(comm)
        now = datetime.datetime.now()
        siid = cname[:-4]
        tiid = loc_user+'__'+cname[:-4]+'_{'+now.ctime()+'}'
        if sendemail == 'yes':
            print 'Sending email to %s' % toemail
            run=dtasks.desthumb.apply_async(args=[user_folder + cname, infP, user_folder+'results/'+siid+'/', xs,ys, siid, tiid, user_folder, listonly], task_id=tiid, link=dtasks.send_note.si(loc_user, tiid, toemail))
        else:
            print 'Not sending email'
            run=dtasks.desthumb.apply_async(args=[user_folder + cname, infP, user_folder+'results/'+siid+'/', xs,ys, siid ,tiid,user_folder, listonly], task_id=tiid)

        self.set_status(200)
        self.flush()
        self.finish()
