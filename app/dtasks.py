from __future__ import absolute_import

import subprocess
from celery import Celery
import time
import tornado.web
import smtplib
import urllib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

class BaseHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")


celery = Celery('dtasks', backend='redis://127.0.0.1:6379/0', broker='redis://127.0.0.1:6379/0')

@celery.task
def desthumb(inputs, user, passwd, outputs,xs,ys, notify):
    com =  "makeDESthumbs  %s --user %s --password %s --MP --outdir=%s" % (inputs, user, passwd, outputs)
    if xs != "": com += ' --xsize %s ' % xs
    if ys != "": com += ' --ysize %s ' % ys
    com2 = '/Users/Matias/Dropbox/DESDM/test_polymer/app/task2 30'
    #A=BaseHandler()
    #print(A.current_user)
    oo = subprocess.check_output([com2],shell=True)
    #print('Done!')
    return oo

@celery.task
def send_note(user, jobid, toemail):
    print 'Task was completed' 
    print 'I will notify %s to its email address :  %s' % (user, toemail)
    fromemail = 'devnull@ncsa.illinois.edu'
    s = smtplib.SMTP('smtp.ncsa.illinois.edu')
    link = "http://localhost:8888/status/%s" % jobid
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