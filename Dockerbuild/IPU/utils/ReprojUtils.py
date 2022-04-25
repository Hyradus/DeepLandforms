#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: 
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Sat Nov 21 17:57:09 2020
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""
import os
import geopandas as gpd
import shutil
import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from utils.GenUtils import make_folder
from pyproj import CRS

def converter(srcfile, dst_path, folder, OUT_CRS):
    xt = srcfile.split('.')
    if len(xt)<=2:
        xt=xt[1]
    else:
        xt=xt[2]
    name = os.path.basename(srcfile)
    #srcfile = folder+'/'+file
    dstfile = dst_path+'/'+xt+'/'+ name
    if xt in['shp','SHP','gpkg','GPKG']:
        vectorReproj(srcfile, dstfile, OUT_CRS)
            
    elif xt in ['tif','TIF','tiff','TIFF']:
        
        rasterReproj(srcfile, dstfile, OUT_CRS)

    else:
        skip_dir = 'Non_GIS_file'
        dstfile = dst_path+'/'+skip_dir+'/'+name
        try:
            shutil.copy(srcfile, dstfile)
        except:
            make_folder(dst_path, 'Non_GIS_file')
            shutil.copy(srcfile, dstfile)

def vectorReproj(srcfile, dstfile, dst_crs):
    basepath = os.path.dirname(dstfile)
    basename = os.path.basename(dstfile)
    wkt_file =dstfile.split('.')[0]+'.wkt'

    gdf = gpd.read_file(srcfile)
    if gdf.size == 0:
        empty_files = 'Empty_files'
        outfile =basepath+'/'+ empty_files+'/'+basename
        try:
            shutil.copy(srcfile, outfile)
        except:
            make_folder(basepath, 'Empty_files')
            shutil.copy(srcfile, outfile)
    else:
        src_crs = gdf.crs
        if src_crs == None:
            no_crs = 'Missing_CRS'
            outfile = basepath+'/'+ no_crs + '/' + basename
            try:
                shutil.copy(srcfile, outfile)
            except:
                no_crs = make_folder(basepath, 'Missing_CRS')
                shutil.copy(srcfile, outfile)
        else:
            
            gdf = gdf.to_crs(dst_crs)
            nameparts = basename.split('.')
            xt = nameparts[len(basename.split('.'))-1]
            if xt in ['gpkg','GPKG']:
                drv = "GPKG"
            else:
                drv = 'ESRI Shapefile'
    
            gdf.to_file(dstfile, driver=drv)
            crs=gdf.crs
            with open(wkt_file, 'w') as cr:
                crs=crs.to_wkt()
                cr.write(crs)
            
        
def rasterReproj(srcfile, dstfile, dst_crs):
    basepath = os.path.dirname(dstfile)
    basename = os.path.basename(dstfile)
    #dst_crs = CRS.from_user_input(user_crs)
    wkt_file =dstfile.split('.')[0]+'.wkt'
    with rio.open(srcfile) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        if src.crs == None:
            no_crs = 'Missing_CRS'
            outfile = basepath+'/'+ no_crs + '/' + basename
            try:
                shutil.copy(srcfile, outfile)
            except:
                no_crs = make_folder(basepath, 'Missing_CRS')
                shutil.copy(srcfile, outfile)
        else:                
            with rio.open(dstfile, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rio.band(src, i),
                        destination=rio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)
             
            with open(wkt_file, 'w') as cr:
                crs=rio.open(srcfile).crs.to_wkt()
                cr.write(crs)