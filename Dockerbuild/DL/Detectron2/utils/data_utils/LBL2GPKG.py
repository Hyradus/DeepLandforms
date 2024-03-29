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

from pyproj import CRS

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

def window_calc(bb, src_img):
    col_off = math.floor(bb[0][0])#-50)
    row_off = math.floor(bb[0][1])#-50)

    width = math.ceil(bb[1][0]-col_off)#+50)
    height = math.ceil(bb[1][1]-row_off)#+50)

    Win = Window(col_off,row_off,width, height)
    return(Win)

def dict_saver(src_dict, new_shape, new_width,new_height,dst_name):
    src_dict['shapes']= [new_shape]
    src_dict['imageWidth']=new_width
    src_dict['imageHeight']=new_height
    src_dict['imagePath']=os.path.basename(dst_name.split('.json')[0])+'.tiff'

    json_name = dst_name
    out_file = open(json_name, 'w')
    json.dump(src_dict,out_file,indent=2)
    out_file.close()
    return(src_dict)

def shapesExtractor(src_name, src_size, dst_dir, dst_crs, src_file):
    # src_name = img_src_file.split('.j')[0]
    base_name = f'{src_dir}/{src_name}{src_size}m'
    src_tiff, _ = src_file.split('.json')
    src_json = f'{src_dir}/{src_file}'
    try:
        with open(src_json)as f:
            src_dict = json.load(f)

        shapes = src_dict['shapes']
        # types = src_dict
        if len(shapes)>0:
            for i in range(len(shapes)):
                # src_img = rio.open(f'{base_name}.tiff')
                src_img = rio.open(f'{src_dir}/{src_tiff}.tiff')
                # dst_name = dst_dir_name+'/'+os.path.basename(src_name)+src_size+'_lbl_'+str(i)
                dst_name = f'{dst_dir_name}/{src_file}'
                shape_dict=labelExtractor(src_dict, shapes[i], src_img, dst_name)
                if i == 0:
                    tmp_df=gpd.GeoDataFrame(shape_dict, crs=src_img.crs)
                    # if src_img.crs != dst_crs:
                    #     tmp_df = tmp_df.to_crs(dst_crs)
                else:
                    tmp_df = gpd.GeoDataFrame(pd.concat([tmp_df,gpd.GeoDataFrame(shape_dict, crs=src_img.crs)]).drop_duplicates().reset_index(drop=True), crs=src_img.crs)
            return(tmp_df)
    except Exception as e:
        print(e)
        pass

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

def labelExtractor(src_dict, shape, src_img, dst_name):

    points = shape['points']

    bb = bounding_box(points)
    bb_min = bb[0]
    bb_max = bb[1]

    x_min = bb_min[0]
    y_min = bb_min[1]
    x_max = bb_max[0]
    y_max = bb_max[1]
    ratio = 0.25
    x_diff = (x_max-x_min)*ratio
    y_diff = (y_max-y_min)*ratio
    
    
    x_min_new, y_min_new, x_max_new, y_max_new = limitcalc(bb_min,
                                                           bb_max,
                                                           y_diff,
                                                           x_diff,
                                                           src_img
                                                           )
    new_bb = [(x_min_new,y_min_new),(x_max_new,y_max_new)]
    # print(x_max-x_min)
    print('old',bb)
    print('new', new_bb)
    
    if (new_bb[1][0]) < 640:
        print(new_bb[1][0],'aaaa')
        # print(dst_name)
        
        x_diff1 = (x_diff*128)//x_diff #(src_img.width-x_diff)*ratio
        y_diff1 = (y_diff*128)//y_diff #(src_img.height-y_diff)*ratio
        
        x_min_new, y_min_new, x_max_new, y_max_new = limitcalc(bb_min,
                                                               bb_max,
                                                               y_diff1,
                                                               x_diff1,
                                                               src_img
                                                               )
        new_bb = [(x_min_new,y_min_new),(x_max_new,y_max_new)]
        print(new_bb, 'new')

    wind =window_calc(new_bb, src_img)
    dst_trs = src_img.window_transform(wind)
    dst_crs = src_img.crs
    w = src_img.read(window=wind)



    with rio.open(dst_name.split('.json')[0]+'.tiff','w',
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

    return ({"Name":os.path.basename(dst_name),"Type":shape['label'],"geometry":[poly]})


src_dir = '/mnt/W-DATS/2022/WorkingDataset/MarsPIT/BC_n_SQCRP_n_CellSize_10_m__LIM_n_None_px_cog_n_V2/'
dst_dir_name = src_dir+'/cropped'
dst_dir = os.makedirs(dst_dir_name, exist_ok=True)


src_files = get_paths(src_dir,'json')
init_src_file=src_files[0].split('.json')[0]+'.tiff'
#init_crs = rio.open(src_dir+'/'+init_src_file).crs

ssize = 10.0
dst_crs = CRS.from_wkt('GEOGCS["Mars 2000",DATUM["D_Mars_2000",SPHEROID["Mars_2000_IAU_IAG",3396190.0,169.89444722361179]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]')
# gdf = gpd.GeoDataFrame(columns=['Name'], crs =dst_crs)

for src_file in src_files:

    # img_src_file = src_file.split('.json')[0]+'.tiff'
    src_name, suffix = os.path.basename(src_file).split(f'{ssize}')
    tmp_gdf=(shapesExtractor(src_name, f'{ssize}', dst_dir, dst_crs, src_file))
    try:
        if tmp_gdf.shape!=None:
            if tmp_gdf.crs!=dst_crs:
                tmp_gdf = tmp_gdf.to_crs(dst_crs)
            if src_file == src_files[0]:
                gdf = tmp_gdf

            else:
                gdf = gpd.GeoDataFrame(pd.concat([gdf,tmp_gdf]).drop_duplicates().reset_index(drop=True), crs=dst_crs)
    except Exception as e:
        print(e)
        print(src_file)



gdf.to_file(src_dir+'/labeled_shapes.gpkg',driver="GPKG")
# gdf.to_crs(dst_crs)
gdf.to_file(src_dir+'/labeled_shapes_crs.gpkg',driver="GPKG")
