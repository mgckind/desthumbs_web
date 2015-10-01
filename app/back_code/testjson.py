import json
import os,sys
from os import listdir
from os.path import isfile, join
import glob

mypath = 'static/uploads/'
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

pngfiles=glob.glob(mypath+'*.png')
titles=[]
for f in pngfiles:
    titles.append(f.split('/')[-1][:-4])


#AA=[]
#json.dumps([dict(mpn=pn) for pn in lst])
#for i in xrange(len(pngfiles)):
#    AA.append(
with open("static/uploads/test.json","w") as outfile:
    json.dump([dict(name='/'+pngfiles[i],title=titles[i]) for i in range(len(pngfiles))], outfile, indent=4)
