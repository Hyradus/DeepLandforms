#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 15:25:46 2021

@author: gnodj
"""


import json
import os
import math
import geopandas as gpd
import pandas as pd
import rasterio as rio
from rasterio.windows import Window
import shapely.geometry as geometry
from utils.GenUtils import get_paths



def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)

    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

def window_calc(bb, src_img):
    col_off = math.floor(bb[0][0])#-50)
    row_off = math.floor(bb[0][1])#-50)
    # if col_off < 0:
    #     col_off = 0
    # if row_off < 0:
    #     row_off = 0
        
    width = math.ceil(bb[1][0]-col_off)#+50)
    height = math.ceil(bb[1][1]-row_off)#+50)
    # if width > src_img.width:
    #     width = src_img.width
    # if height > src_img.height:
    #     height = src_img.height
    Win = Window(col_off,row_off,width, height)
    return(Win)
    
def dict_saver(src_dict, new_shape, new_width,new_height,dst_name):
    src_dict['shapes']= [new_shape]
    src_dict['imageWidth']=new_width
    src_dict['imageHeight']=new_height
    src_dict['imagePath']=os.path.basename(dst_name)+'.tiff'

    json_name = dst_name+'.json'
    out_file = open(json_name, 'w')
    json.dump(src_dict,out_file,indent=2)
    out_file.close()  
    return(src_dict)

def shapesExtractor(src_file, dst_dir, init_crs):
    src_name = src_file.split('.t')[0]
    try:
        with open(src_dir+'/'+src_name+'.json') as f:
            src_dict = json.load(f)
    
        shapes = src_dict['shapes']      
        types = src_dict
        if len(shapes)>0:
            for i in range(len(shapes)):
                src_img = rio.open(src_dir+'/'+src_name+'.tiff')
                dst_name = dst_dir_name+'/'+os.path.basename(src_name)+'_lbl_'+str(i)
                shape_dict=labelExtractor(src_dict, shapes[i], src_img, dst_name)
                if i == 0:                    
                    tmp_df=gpd.GeoDataFrame(shape_dict, crs=src_img.crs)
                else:
                    tmp_df = gpd.GeoDataFrame(pd.concat([tmp_df,gpd.GeoDataFrame(shape_dict, crs=src_img.crs)]).drop_duplicates().reset_index(drop=True), crs=src_img.crs)                                
            return(tmp_df)
    except Exception as e:
        print(e)
        pass
        
def labelExtractor(src_dict, shape, src_img, dst_name):

    points = shape['points']

    bb = bounding_box(points)
    bb_min = bb[0]
    bb_max = bb[1]

    x_min = bb_min[0]
    y_min = bb_min[1]
    x_max = bb_max[0]
    y_max = bb_max[1]
    
    x_diff = (x_max-x_min)
    y_diff = (y_max-y_min)
    
    x_min_new = bb_min[0] - y_diff
    if x_min_new <0:
        x_min_new = 0
    y_min_new = bb_min[1] - x_diff
    if y_min_new <0:
        y_min_new = 0
    x_max_new = bb_max[0] + y_diff
    if x_max_new > src_img.width:
        x_max_new = src_img.width
    y_max_new = bb_max[1] + x_diff
    if y_max_new > src_img.height:
        y_max_new = src_img.height

    new_bb = [(x_min_new,y_min_new),(x_max_new,y_max_new)]
    
    
    
    wind =window_calc(new_bb, src_img)
    dst_trs = src_img.window_transform(wind)
    dst_crs = src_img.crs
    w = src_img.read(window=wind)
    
    
    
    with rio.open(dst_name+'.tiff','w',
              driver='GTiff',
              window=wind,
              width=wind.width,
              height=wind.height,
              count=src_img.count,
              dtype=src_img.dtypes[0],
              transform=dst_trs,
              crs=dst_crs) as dst:
            
        dst.write(w)
    
    new_points = [[x - wind.col_off, y - wind.row_off] for x, y in points]
    shape['points']=new_points
    dict_saver(src_dict, shape, wind.width,wind.height, dst_name)
    
    
    points_2 = [rio.transform.xy(src_img.transform,points[i][1],points[i][0]) for i in range(len(points))]
    pointList = [geometry.Point(x,y) for x,y in points_2]
    poly = geometry.Polygon([[p.x, p.y] for p in pointList])
    
    return ({"Name":os.path.basename(src_file),"Type":shape['label'],"geometry":[poly]})
    
src_dir = "/mnt/DATA/Working/BC_n_SQCRP_n_CellSize_10_m__LIM_n_None_px_cog_n/cropped"
dst_dir_name = src_dir+'/cropped'
dst_dir = os.makedirs(dst_dir_name, exist_ok=True)



src_files = get_paths(src_dir,'tiff')
init_crs = rio.open(src_dir+'/'+src_files[0]).crs
gdf = gpd.GeoDataFrame(columns=['Name'])



for src_file in src_files:
    tmp_gdf=(shapesExtractor(src_file,dst_dir, init_crs))
    try:
        if tmp_gdf.crs != init_crs:
            tmp_gdf = tmp_gdf.to_crs(init_crs)    
    except:
        pass
    gdf = gpd.GeoDataFrame(pd.concat([gdf,tmp_gdf]).drop_duplicates().reset_index(drop=True), crs=init_crs)
    
    


gdf.to_file(src_dir+'/labeled_shapes.gpkg',driver="GPKG")




