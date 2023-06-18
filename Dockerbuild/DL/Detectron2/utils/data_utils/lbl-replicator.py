#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 11:30:51 2021

@author: hyradus
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 15:25:46 2021

@author: gnodj
"""


import os
import rasterio as rio

from shapely.geometry import box
import geopandas as gpd
import pandas as pd
import math
from rasterio.windows import Window
import json
import shapely.geometry as geometry
from osgeo import gdal


def get_paths(PATH, ixt):
    import re
    import fnmatch
    #os.chdir(PATH)
    ext='*.'+ixt
    chkCase = re.compile(fnmatch.translate(ext), re.IGNORECASE)
    files = [f for f in os.listdir(PATH) if chkCase.match(f)]
    return(files)

def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)

    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]


def limitcalc(bb_min, bb_max, y_diff, x_diff, src_img):
    x_min_new = bb_min[0] - int(y_diff//2)
    if x_min_new <0:
        x_min_new = 0
    y_min_new = bb_min[1] - int(x_diff//2)
    if y_min_new <0:
        y_min_new = 0
    x_max_new = bb_max[0] + int(y_diff//2)
    if x_max_new > src_img.width:
        x_max_new = src_img.width
    y_max_new = bb_max[1] + int(x_diff//2)
    if y_max_new > src_img.height:
        y_max_new = src_img.height
    return(x_min_new, y_min_new, x_max_new, y_max_new)

# def window_calc(bb, src_img, sq):
#     col_off = math.floor(bb[0][0])#-50)
#     row_off = math.floor(bb[0][1])#-50)
#     # if col_off < 0:
#     #     col_off = 0
#     # if row_off < 0:
#     #     row_off = 0
        
#     width = math.ceil(bb[1][0]-col_off)#+50)
#     height = math.ceil(bb[1][1]-row_off)#+50)
#     # if width > src_img.width:
#     #     width = src_img.width
#     # if height > src_img.height:
#     #     height = src_img.height
#     # if sq.lower() in ['y','yes']:
#     center_x = width//2
#     center_y = height//2
#     diff = abs(width-height)
#     if width <= height:
#         x= width
#         y=height-diff
    
#     elif width > height:
#         x=width-diff
#         y=height
#     top_edge = center_y - y//2+row_off
#     left_edge = center_x - x//2 +col_off
#     right_edge = center_x +x//2 +col_off
#     size = right_edge -left_edge
#     size = int(size)
#     Win = Window(left_edge,top_edge,size,size)
#     # Win = Window(col_off,row_off,width, height)
#     return(Win)

def window_calc(bb, src_img):
    col_off = math.floor(bb[0][0])#-50)
    row_off = math.floor(bb[0][1])#-50)

    width = math.ceil(bb[1][0]-col_off)#+50)
    height = math.ceil(bb[1][1]-row_off)#+50)

    Win = Window(col_off,row_off,width, height)
    return(Win)

def bb_cal(src_img, bb_min, bb_max,mm):
    x_min = bb_min[0]
    y_min = bb_min[1]
    x_max = bb_max[0]
    y_max = bb_max[1]
    
    x_diff = (x_max-x_min)
    y_diff = (y_max-y_min)
    
    x_min_new = bb_min[0] - int(y_diff*mm)
    if x_min_new <0:
        x_min_new = 0
    y_min_new = bb_min[1] - int(x_diff*mm)
    if y_min_new <0:
        y_min_new = 0
    x_max_new = bb_max[0] + int(y_diff*mm)
    if x_max_new > src_img.width:
        x_max_new = src_img.width
    y_max_new = bb_max[1] + int(x_diff*mm)
    if y_max_new > src_img.height:
        y_max_new = src_img.height
    
    
    new_bb = [(x_min_new,y_min_new),(x_max_new,y_max_new)]
    return(new_bb)


# PATH = "/mnt/DATA/Working/BC_n_SQCRP_n_CellSize_10_m__LIM_n_None_px_cog_n/"
# BASE_PATH = '/mnt/NAS/OrbitalData/Mars/HiRISE/OriginalforPITS/BC_n_SQCRP_n_CellSize_5_m__LIM_n_None_px_cog_n/'
# PATH = BASE_PATH+'src_5m/'
#PATH = '/mnt/NAS/OrbitalData/Mars/HiRISE/OriginalforPITS/BC_n_SQCRP_n_CellSize_0-5_m__LIM_n_None_px_cog_n/'
PATH = '/mnt/NAS/OrbitalData/Mars/HiRISE/OriginalforPITS/BC_n_SQCRP_n_CellSize_2_m__LIM_n_None_px_cog_n/'
# PATH = '/mnt/NAS/OrbitalData/Mars/HiRISE/OriginalforPITS/BC_n_SQCRP_n_CellSize_2_m__LIM_n_None_px_cog_n'
dst_dir_name = PATH+'/extracted/'
dst_dir = os.makedirs(dst_dir_name, exist_ok=True)
dsize= 2.0

start_path='/mnt/W-DATS/2022/WorkingDataset/MarsPIT/BC_n_SQCRP_n_CellSize_10_m__LIM_n_None_px_cog_n_V2/'
ssize= 10.0


src_gpkg = '/mnt/W-DATS/2022/WorkingDataset/MarsPIT/BC_n_SQCRP_n_CellSize_10_m__LIM_n_None_px_cog_n_V2/labeled_shapes.gpkg'
src_gdf = gpd.read_file(src_gpkg)


paths = get_paths(start_path, 'json')
import rasterio as rio
import rioxarray as riox
from shapely.geometry import mapping
import time
from pyproj import CRS, Transformer
# dst_crs = CRS.from_wkt('GEOGCS["Mars 2000",DATUM["D_Mars_2000",SPHEROID["Mars_2000_IAU_IAG",3396190.0,169.89444722361179]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]')
for i in range(len(paths)):
    # base_name, suffix = paths[i].split(f'{ssize}')
    base_name, suffix =src_gdf.iloc[i]["Name"].split(f'{ssize}')
    try:
        
        # print(base_name, suffix)
        #src_name = base_name.split('10')[0]
        # img_src_file = f'{PATH}/{base_name}{dsize}m.tiff'
        img_src_file = f'{PATH}/{base_name}{dsize}m.tiff'
        
        src_img = rio.open(img_src_file)
        layer = gdal.Open(img_src_file)
        gt =layer.GetGeoTransform()
        
        
        c, a, b, f, d, e = gt
        
        
        
        # src_img2 = riox.open_rasterio(img_src_file)
        # gt2 = src_img2.rio.transform()
        # a1, b1, c1, d1, e1, f1, _,_,_ = gt2
        # # from your function
        # # col = 100
        # # row = 75
        # # x_geo = a * col + b * row + a * 0.5 + b * 0.5 + c
        # # y_geo = d * col + e * row + d * 0.5 + e * 0.5 + f
        # # print(x_geo,y_geo)
        src_gdf_r = src_gdf.to_crs(src_img.crs)
        shape = src_gdf_r.iloc[i].geometry
        
        
        
        
        geo_points = list(shape.exterior.coords)
        points = [(int((x - c) / a),int((y - f) / e)) for x,y in geo_points]
        transformer = Transformer.from_crs(src_gdf.crs, src_img.crs, always_xy=True)
        
    
        
        # points = shape['points']

        bb = bounding_box(points)
        bb_min = bb[0]
        bb_max = bb[1]
        
        x_min = bb_min[0]
        y_min = bb_min[1]
        x_max = bb_max[0]
        y_max = bb_max[1]
        
        label_width = math.ceil(x_max-x_min)
        label_height = math.ceil(y_max-y_min)
        
        
            
        dst_width, dst_height = 64, 64
        width_diff = (dst_width - label_width)//2
        height_diff = (dst_height - label_height)//2
        

        x_min_new = bb_min[0] - width_diff    
        y_min_new = bb_min[1] - height_diff
        x_max_new = bb_max[0] + width_diff    
        y_max_new = bb_max[1] + height_diff

        if label_width > math.ceil(x_max_new-x_min_new):
            x_min_new = x_min-dst_width//2
            x_max_new = x_max+dst_width//2
        if label_height > math.ceil(y_max_new-y_min_new):
            y_min_new = y_min-dst_height//2
            y_max_new = y_max+dst_height//2
            
        x_center = label_width//2
        y_center = label_height//2
        new_width = math.ceil(x_max_new-x_min_new)
        new_height = math.ceil(y_max_new-y_min_new)
        
        if new_width > new_height:
            height_diff = (new_width - new_height)//2        
            y_min_new = y_min_new - height_diff
            y_max_new = y_max_new + height_diff
            
        elif new_width < new_height:
            width_diff = (new_height - new_width)//2
            x_min_new = x_min_new - width_diff    
            x_max_new = x_max_new + width_diff  
            
            
        if x_max_new > src_img.width:
            x_max_new = src_img.width
        if y_max_new > src_img.height:
            y_max_new = src_img.height
        if y_min_new <0:
            y_min_new = 0
        if x_min_new <0:
            x_min_new = 0
        
        
        
        max_cords = (x_max_new, y_max_new)
        min_cords = (x_min_new, y_min_new)
        
        
        new_bb = [min_cords,max_cords]
        
        wind =window_calc(new_bb, src_img)
        #wind =window_calc(new_bb, src_img)
        dst_trs = src_img.window_transform(wind)
        dst_crs = src_img.crs
        w = src_img.read(window=wind)
        # print(i)
        suf = suffix.split('.json')[0]
        dst_name = f'{dst_dir_name}{base_name}{dsize}{suf}.tiff'
        # dst_name = dst_dir_name+base_name+'2.0'+suffix.split('.json')[0]+'.tiff'
        with rio.open(dst_name,'w',
                  driver='GTiff',
                  window=wind,
                  width=wind.width,
                  height=wind.height,
                  count=src_img.count,
                  dtype=src_img.dtypes[0],
                  transform=dst_trs,
                  crs=dst_crs) as dst:
                
            dst.write(w)
        
        SRC_LBL_PATH = start_path
        json_src_file = f'{base_name}{ssize}{suffix}'
        
        with open(SRC_LBL_PATH+json_src_file) as f:
            src_dict = json.load(f)
            # original = '/mnt/DATA/Working/Working_Pit_2022/src_10m/ESP_011386_2065_RED_resized_10.0m.tiff'
            original = start_path+paths[i]
            ori_img = rio.open(original.split('.json')[0]+'.tiff')
        
            layer = gdal.Open(dst_name)
            gt =layer.GetGeoTransform()
            # gt = src_img.transform
            c, a, b, f, d, e = gt
            points = [(int((x - c) / a),int((y - f) / e)) for x,y in geo_points]
            src_dict['shapes'][0]['points']=[list(pt) for pt in points]
            src_dict['imageWidth']=wind.width
            src_dict['imageHeight']=wind.height
            src_dict['imagePath']=os.path.basename(dst_name)
        
            json_name = dst_name.split('.tiff')[0]+'.json'
            out_file = open(json_name, 'w')
            json.dump(src_dict,out_file,indent=2)
            out_file.close()
    except Exception as e:
        print(base_name+suffix, i)
        print(e)
