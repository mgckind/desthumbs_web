from __future__ import absolute_import

import subprocess
from celery import Celery
import time
import tornado.web
import smtplib
import urllib
import glob
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")


celery = Celery('dtasks')
#celery = Celery('dtasks', backend='redis://127.0.0.1:6379/0', broker='redis://127.0.0.1:6379/0')
#celery.conf.CELERY_TASK_RESULT_EXPIRES = 0
celery.config_from_object('celeryconfig')

@celery.task
def desthumb(inputs, infoP, outputs,xs,ys, siid, tiid, user_folder, listonly):
    com =  "makeDESthumbs  %s --user %s --password %s --MP --outdir=%s" % (inputs, infoP._uu, infoP._pp, outputs)
    if xs != "": com += ' --xsize %s ' % xs
    if ys != "": com += ' --ysize %s ' % ys
    com2 = '/root/DES/desth/app/task2 30'
    #A=BaseHandler()
    #print(A.current_user)
    oo = subprocess.check_output([com],shell=True)
    mypath = '/static/uploads/'+infoP._uu+'/results/'+siid+'/'


    if listonly == 'yes':
        if os.path.exists(user_folder+"results/"+siid+"/list.json"): os.remove(user_folder+"results/"+siid+"/list.json")
        with open(user_folder+"results/"+siid+"/list.json","w") as outfile:
            json.dump('', outfile, indent=4)
    else:
        tiffiles=glob.glob(user_folder+'results/'+siid+'/*.tif')
        titles=[]
        pngfiles=[]
        Ntiles = len(tiffiles)
        for f in tiffiles:
            title=f.split('/')[-1][:-4]
            os.system("convert %s %s.png" % (f,f))
            titles.append(title)
            pngfiles.append(mypath+title+'.tif.png')
       
        os.chdir(user_folder)
        os.system("tar -zcf results/"+siid+"/all.tar.gz results/"+siid+"/") 
        os.chdir(os.path.dirname(__file__))
        if os.path.exists(user_folder+"results/"+siid+"/list.json"): os.remove(user_folder+"results/"+siid+"/list.json")
        with open(user_folder+"results/"+siid+"/list.json","w") as outfile:
            json.dump([dict(name=pngfiles[i],title=titles[i], size=Ntiles) for i in range(len(pngfiles))], outfile, indent=4)


    # writing files for wget
    allfiles = glob.glob(user_folder+'results/'+siid+'/*.*')
    Fall = open(user_folder+'results/'+siid+'/list_all.txt','w')
    prefix='http://desdev2.cosmology.illinois.edu/static'
    for ff in allfiles:
        if (ff.find('all.tar.gz')==-1 & ff.find('list.json')==-1): Fall.write(prefix+ff.split('static')[-1]+'\n')
    Fall.close()

    return oo

@celery.task
def send_note(user, jobid, toemail):
    print 'Task was completed' 
    print 'I will notify %s to its email address :  %s' % (user, toemail)
    fromemail = 'devnull@ncsa.illinois.edu'
    s = smtplib.SMTP('smtp.ncsa.illinois.edu')
    link = "http://desdev2.cosmology.illinois.edu/results/%s" % jobid
    link2 = urllib.quote(link.encode('utf8'),safe="%/:=&?~#+!$,;'@()*[]")
    jobid2=jobid[jobid.find('__')+2:jobid.find('{')-1]



    html = """\
    <html>
    <head></head>
    <body>
         <b> Please do not reply to this email</b> <br><br>

        <p>The job %s was completed, <br> 
        the results can be retrieved from this <a href="%s">link</a> .
        </p><br>

        <p> DESDM Thumbs generator</p><br>

        <p> PS: This is the full link to the results: <br>
        %s </p>

    </body>
    </html>
    """ % (jobid2, link2, link2)

    MP1 = MIMEText(html, 'html')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Job %s is completed' % jobid2
    #msg['From'] = fromemail
    msg['From'] = formataddr((str(Header('DESDM Thumbs', 'utf-8')), fromemail))
    msg['To'] = toemail

    msg.attach(MP1)


    s.sendmail(fromemail, toemail, msg.as_string())
    s.quit()
    return "Email Sent to %s" % toemail
