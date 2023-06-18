#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: ImgUtils module containing various function for manipulate images
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Mon Oct 12 16:47:44 2020
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""
import os
from copy import copy
import numpy as np
import cv2 as cv
# from PIL import Image
# Image.MAX_IMAGE_PIXELS = None
import rasterio as rio
from rasterio.plot import reshape_as_raster, reshape_as_image
from rasterio.windows import Window
from rasterio.enums import Resampling
from utils.TileFuncs import Dim2Tile, TileNumCheck
import gc
from rasterio.windows import Window
import math
from osgeo import gdal
from osgeo.gdal import gdalconst
import pandas as pd
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from skimage.exposure import match_histograms
from skimage import exposure
from sklearn import preprocessing
from skimage.filters import rank
from skimage.morphology import ball
from skimage import exposure

def geoslicer(image, max_dim, savename, bc, sqcrp, res, cell_size, oxt, cog, cog_cfg, bit, data_dict, dem, ixt, overlap):
        # from datetime import datetime as dt
    # start = dt.now()
    src = rio.open(image)
    try:
        cnt, src_height, src_width = src.shape
    except:
        src_height, src_width = src.shape
        cnt = 1

    crs = src.crs
    src_trs = src.transform
    vt=Dim2Tile(max_dim, src_width)
    ht = Dim2Tile(max_dim, src_height)
    vt, ht = TileNumCheck(vt,ht, src_width, src_height, max_dim)

    names =[]
    windows =[]
    transforms=[]


    for ih in range(ht):

        for iw in range(vt):
            sname = savename.split('.'+oxt)[0]+'_H'+str(ih)+'_V'+str(iw)
            names.append(sname)

            x = math.floor(src_width/vt*iw)
            y = math.floor(src_height/ht*ih)
            h = math.floor(src_height/ht)
            w = math.floor(src_width/vt)
            if overlap != None:
                x=round(x-x*overlap/100)
                y=round(y-y*overlap/100)

                h=round(h+h*overlap/100)

                w=round(w+w*overlap/100)            
                if ih+1 == ht:

                    if (y+h)< src_height:
                        h=src_height-y
                if iw+1 == vt:
                    if (x+w)< src_width:
                        #print((x+w)<src_width)
                        w=src_width-x
                        #print(w)
            tile_win = Window(x,y,w,h)
            windows.append(tile_win)
            dst_trs = src.window_transform(tile_win)
            # t= rio.windows.transform(win, src_trs)
            # t = src.window_transform(win)
            transforms.append(dst_trs)

    tiles_dict = {'Names':names,
                  'Windows':windows,
                  'Transforms':transforms}

    for i in range(len(tiles_dict['Names'])):
            # start=dt.now()
            savename = tiles_dict['Names'][i]
            tile_src_win = tiles_dict['Windows'][i]
            tile_trs = tiles_dict['Transforms'][i]
            xoff = tile_win.col_off
            yoff = tile_win.row_off
            tile_height = tile_src_win.height
            tile_width = tile_src_win.width

            if bc in ['y','Y']:
                try:
                    tile_width, tile_height, temp_win, tile_trs, savename =  borderCropper(src,
                                                                                        tile_src_win,
                                                                                        savename)
                    tile_col_off = tile_src_win.col_off + temp_win.col_off
                    tile_row_off = tile_src_win.row_off + temp_win.row_off
                    tile_width = temp_win.width
                    tile_height = temp_win.height
                    tile_src_win = Window(col_off=tile_col_off, row_off=tile_row_off,
                                      width=tile_width,
                                      height = tile_height)
                    tile_trs = src.window_transform(tile_src_win)
                except Exception as e:

                    data_dict['Status']=e
                    break

            if sqcrp in ['Y','y']:

                try:
                    tile_width, tile_height, tile_src_win, tile_trs, savename = square_crop(src,
                                                                          tile_width,
                                                                          tile_height,
                                                                          tile_src_win,
                                                                          savename)
                except Exception as e:
                    data_dict['Status']=e
                    pass

            if res in ['Y', 'y']:
                try:
                    tile_height, tile_width, tile_trs, savename = CellSizeScale(src,
                                                                             tile_height,
                                                                             tile_width,
                                                                             float(cell_size),
                                                                             tile_trs,
                                                                             savename)
                except Exception as e:
                    data_dict['Status']=e
                    pass

            try:
                
                img = src.read(window=tile_src_win,
                               out_shape=(cnt, tile_height, tile_width),
                               resampling=Resampling.cubic,
                              masked=True)
                noData=src.nodata
                dt = img.dtype
                if noData == None:
                    noData = 0
                #img = exposure.equalize_adapthist(img, clip_limit=0.01)                   
                if bit in ['yes','ye','y']:
                    noData=0                
                    img = cv.convertScaleAbs(img,alpha=(255.0/img.max()))
                    dt = img.dtype
               
                #min_max_scaler = preprocessing.MinMaxScaler()#feature_range=(0,255))
                #img = min_max_scaler.fit_transform(img[:,:,0])
                #img = reshape_as_raster(img[:,:,np.newaxis])
                #img = exposure.equalize_adapthist(img, clip_limit=1)    
                
                #if i==0:
                #    img0=img.copy()
                #else:
                #    img=matched = match_histograms(img, img0, channel_axis=-1)

                #mg = exposure.equalize_adapthist(reshape_as_image(image)[:,:,0], clip_limit=0.01)
                #img = exposure.adjust_log(img)

                
                if dem.lower() in ['yes','ye','y']:

                    print('DEM cannot be 8bit')
                    bit = 'n'

                savename = savename+'.'+oxt
                with rio.open(savename,'w',
                          driver='GTiff',
                          window=tile_src_win,
                          width=tile_width,
                          height=tile_height,
                          count=cnt,
                          nodata=noData,
                          dtype=dt,
                          transform=tile_trs,
                          crs=crs) as dst:
                    dst.write(img)
                
                del img

                if cog in ['Yes','yes','Y','y']:                           
                    dest = savename.split('.'+oxt)[0]+'-cog.'+oxt  
                    try:                        
                        _translate(savename, dest,profile='DEFLATE', profile_options=cog_cfg)                        
                    except Exception as e:                                              
                        try:
                            _translate(image, dest,profile='DEFLATE', profile_options=cog_cfg)
                        except:
                            data_dict['Errors']=e
                            print(e)

                data_dict['Status']='Done'
                tmp_df = pd.DataFrame.from_dict([data_dict])

                _ = gc.collect()
                data_dict['Status']='Done'
            except Exception as e:
                print(e)
                del img
                _ = gc.collect()

    data_dict['Status']='Done'
    tmp_df = pd.DataFrame.from_dict([data_dict])
    return tmp_df

def gdalWriter(driverName, src, shape, dst_name,transform, srs):
    driver=gdal.GetDriverByName(driverName)
    rows, cols, bands = shape

def _translate(src_path, dst_path, profile="DEFLATE", profile_options={}, **options):
    #source: https://github.com/cogeotiff/rio-cogeo
    """Convert image to COG."""
    # Format creation option (see gdalwarp `-co` option)
    output_profile = cog_profiles.get(profile)
    output_profile.update(dict(BIGTIFF="IF_SAFER"))
    output_profile.update(profile_options)

    # Dataset Open option (see gdalwarp `-oo` option)
#    config = dict(
#        GDAL_NUM_THREADS="ALL_CPUS",
#        #GDAL_TIFF_INTERNAL_MASK=True,
#        #GDAL_TIFF_OVR_BLOCKSIZE="128",
#    )

    cog_translate(
        src_path,
        dst_path,
        output_profile,
        #config=config,
        in_memory=False,
        quiet=True,
        **options,
    )
    return True

def cogCreator(savename, cog_cfg, nodata, otype):#, stats):

    base_opts = f'-a_nodata {nodata} -mask none -ot {otype}'
    tmp_opts=base_opts
    final_opts=base_opts
    #if otype in ['Byte']:
        #cog_cfg['COMPRESS']='JPEG'
    for k, v in cog_cfg.items():
        if k in ['levels','RESAMPLING']:
            pass
        elif k in ['TILED','COMPRESS','BIGTIFF']:
            final_opts = final_opts + f' -co {k}'+f'={v}'
            tmp_opts = tmp_opts+  f' -co {k}'+f'={v}'
        else:
            final_opts = final_opts + f' -co {k}'+f'={v}'
    final_opts = final_opts + f' -co COPY_SRC_OVERVIEWS=YES'


    dst_tmp_cog = savename.split('.tiff')[0]+'-tmp-cog.tiff'
    tmp_cog=gdal.Translate(dst_tmp_cog, savename, options=tmp_opts)#,scaleParams=[])
    tmp_cog.BuildOverviews(cog_cfg['RESAMPLING'], cog_cfg['levels'])
    tmp_cog = None
    final_cog = savename.split('.tiff')[0]+'-cog.tiff'
    final_cog=gdal.Translate(final_cog, dst_tmp_cog, options=final_opts)#,scaleParams=[])
    final_cog = None
    os.remove(dst_tmp_cog)



def borderCropper(src, source_win,savename, oxt):
    pre_crop, crd = CvContourCrop(np.array(reshape_as_image(src.read(window=source_win)).astype(np.uint8)))
    bx =  maxRectContourCrop(pre_crop)
    del pre_crop
    ysize = bx[3]-bx[1]
    xsize = bx[2]-bx[0]
    xoff = crd[0]+bx[0]#+src_win.width
    yoff = crd[1]+bx[1]#+src_win.height
    bc_win = Window(xoff, yoff, xsize, ysize)
    src_win = copy(bc_win)
    dst_trs = src.window_transform(src_win)
    src_width = bc_win.width
    src_height = bc_win.height
    savename = savename.split('.'+oxt)[0]+'_cropped'
    return(src_width, src_height, src_win, dst_trs, savename)




def CvContourCrop(source):
    _, threshold = cv.threshold(source, 1, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    max_area = 0
    max_areas = []
    if len(contours) > 0:
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area > max_area:
                max_area = area
                max_areas.append([area,cnt])
                best_cnt = cnt
        x, y, w, h = cv.boundingRect(best_cnt)
    # else:
    #     x = 0
    #     y = 0
    #     w = source.shape[0]
    #     h = source.shape[1]
    crd = [x,y,w,h]
    try:
        img_crop = source[y:y+h, x:x+w,:]
    except:
        img_crop = source[y:y+h, x:x+w]
    return(img_crop, crd)



def maxRectContourCrop(img_crop):
    _, bins = cv.threshold(img_crop, 1, 255, cv.THRESH_BINARY)
    kernel = np.ones((100,100), np.uint8)

    bins = cv.dilate(bins, kernel, iterations=1)
    bins = cv.erode(bins, kernel, iterations=1)
    contours, hierarchy = cv.findContours(bins, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    from maxrect import get_intersection, get_maximal_rectangle
    coords = coordFinder(contours, img_crop)
    #coords = [[int(cc[0]),int(cc[1])]for cc in coords]
    _, coordinates = get_intersection([coords])
    coo = list(coordinates)
    ll, ur = get_maximal_rectangle(coo)
    bx = (ll[0],ll[1],ur[0],ur[1])
    bx = [round(num) for num in bx]
    # image = Image.fromarray(processed_image)
    # img_crop = image.crop(bx)
    return(bx)#img_crop, bx)

def coordFinder(contours, gray):
    for cnt in contours :
        approx = cv.approxPolyDP(cnt, 0.009 * cv.arcLength(cnt, True), True)
        n = approx.ravel()
        i = 0
        coords =[]
        for j in n :
            if(i % 2 == 0):
                x = n[i]
                y = n[i + 1]
                # String containing the coordinates.
                coords.append([int(x),int(y)])
            i = i + 1
    return(coords)

def square_crop(src, src_width, src_height, src_win, savename, oxt):
    center_x = src_width//2
    center_y = src_height//2
    diff = abs(src_width-src_height)
    if src_width <= src_height:
        x= src_width
        y=src_height-diff

    elif src_width > src_height:
        x=src_width-diff
        y=src_height

    top_edge = center_y - y//2+src_win.row_off
    left_edge = center_x - x//2 +src_win.col_off
    right_edge = center_x +x//2 +src_win.col_off
    size = right_edge -left_edge
    size = int(size)
    crp_win = Window(left_edge,top_edge,size,size)
    src_win = copy(crp_win)
    dst_trs = src.window_transform(crp_win)
    src_width = src_win.width
    src_height = src_win.height
    savename = savename.split('.'+oxt)[0]+'_centered'
    return(src_width, src_height, src_win, dst_trs, savename)

def CellSizeScale(src, src_height, src_width, cell_size, dst_trs, savename):
    cell_sizeX = abs(src.transform[0])
    cell_sizeY = abs(src.transform[4])
    dst_cell_sizeX = cell_size
    dst_cell_sizeY = cell_size
    scaleX = cell_sizeX/dst_cell_sizeX
    scaleY = cell_sizeY/dst_cell_sizeY
    dst_height=int(src_height*scaleY)
    dst_width=int(src_width*scaleX)
    dst_trs = dst_trs * dst_trs.scale(
            (src_width/dst_width),
            (src_height/dst_height))
    src_width = copy(dst_width)
    src_height = copy(dst_height)
    savename = savename+'_resized_'+str(cell_size)+'m'
    return(src_height, src_width, dst_trs, savename)

def GTiffImageResizer(image, dim):
    with rio.open(image) as src:
        width, height = src.shape
        new_height=dim
        new_width = int(width*new_height/height)
        cnt = src.count
        t = src.transform

        img = src.read(
                out_shape=(cnt, new_height, new_width),
                resampling=Resampling.nearest,
            )

        transform = t * src.transform.scale(
                new_width,
                new_height)
        src.close()
    return(img, transform, cnt)




def ImgWriter(img, savename, driver, cnt,dtp,transform, crs):
    width, height = img.shape
    with rio.open(savename,'w',
              driver='GTiff',
              width=width,
              height=height,
              count=cnt,
              dtype=dtp,
              transform=transform,
              crs=crs) as dst:
        dst.write(img)



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
 #img = cv.normalize(img, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
                #maxval = img.max()

                #if maxval != 0:
                #    if maxval == 255:
                #        alpha = 255
                #    else:
                #        alpha = (255.0/maxval)
