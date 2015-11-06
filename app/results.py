import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from celery.result import AsyncResult
from celery.task.control import inspect
from celery.task.control import revoke
import redis
import json
import os
import Settings
import datetime
import time
import numpy
import shutil

def humantime(s):
    if s < 60:
        return "%d seconds ago" % s
    else:
        mins = s/60
        secs = s % 60
        if mins < 60:
            return "%d minutes and %d seconds ago" % (mins, secs)
        else:
            hours = mins/60
            mins  = mins % 60
            if hours < 24:
                return "%d hours and %d minutes ago" % (hours,mins)
            else:
                days = hours/24
                hours = hours % 24
                return "%d days and %d hours ago" % (days, hours)

class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")

class DisplayHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, slug):
        print slug
        res = AsyncResult(slug)
        if res.ready():
            self.render("results.html", username=self.current_user.replace('\"',''), jobid=slug)
        else:
            self.render("results.html", username=self.current_user.replace('\"',''), jobid='00')

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

class StatusHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, slug):
        res = AsyncResult(slug)
        if res.ready():
            self.render("log.html", joblog=res.result.replace('\n','<br>'))
            #self.write(res.result.replace('\n', '<br>'))
        else:
            #self.write('Running')
            self.render("log.html", joblog="Running")

class StatusUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        loc_user = self.get_secure_cookie("user").replace('\"','')
        r=redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        all_tasks = r.keys()
        #self.write('COMPLETED <br>')
        completed = {}
        completed2 = {}
        jobnames = []
        jobstatus = []
        jobdate = []
        jobelapsed = []
        today = datetime.datetime.now()
        for t in all_tasks:
            if t.find(loc_user) > -1:
                t=t.replace("celery-task-meta-",'')
                stime=t[t.find('{')+1:-1]
                cc = AsyncResult(t)
                completed[t]=cc.status
                jobnames.append(t)
                jobstatus.append(cc.status)
                jobdate.append(stime)
                ftime = datetime.datetime.strptime(stime,'%a %b %d %H:%M:%S %Y')
                jobelapsed.append((today-ftime).seconds)
                
                #self.write( '<a href="/status/'+t+'">'+t+'</a>  : ' + cc.status + '<br>')
        i=inspect()
        aa=i.active()
        #self.write('RUNNING <br>')
        running={}
        aa=aa[aa.keys()[0]]
        if len(aa) > 0:
            for i in range(len(aa)):
                t=aa[i]['id']
                stime=t[t.find('{')+1:-1]

                cc = AsyncResult(t)
                running[t] = cc.status
                jobnames.append(t)
                jobstatus.append(cc.status)
                jobdate.append(stime)
                ftime = datetime.datetime.strptime(stime,'%a %b %d %H:%M:%S %Y')
                jobelapsed.append((today-ftime).seconds)

                #self.write( '<a href="/status/'+t+'">'+t+'</a>  : ' + cc.status + '<br>')
        jobnames=numpy.array(jobnames)
        jobstatus=numpy.array(jobstatus)
        jobdate=numpy.array(jobdate)
        jobelapsed=numpy.array(jobelapsed)
        sort_time=numpy.argsort(jobelapsed)
        completed2['job']=jobnames
        completed2['status']= jobstatus
        username = self.current_user.replace('\"','')
        user_folder=os.path.join(Settings.UPLOADS,self.current_user.replace('\"','')) + '/'
        myjobs = user_folder+'jobs.json'
        with open(myjobs,"w") as outfile:
            json.dump([dict(job=jobnames[sort_time[i]],status=jobstatus[sort_time[i]], 
                time=jobdate[sort_time[i]], 
                elapsed=humantime(jobelapsed[sort_time[i]])) for i in range(len(jobnames))], outfile, indent=4)
        self.render("status.html", completed=completed, running=running, username=username, completed2=completed2)

                
class CancelHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        jobid = self.get_argument("jobname")
        print jobid
        loc_user = self.get_secure_cookie("user").replace('\"','')
        r=redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        revoke(jobid, terminate=True)
        self.set_status(200)
        self.flush()
        self.finish()

class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        jobid = self.get_argument("jobname")
        jobid2=jobid[jobid.find('__')+2:jobid.find('{')-1]
        user_folder=os.path.join(Settings.UPLOADS,self.current_user.replace('\"','')) + '/'
         
        os.chdir(user_folder+'results/')
        try:
            shutil.rmtree(jobid2+'/')
        except:
            pass 
        os.chdir(user_folder)
        os.remove(jobid2+'.csv')
        r=redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
        r.delete('celery-task-meta-'+jobid)        
        self.set_status(200)
        self.flush()
        self.finish()

      
