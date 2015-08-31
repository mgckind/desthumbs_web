from PIL import Image, ImageFilter
import time
import os


#im=Image.open('DES2131+0043_RGB.png')
imb=Image.open('test_heatmap.png')
w= 256#157
h = 256#157

#imb=Image.new('RGB',(w*2**6,h*2**6),'black')
#imb.paste(im,(24,24))

#crop((x1,y1,x2,y2)

def tile(zoom,xt,yt):
    path = 'tiles_map/'+str(zoom)
    if not os.path.exists(path): os.makedirs(path)
    path = 'tiles_map/'+str(zoom)+'/'+str(xt)
    if not os.path.exists(path): os.makedirs(path)
    filem = 'tiles_map/'+str(zoom)+'/'+str(xt)+'/'+str(yt)+'.png'
    nx=w*2**zoom
    ny=h*2**zoom
    imt=imb.resize((nx,ny),Image.BICUBIC)
    x1=xt*w
    y1=yt*w
    x2=x1+w
    y2=y1+w
    imf=imt.crop((x1,y1,x2,y2))
    imf.save(filem)
    
for z in xrange(6,7):
    nx=2**z
    ny=2**z
    t1=time.time()
    print z
    for xt in range(nx):
        for yt in range(ny):
            tile(z,xt,yt)
    print '%.5f seconds' % (time.time()-t1)
