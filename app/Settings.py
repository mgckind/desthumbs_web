import os
DEBUG = True
DIRNAME = os.path.dirname(__file__)
STATIC_PATH = os.path.join(DIRNAME, 'static')
TEMPLATE_PATH = os.path.join(DIRNAME, 'templates')
UPLOADS = os.path.join(STATIC_PATH,"uploads/")

import logging
import sys
#log linked to the standard error stream
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)-8s - %(message)s',
                    datefmt='%d/%m/%Y %Hh%Mm%Ss')
console = logging.StreamHandler(sys.stderr)

#import base64
#import uuid
#base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
FF=open('ranC.tck','r')
COOKIE_SECRET = FF.readlines()[0]
FF.close()

class dbConfig(object):
    def __init__(self):
        self.host = 'leovip148.ncsa.uiuc.edu'
        self.port = '1521'

class mysession(object):
    randomname = 'abcde'
