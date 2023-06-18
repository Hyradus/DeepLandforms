#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 15:34:37 2022

@author: hyradus
"""
import shutil
from utils.GenUtils import get_paths, make_folder
import json
import os
import pandas as pd
# from pathlib import Path
src_dir = '/mnt/DATA/Working/Working_Pit_2022/MARSPIT_v2/MixRes/'

# dst_dir = make_folder(src_dir, 'Labeled')
json_list = get_paths(src_dir,'json')
import pandas
import re
valid_classes =['Type-1','Type-2','Type-3','Type-4']#,'Type-1b','Type-2a','Type-2b','Type-2','Type-3','Type-4','Crater']
# not_valid_classes =['Type-2','Type-3','Type-4','Crater']#,'Crater']
DF_in = pd.DataFrame([], columns=['Json','Classes'])
DF_out = pd.DataFrame([], columns=['Json','Classes'])
# single_class_labels = []y
jfiles = list(set(json_list))
valid_json_in = []
valid_json_out = []
dst_dir = make_folder(src_dir, 'filtered_in')
dst_dir2 = make_folder(src_dir, 'filtered_out')
for jsf in jfiles:
    jsf = src_dir+'/'+ jsf
    with open(jsf) as f:
        try:
            json_data = json.load(f)
            types = []
            shapes = json_data['shapes']
            types = [shape['label'] for shape in shapes]
            # if all(e =='Crater' for e in types):

            if shapes[0]['label'] in valid_classes:
                print('ok')
                basename=os.path.basename(jsf).split('.json')[0]
                src_image=f'{src_dir}/{basename}.tiff'
                dst_image=f'{dst_dir}/{basename}.tiff'
                dst_json=f'{dst_dir}/{basename}.json'
                shutil.copy(jsf, dst_json)
                shutil.copy(src_image, dst_image)
           # shutil.copy(src_image,dst_image)
        except:
            print(jsf)
