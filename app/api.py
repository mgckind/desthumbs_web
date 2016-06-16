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
import Settings
import cx_Oracle
import pandas as pd
import numpy as np
import os, uuid
import datetime
import dtasks
import json
from Settings import mysession
from results import humantime
from results import update_job_json
from expiringdict import ExpiringDict
import binascii
import hashlib

dbConfig0 = Settings.dbConfig()
ddbb= "desoper"
float_input = ['ra','dec','xsize','ysize']

tokens = ExpiringDict(max_len=200, max_age_seconds=120)

class infoP(object):
    def __init__(self, uu, pp):
        self._uu=uu
        self._pp=pp

def check_permission(password, username, database='desoper'):
    kwargs = {'host': dbConfig0.host, 'port': dbConfig0.port, 'service_name': database}
    dsn = cx_Oracle.makedsn(**kwargs)
    try:
        dbh = cx_Oracle.connect(username, password, dsn=dsn)
        dbh.close()
        return True,""
    except Exception as e:
        error = str(e).strip()
        return False,error

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")



class TokenHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        response = { k: self.get_argument(k) for k in self.request.arguments }
        response2 = {'status':'error', 'message':''}
        response3={}
        for k in response.keys():
            response2[k.lower()]=response[k]
        if 'token' in response2:
            ttl = tokens.ttl(response2['token'])
            if ttl is None:
                response2['status']='error'
                response2['message']='Token does not exist ot it expired'
            else:
                response2['status'] = 'ok'
                response2['message'] = 'Token is valid for %s seconds' % str(round(ttl))
            self.write(response2)
            self.set_status(200)
            self.flush()
            self.finish()
            return
                
        if 'username' in response2:
            if 'password' not in response2:
                response2['message'] = 'Need password'
            else:
                user = response2['username']
                passwd = response2['password']
                check,msg = check_permission(passwd, user)
                if check:
                    response2['status']='ok'
                    newfolder = os.path.join(Settings.UPLOADS,user)
                    user_folder = newfolder + '/'
                    if not os.path.exists(newfolder):
                        os.mkdir(newfolder)
                else:
                    response2['message']=msg
        else:
            response2['message'] = 'Need username'
        
        if response2['status'] == 'ok':
            response2['message'] = 'Token created, expiration is 24 hours'
            #temp = binascii.hexlify(os.urandom(64))
            temp = hashlib.sha1(os.urandom(64)).hexdigest()
            tokens[temp] = [user,passwd]
            response3['token']=temp 
        response3['status']=response2['status']
        response3['message']=response2['message']
        self.write(response3)
        self.set_status(200)
        self.flush()
        self.finish()
       



class ApiHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        response = { k: self.get_argument(k) for k in self.request.arguments }
        response2 = {'status':'error', 'message':''}
        response3={}
        for k in response.keys():
            rs = response[k].replace('[','')
            k = k.lower()
            rs = rs.replace(']','')
            if k in float_input:
                response2[k]=[float(i) for i in rs.split(',')]
            else:
                response2[k] = rs
        if 'token' in response2:
            auths = tokens.get(response2['token'])
            if auths is None:
                response2['message'] = 'Token does not exist or it expired'
            else:
                user = auths[0]
                passwd = auths[1]
                newfolder = os.path.join(Settings.UPLOADS,user)
                user_folder = newfolder + '/'
                if not os.path.exists(newfolder):
                    os.mkdir(newfolder)
                response2['status'] = 'ok'
        if 'username' in response2:
            if 'password' not in response2:
                response2['message'] = 'Need password'
            else:
                user = response2['username']
                passwd = response2['password']
                check,msg = check_permission(passwd, user)
                if check:
                    response2['status']='ok'
                    newfolder = os.path.join(Settings.UPLOADS,user)
                    user_folder = newfolder + '/'
                    if not os.path.exists(newfolder):
                        os.mkdir(newfolder)
                else:
                    response2['message']=msg
        else:
            if 'token' not in response2:
                response2['message'] = 'Need username'
        if response2['status'] == 'ok':
            ra = response2['ra']
            dec = response2['dec']
            if len(ra) != len(dec):
                response2['status']='error'
                response2['message'] = 'RA and DEC arrays must have same dimensions'
            xs = np.ones(len(ra))
            ys = np.ones(len(ra))
            if response2['status'] == 'ok':
                if 'xsize' in response2:
                    xs_read = response2['xsize']
                    if len(xs_read) == 1 : xs=xs*xs_read
                    if len(xs) >= len(xs_read): xs[0:len(xs_read)] = xs_read
                    else: xs = xs_read[0:len(xs)]
                if 'ysize' in response2:
                    ys_read = response2['ysize']
                    if len(ys_read) == 1 : ys=ys*ys_read
                    if len(ys) >= len(ys_read): ys[0:len(ys_read)] = ys_read
                    else: ys = ys_read[0:len(ys)]
                listonly = ''
                sendemail=''
                cname = str(uuid.uuid4()) + '.csv'
                df = pd.DataFrame(np.array([ra,dec,xs,ys]).T,columns=['RA','DEC','XSIZE','YSIZE'])
                df.to_csv(newfolder+'/'+cname,sep=',',index=False)
                del df
                xs = ''
                ys = ''
                infP=infoP(user, passwd) 
                now = datetime.datetime.now()
                siid = cname[:-4]
                tiid = user+'__'+cname[:-4]+'_{'+now.ctime()+'}'
                if 'email' in response2:
                    sendemail = 'yes'
                    toemail = response2['email']
                if sendemail == 'yes':
                    run=dtasks.desthumb.apply_async(args=[user_folder + cname, infP, user_folder+'results/'+siid+'/', xs,ys, siid, tiid, user_folder, listonly], task_id=tiid, link=dtasks.send_note.si(user, tiid, toemail))
                    response2['message'] = 'Job %s submitted. Email sent to %s on completion' % (siid, toemail) 
                    response3['job'] = siid 
                else:
                    run=dtasks.desthumb.apply_async(args=[user_folder + cname, infP, user_folder+'results/'+siid+'/', xs,ys, siid ,tiid,user_folder, listonly], task_id=tiid)
                    response2['message'] = 'Job %s submitted.' % (siid)
                    response3['job'] = siid 

        response3['status']=response2['status']
        response3['message']=response2['message']
        self.write(response3)
        self.set_status(200)
        self.flush()
        self.finish()


class ApiJobHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        response = { k: self.get_argument(k) for k in self.request.arguments }
        response2 = {'status':'error', 'message':''}
        response3={}
        for k in response.keys():
            rs = response[k]
            k = k.lower()
            response2[k] = rs
        if 'username' in response2:
            if 'password' not in response2:
                response2['message'] = 'Need password'
            else:
                user = response2['username']
                passwd = response2['password']
                check,msg = check_permission(passwd, user)
                if check:
                    response2['status']='ok'
                    newfolder = os.path.join(Settings.UPLOADS,user)
                    user_folder = newfolder + '/'
                else:
                    response2['message']=msg
        else:
            response2['message'] = 'Need username'

        if response2['status'] == 'ok':
            r=redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
            all_tasks = r.keys()
            _ = update_job_json(all_tasks, user)
            jfile = user_folder + 'jobs.json'
            with open(jfile,'r') as jsonfile:
                data = json.load(jsonfile)
            jobs=[j['job'][j['job'].index('__')+2:j['job'].index('_{')] for j in data]
            #response3['jobs']=jobs
            try:
                jobid = response2['jobid']
            except:
                jobid = '0'
            if jobid in jobs:
                status = data[jobs.index(jobid)]['status']
                if status == 'SUCCESS':
                    response2['status'] = 'ok'
                    response2['message'] = 'Job completed.'
                    list_file = user_folder + 'results/'+jobid+'/list_all.txt'
                    with open(list_file) as f:
                        links = f.read().splitlines() 
                    response2['status'] = 'ok'
                    response3['links'] = links
                elif status == 'PENDING':
                    response2['status'] = 'error'
                    response2['message'] = 'Job still running'
                else:
                    response2['status'] = 'error'
                    response2['message'] = 'Job failed'
            else:
                response2['status'] = 'error'
                response2['message'] = 'Job Id not found, please use correct jobid'

        response3['status']=response2['status']
        response3['message']=response2['message']
        self.write(response3)
        self.set_status(200)
        self.flush()
        self.finish()


