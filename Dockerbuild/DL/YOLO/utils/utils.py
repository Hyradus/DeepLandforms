#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: giacomo.nodjoumi@hyranet.info - gnodjoumi@constructor.university
"""
import cv2
import geopandas as gpd
import math
import numpy as np
import os 
import pandas as pd
from rasterio.features import shapes as sp
from rasterio.windows import Window
import rasterio as rio
import shapely
from shapely import Point


def get_paths(PATH, ixt):
    import re
    import fnmatch
    #os.chdir(PATH)
    ext='*.'+ixt
    chkCase = re.compile(fnmatch.translate(ext), re.IGNORECASE)
    files = [f for f in os.listdir(PATH) if chkCase.match(f)]
    return(files)
    
def window_calc(bb, src_img):
    col_off = math.floor(bb[0])
    row_off = math.floor(bb[1])
    width = math.ceil(bb[2]-col_off)
    height = math.ceil(bb[3]-row_off)
    Win = Window(col_off,row_off,width, height)
    return(Win)

#def label_builder(poly_dict, coordinates, cls):
#    poly_dict['points']=[[int(x),int(y)] for x,y in coordinates]
#    poly_dict['label']=cls
#    return(poly_dict)

def mask2shape(msk, aff):
    for shape, value in sp(msk.astype(np.uint8), mask=(msk>0) ,transform = aff):
        shape_list=shapely.geometry.shape(shape)
    return(shape_list)


def bboxes2df(bboxes, classes, confs, cols, data_min=0, data_max=None):
    
    data = []
    for bb in bboxes:
        if data_max is None:
            data_max = len(bb)
        data_list = list(bb[data_min:data_max])
        #new_xywh.insert(0, data[5])
        #new_xywh.append(conf)
        data.append(data_list)
        
    yolo_df = pd.DataFrame(data=data,columns=cols)
    yolo_df['Class']=classes
    yolo_df['Conf']=confs
    return(yolo_df)
    #return(yolo_df[['Class','x','y','w','h','Conf']])
    
def bbox2points(df, src_image):    
    img = rio.open(src_image)
    aff = img.transform
    width = img.width
    height = img.height
    src_crs = img.crs
    cords = []
    for i in range(df.shape[0]):
        pX=df['x'].iloc[i]
        pY=df['y'].iloc[i]
        pXw=pX*width
        pYw=pY*height
        col, row = pXw, pYw
        coord=aff*(col,row)
        df.at[i,'long']=coord[0]
        df.at[i,'lat']=coord[1]
        cords.append(Point(coord[0],coord[1]))
    return(gpd.GeoDataFrame(data=df, geometry=cords, crs=src_crs))

    
def box2geotiff(bbox, img, dst_dir, image_name, ext, cls, i):
    import numpy as np

    input_box = np.array(bbox)
    wind =window_calc(input_box, img)
    dst_trs = img.window_transform(wind)
    dst_crs = img.crs
    w = img.read(window=wind)
    image_det_dir = f"{dst_dir}/{image_name}"
    os.makedirs(image_det_dir, exist_ok=True)
    dst_name = f"{image_det_dir}/{image_name}_ID{i}_{cls}{ext}"
    with rio.open(dst_name,'w',
              driver='GTiff',
              width=wind.width,
              height=wind.height,
              count=img.count,
              dtype=img.dtypes[0],
              transform=dst_trs,
              crs=dst_crs) as dst:
        dst.write(w)
        return(w)
                  
def box2sam(predictor, image, bbox, img_crs, conf, cls):
    img = rio.open(image)
    image_name, ext = os.path.splitext(os.path.basename(image))
    predictor.set_image(cv2.imread(image))
    masks, _, _ = predictor.predict(
    point_coords=None,
    point_labels=None,
    box=bbox,
    multimask_output=False,
    )
    
    shp_data = {
    'Image': [image_name],
    'Class':[cls],
    'Conf':[conf]
    }
    geometry = mask2shape(masks[0], img.transform)
    binary_image = np.uint8(masks[0]) * 255
    contours , _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    outer_contour = contours[0]
    exterior_coordinates = outer_contour.squeeze().tolist()

    #cnt_msk_flip = np.flip(cnt_msk[0], axis=1)
    #segment = cnt_msk_flip.tolist()
    shape_dict = {
                "label": cls,
                "points": exterior_coordinates,
                "group_id": None,
                "shape_type": "polygon",
                "flags": {}
                }
    
    return(gpd.GeoDataFrame(data=shp_data, geometry= [geometry], crs = img_crs), shape_dict)


def PlotMap(geo_points):
    from localtileserver import TileClient, get_leaflet_tile_layer, examples
    from ipyleaflet import Map
    import rasterio as rio
    import leafmap
    from ipyleaflet import Map, WMSLayer, basemaps
    from owslib.wms import WebMapService
    from folium.plugins import Fullscreen, MeasureControl
    
    #import leafmap.foliumap as leafmap
    wms_url='https://explore.jacobs-university.de/geoserver/ows?service=WMS'
    layers='Mars_Viking_MDIM21_ClrMosaic_global_232m_crs',
    wms = WebMapService(
        url=wms_url,
        version='1.3.0'
    )
    body='Mars'
    my_projection = {
        "name": "EPSG:104905",
        "custom": True,  # This is important, it tells ipyleaflet that this projection is not on the predefined ones.
        #"proj4def": "+proj=longlat +a=3396190 +rf=169.894447223612 +no_defs +type=crs",
        "proj4def": "+proj=longlat +a=3396190 +b=3396190  +no_defs +type=crs",
        "origin": [0, 0],
        "bounds": [[-180, -90], [180, 90]],
        "resolutions": [8192.0, 4096.0, 2048.0, 1024.0, 512.0, 256.0],
    }
    wms_layers = list(wms.contents)
    
    if body=='Mars':
        baselayer='Mars:Mars_Viking_MDIM21_ClrMosaic_global_232m_crs_cog'
    if body=='Moon':
        'Moon:Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013-104903-cog'
    idx = wms_layers.index(baselayer)
    wms_layer = WMSLayer(url=wms_url, layers=wms_layers[idx], format='image/png', max_zoom=14, min_zoom=2,   crs=my_projection, tiles=True)
    # Create a TileClient from a raster file
    
    try:
        image_path = f"{test_dir}/{image_list[0]}"
        image = rio.open(image_path)
        client = TileClient(image_path)
        
        t = get_leaflet_tile_layer(client)
        map_select.add_layer(t)
    except:
        print('Image must by in EPSG:4326')
    
    map_select = leafmap.Map(
        basemap=wms_layer,
        tiles=True,    
        max_zoom=14,
        min_zoom=2,    
    )
    style = {
        "color": "#93c47d ",
        "weight": 5,
        "opacity": 100,
        "fill": True,
    }
    #map_select.set_view([(image.bounds.left, image.bounds.bottom), (image.bounds.right, image.bounds.top)])
    geo_points.crs = "EPSG:4326"
    map_select.add_gdf(geo_points,layer_name='PointsDetections',fill_colors=["red", "green", "blue"],style = style,)
    return(map_select)