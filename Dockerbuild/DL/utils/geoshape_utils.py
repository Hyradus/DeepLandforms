#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: giacomo.nodjoumi@hyranet.info - g.nodjoumi@jacobs-university.de
"""
import json
import numpy as np
import geopandas as gpd
import pandas as pd
import pathlib
from rasterio.features import shapes as sp
import shapely
import shapely.geometry
from skimage import measure
import os

def parallel_funcs(masks, JOBS, func, aff):
    from joblib import Parallel, delayed
    result = Parallel (n_jobs=JOBS)(delayed(func)(masks[i,:,:], aff)
                            for i in range(len(masks)))
    return(result)

def chunk_creator(item_list, chunksize):
    import itertools
    it = iter(item_list)
    while True:
        chunk = tuple(itertools.islice(it, chunksize))
        if not chunk:
            break
        yield chunk

def mask2shape(msk, aff):
    for shape, value in sp(msk.astype(np.uint8), mask=(msk>0) ,transform = aff):
        shape_list=shapely.geometry.shape(shape)
    return(shape_list)


def pred2coco(masks, pred_clas, img_path, classes, out_dir):
    annotations = {
      "version": "4.5.6",
      "flags": {},
      "shapes": [],
      "imagePath": pathlib.Path(img_path).name,
      "imageData": None,
      "imageHeight": None,
      "imageWidth": None
    }
    for i in range(len(masks)):
        msk = masks[i,:,:]
        try:
            cnt_msk = measure.find_contours(msk, 0.8)
            cnt_msk_flip = np.flip(cnt_msk[0], axis=1)
            segment = cnt_msk_flip.tolist()
            shape_mask = {
            "label": classes[pred_clas[i]],
            "points": segment,
            "group_id": None,
            "shape_type": "polygon",
            "flags": {}
            }
            annotations["imageHeight"] = msk.shape[0]
            annotations["imageWidth"] = msk.shape[1]
            annotations['shapes'].append(shape_mask)
        except:
            pass
            
    json_name = out_dir+'/'+os.path.splitext(pathlib.Path(img_path).name)[0]+'.json'#.split('.')[0]+'.json'
    out_file = open(json_name, 'w')
    json.dump(annotations,out_file,indent=2)
    out_file.close()   
    
def pred2shapeWin(outputs, l, image_path, aff, src_crs, classes, JOBS, out_dir, i):
    masks = outputs['instances'].pred_masks.cpu().numpy()
    pred_clas = outputs['instances'].pred_classes.cpu().numpy().tolist()
    score = outputs['instances'].scores.cpu().numpy().tolist()
    cols = ['Name','Class','Score']#, 'lon','lat']
    inf_df =pd.DataFrame(columns=cols)
    inf_df['Class']=[classes[i] for i in pred_clas]
    inf_df['Score']=score
    inf_df['Name']=pathlib.Path(image_path).name.split('.')[0]+'_{l}.tiff'
    #aff = img.transform
    #src_crs = img.crs.to_wkt()
    src_crs = src_crs.to_wkt()
    #img.close()
    pred2coco(masks, pred_clas, image_path, classes, out_dir)
    poly_list = parallel_funcs(masks, JOBS, mask2shape, aff)
    gdf = gpd.GeoDataFrame(data=inf_df, geometry = poly_list, crs=src_crs)
    #if dst_crs != gdf.crs:
    #    gdf.to_crs(dst_crs)
    #gdf.to_file(out_dir+'/gp_'+str(i)+'.gpkg', driver='GPKG', crs=src_crs)     
    return(gdf)#, poly_list)    

    
    
def pred2shape(outputs, image_path, img, classes, JOBS, out_dir, i):
    masks = outputs['instances'].pred_masks.cpu().numpy()
    pred_clas = outputs['instances'].pred_classes.cpu().numpy().tolist()
    score = outputs['instances'].scores.cpu().numpy().tolist()
    cols = ['Name','Class','Score']#, 'lon','lat']
    inf_df =pd.DataFrame(columns=cols)
    inf_df['Class']=[classes[i] for i in pred_clas]
    inf_df['Score']=score
    inf_df['Name']=pathlib.Path(image_path).name#.split('.')[0]
    aff = img.transform
    src_crs = img.crs.to_wkt()
    img.close()
    pred2coco(masks, pred_clas, image_path, classes, out_dir)
    poly_list = parallel_funcs(masks, JOBS, mask2shape, aff)
    gdf = gpd.GeoDataFrame(data=inf_df, geometry = poly_list, crs=src_crs)
    #if dst_crs != gdf.crs:
    #    gdf.to_crs(dst_crs)
    #gdf.to_file(out_dir+'/gp_'+str(i)+'.gpkg', driver='GPKG', crs=src_crs)     
    return(gdf)#, poly_list)    

def crs_validator(geoshapes, gdf):
    if geoshapes.crs != gdf.crs:
        reprj_gdf.to_crs(geoshapes.crs)
    return(reprj_gdf)
