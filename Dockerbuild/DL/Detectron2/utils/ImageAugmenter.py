#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: 
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Tue Mar  9 15:13:26 2021
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""
import os
import rasterio as rio
from skimage.util import random_noise
from skimage.filters import gaussian
from skimage import exposure
from rasterio.plot import reshape_as_image, reshape_as_raster
import cv2 as cv
import numpy as np
from skimage.morphology import disk
from skimage.morphology import ball
from skimage.filters import rank
import rasterio as rio
import json

def imgNorm(image, image_dir, name):
    import cv2 as cv
    image_norm= cv.normalize(image, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
    name_norm=image_dir+name+'_normalized.png'
    cv.imwrite(name_norm,image_norm)
    return(image_norm)

def imgScaler(image, image_dir,name):
    from sklearn import preprocessing 
    min_max_scaler = preprocessing.MinMaxScaler()
    img_norm = (min_max_scaler.fit_transform(image)*255).astype(np.uint8)
    name_scal = image_dir+name+'_scaled.png'
    cv.imwrite(name_scal, img_norm)
    
def imgDen(image, image_dir, name):
    import cv2 as cv
    image_den = cv.fastNlMeansDenoising((image).astype(np.uint8), None, 10,7,21)
    name_den=name+'_denoised.png'
    cv.imwrite(name_den, image_den)

def imgEnh(image, name):
    if isinstance(image, list):
        img_norm = []
        for im in image:
            img_norm.append(cv.normalize(im, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX))
        img_merge=(img_norm[0]+img_norm[1])*2
        cv.imwrite('Merged2.png',img_merge)

def AddNoise(image, sigma):
    # img = rio.open(image).read()
    #sigma = 0.155
    return(random_noise(reshape_as_image(image)[:,:,0],var=sigma**2))

def AddBlur(image, sigma):
    # img = rio.open(image).read()
    return(gaussian(reshape_as_image(image)[:,:,0], sigma))

def GammaCorr(image, gamma_val, gain_val):
    # img = rio.open(image).read()
    return(exposure.adjust_gamma(image, gamma = gamma_val, gain = gain_val))

def LogCorr(image):
    # img = rio.open(image).read()
    return(exposure.adjust_log(image))
    
def LocEqu(image, rad):
    # img = rio.open(image).read()
    #selem = disk(30)
    neigh = ball(rad)
    return(rank.equalize(image, selem=neigh))#disk(rad)))

def AdapEqu(image, clp):
    # img = rio.open(image).read()
    #selem = disk(30)
    from skimage import exposure
    # from rasterio.plot import reshape_as_image        
    return(exposure.equalize_adapthist(reshape_as_image(image)[:,:,0], clip_limit=clp))#disk(rad)))

def noiser(image, jfile,img_ext, driver, cnt, dtp, transform, crs, sigma,DSTdir):    
    dstname = DSTdir+'/'+os.path.basename(jfile).split('.json')[0]
    try:
        noised_img = (AddNoise(image, sigma)*255).astype(dtp)
    except:
        image = reshape_as_raster(image[:,:,np.newaxis])
        # image2 = reshape_as_raster(image)
        noised_img = (AddNoise(image, sigma)*255).astype(dtp)
    savename = dstname+'_noised_sigma_'+str(sigma)+'_'
    imgname = savename+img_ext
    # print(imgname)
    ImgWriter(noised_img, imgname, driver, cnt, dtp,transform, crs)
    dst_jfile = savename+'.json'
    with open(jfile) as jf:
       jdata = json.load(jf)    
       jdata['imagePath']= os.path.basename(imgname)
       out_file = open(dst_jfile, 'w')
       json.dump(jdata,out_file,indent=2)
       out_file.close()   
    return (noised_img, imgname, dst_jfile)               

def blurrer(image, jfile,img_ext,   driver, cnt, dtp, transform, crs, sigma,DSTdir):    
    dstname = DSTdir+'/'+os.path.basename(jfile).split('.json')[0]
    try:
        blurred_img = (AddBlur(image, sigma)*255).astype(dtp)
    except:
        image = reshape_as_raster(image[:,:,np.newaxis])
        blurred_img = (AddBlur(image, sigma)*255).astype(dtp)
    savename = dstname+'_blurred_sigma_'+str(sigma)
    imgname = savename+img_ext
    # print(imgname)
    ImgWriter(blurred_img, imgname, driver, cnt, dtp,transform, crs)
    dst_jfile = savename+'.json'
    with open(jfile) as jf:
       jdata = json.load(jf)       
       jdata['imagePath']= os.path.basename(imgname)
       out_file = open(dst_jfile, 'w')
       json.dump(jdata,out_file,indent=2)
       out_file.close()
       return (blurred_img, imgname, dst_jfile)
 
    
def Gamma(image, jfile,img_ext,   dstname, driver, cnt, dtp, transform, crs, ):    
    gamma_img = (GammaCorr(image, 0.5,0.5))#*255).astype(dtp)
    savename = dstname+'_gamma'
    imgname = savename+img_ext
    ImgWriter(gamma_img, imgname, driver, cnt, dtp,transform, crs)
    dst_jfile = savename+'.json'
    with open(jfile) as jf:
       
       jdata = json.load(jf)
       
       jdata['imagePath']= os.path.basename(imgname)
   
       out_file = open(dst_jfile, 'w')
       json.dump(jdata,out_file,indent=2)
       out_file.close()   
    
def LogCorrect(image, jfile, img_ext,  driver, cnt, dtp, transform, crs,DSTdir):    
    dstname = DSTdir+'/'+os.path.basename(jfile).split('.json')[0]
    try:
        log_corr_img = (LogCorr(image))#*255).astype(dtp)
    except:
        image = reshape_as_raster(image[:,:,np.newaxis])   
        log_corr_img = (LogCorr(image))#*255).astype(dtp)
    savename = dstname+'_logcorrected'
    imgname = savename+img_ext
    # print(imgname)
    ImgWriter(log_corr_img, imgname, driver, cnt, dtp,transform, crs)
    dst_jfile = savename+'.json'
    with open(jfile) as jf:
       jdata = json.load(jf)
       jdata['imagePath']= os.path.basename(imgname)
       out_file = open(dst_jfile, 'w')
       json.dump(jdata,out_file,indent=2)
       out_file.close()       
       return(log_corr_img)
   
def LEqualizer(image, jfile,img_ext,   dstname, driver, cnt, dtp, transform, crs, rad,DSTdir):    
    try:
        locequal_img = (LocEqu(image, rad))#*255).astype(dtp)
    except:
        image = reshape_as_raster(image[:,:,np.newaxis])
        locequal_img = (LocEqu(image, rad))#*255).astype(dtp)
    savename = dstname+'_LocEqu_rad_'+str(rad)
    imgname = savename+img_ext
    # print(imgname)
    ImgWriter(locequal_img, imgname, driver, cnt, dtp,transform, crs)
    dst_jfile = savename+'.json'
    with open(jfile) as jf:
       jdata = json.load(jf)
       jdata['imagePath']= os.path.basename(imgname)
       out_file = open(dst_jfile, 'w')
       json.dump(jdata,out_file,indent=2)
       out_file.close()   
       return(locequal_img)

def AdaptEqualizer(image, jfile,img_ext, driver, cnt, dtp, transform, crs, clp,DSTdir):    
    # from skimage import exposure
    # from rasterio.plot import reshape_as_image
    # img = rio.open(img_file).read()
    # im = reshape_as_image(img)[:,:,0]
    # imex=exposure.equalize_adapthist(im, clip_limit=clp)
    dstname = DSTdir+'/'+os.path.basename(jfile).split('.json')[0]
    try:
        adapequal_img = (AdapEqu(image, clp)*255).astype(dtp)
    except:
        image = reshape_as_raster(image[:,:,np.newaxis])   
        adapequal_img = (AdapEqu(image, clp)*255).astype(dtp)         
    savename = dstname+'_AdaptEqu_clp_'+str(clp)
    imgname = savename+img_ext
    # print(imgname)
    ImgWriter(adapequal_img, imgname, driver, cnt, dtp,transform, crs)
    dst_jfile = savename+'.json'
    with open(jfile) as jf:
       jdata = json.load(jf)
       jdata['imagePath']= os.path.basename(imgname)
       out_file = open(dst_jfile, 'w')
       json.dump(jdata,out_file,indent=2)
       out_file.close() 
       return(adapequal_img, imgname, dst_jfile)

def ImageAugmenter(jfile, img_ext, DSTdir, path):
    basename = jfile.split('.json')[0]
    dstname = DSTdir+'/'+os.path.basename(jfile).split('.json')[0]
    
    img_file = path +'/'+basename+img_ext
    img = rio.open(img_file)
    driver = 'GTiff'
    crs = img.crs
    dtp = img.dtypes[0]
    transform = img.transform
    cnt = img.count
    image = img.read()
    
        
    jfile = path +'/'+jfile
    logcor = LogCorrect(image, jfile,  img_ext, driver, cnt, dtp, transform, crs,DSTdir)
    noise, noisename, noisejs = noiser(image, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.1,DSTdir)
    blur, blurname,blurjs = blurrer(image, jfile, img_ext,  driver, cnt, dtp, transform, crs, 1.5,DSTdir)
    #adapequal,adapname,adapjs =AdaptEqualizer(image, jfile,img_ext, driver, cnt, dtp, transform, crs, 0.01,DSTdir)
    
    #noiser(blur, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.15,DSTdir)
    #blurrer(noise, jfile, img_ext,  driver, cnt, dtp, transform, crs, 2.5,DSTdir)        
    
    #noiser(adapequal, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.1,DSTdir)
    #blurrer(adapequal, jfile, img_ext,  driver, cnt, dtp, transform, crs, 2,DSTdir)        
    
   
    rnd = np.random.randint(0, 5, 1)[0]
    if rnd == 0:        
        noiser(image, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.05,DSTdir)
        blurrer(image, jfile, img_ext,  driver, cnt, dtp, transform, crs, 1,DSTdir)           
    elif rnd ==1:
        noiser(image, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.15,DSTdir)
        blurrer(image, jfile, img_ext,  driver, cnt, dtp, transform, crs, 2,DSTdir)   
    elif rnd==2:
        noiser(image, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.2,DSTdir)
        blurrer(image, jfile, img_ext,  driver, cnt, dtp, transform, crs, 2.5,DSTdir)   
    elif rnd==3:
        noiser(image, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.25,DSTdir)
        blurrer(image, jfile, img_ext,  driver, cnt, dtp, transform, crs, 3,DSTdir)                
    elif rnd==4:
        noiser(image, jfile,  img_ext, driver, cnt, dtp, transform, crs, 0.3,DSTdir)
        blurrer(image, jfile, img_ext,  driver, cnt, dtp, transform, crs, 3.5,DSTdir)        
    
    img.close()

    
def ImgWriter(img, savename, drv, cnt,dtp,transform, crs):
    try:
        cnt,height, width= img.shape
        simg = img
    except:
        nimg = img[:,:,np.newaxis]
        #width, height, cnt = nimg.shape
        from rasterio.plot import reshape_as_raster
        simg = reshape_as_raster(nimg)
        ctn, height, width = simg.shape
    with rio.open(savename,'w',
              driver=drv,
              width=width,
              height=height,
              count=cnt,
              dtype=dtp,
              transform=transform,
              crs=crs) as dst:
        dst.write(simg)