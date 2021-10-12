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
    json_name = out_dir+'/'+os.path.splitext(pathlib.Path(img_path).name)[0]+'.json'#.split('.')[0]+'.json'
    out_file = open(json_name, 'w')
    json.dump(annotations,out_file,indent=2)
    out_file.close()   
    
    
def pred2shape(outputs, image_path, img, classes, JOBS, out_dir):
    masks = outputs['instances'].pred_masks.cpu().numpy()
    pred_clas = outputs['instances'].pred_classes.cpu().numpy().tolist()
    score = outputs['instances'].scores.cpu().numpy().tolist()
    cols = ['Name','Class','Score']#, 'lon','lat']
    inf_df =pd.DataFrame(columns=cols)
    inf_df['Class']=[classes[i] for i in pred_clas]
    inf_df['Score']=score
    inf_df['Name']=pathlib.Path(image_path).name#.split('.')[0]
    aff = img.transform
    dst_crs = img.crs.to_wkt()
    img.close()
    pred2coco(masks, pred_clas, image_path, classes, out_dir)
    poly_list = parallel_funcs(masks, JOBS, mask2shape, aff)
    gdf = gpd.GeoDataFrame(data=inf_df, geometry = poly_list, crs=dst_crs)
    return(gdf)#, poly_list)    

### add in pred2shape a function to call and read a DEM using the detected polygon
### or add/create a new function to do this after inference of 
