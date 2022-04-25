#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: 
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Mon Sep 28 11:58:29 2020
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""
# from utils.ImgUtils import Area

import math

def Dim2Tile(max_dim, dimension):
    # tile = int(round(dimension/min_val,0))   
    tile = math.ceil(dimension/max_dim)
    return(tile)


from PIL import Image
Image.MAX_IMAGE_PIXELS = None
# import numpy as np 
    
# import cv2 as cv


# def TileCheckSave(img, save_name, vt, ht, iw, ih):
#     width, height = img.size
#     x = int(width/vt*iw)
#     y = int(height/ht*ih)
#     h = int((height/ht))
#     w = int((width/vt))

#     im = np.array(img)
#     tile = im[y:y+h, x:x+w]
#     area = Area(tile)
#     if area <8192:
#         print("\nImage too small, skipping...", area,' pixels')
#     else:
#         cv.imwrite(save_name,tile)

def TileNumCheck(vt, ht, width, height, size):
    if vt == 0:
        vt+=1
        vv = height/vt
    if ht == 0:
        ht+=1
    
    vv = height/vt
    hh = width/ht
    if vv/hh > 2:
        ht+=1
    if hh/vv >2:
        vt+=1
    return(vt, ht)
# def TileNumCheck(tilenum, dimension, size):
#     try:
#         ratio = dimension/tilenum
#         if ratio < size:
#             tilenum-=1
#             if tilenum ==0:
#                 tilenum+=1
#     except Exception as e:
#         print(e)
#         tilenum = 1
   
#     return(tilenum)
