#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: giacomo.nodjoumi@hyranet.info - gnodjoumi@constructor.university
"""
import os
import shutil


def get_paths(PATH, ixt):
    import re
    import fnmatch
    #os.chdir(PATH)
    ext='*.'+ixt
    chkCase = re.compile(fnmatch.translate(ext), re.IGNORECASE)
    files = [f for f in os.listdir(PATH) if chkCase.match(f)]
    return(files)

def dataMover(image_path, train, valid, test):
    ### TRAIN DATASET
    train_data_path = image_path+'/train_data'
    os.makedirs(train_data_path, exist_ok=True)
    for i in range(len(train)):
        file = train[i]['file_name']
        basename = os.path.basename(file.split('.tiff')[0])
        src_dir = os.path.dirname(file)
        shutil.copy(src_dir+'/'+basename+'.tiff',  train_data_path+'/'+basename+'.tiff')
        shutil.copy(src_dir+'/'+basename+'.json',  train_data_path+'/'+basename+'.json')
        train_file = train_data_path+'/dataset.json'
    #labelme2coco.convert(train_data_path, train_data_path)
    #train_dataset = detectron2.data.datasets.load_coco_json(train_file,
    #                        train_data_path, 'train_data')
    #register_coco_instances("train_data", {}, train_file, '')


    ### VALID DATASET
    valid_data_path = image_path+'/valid_data'
    os.makedirs(valid_data_path, exist_ok=True)
    for i in range(len(valid)):
        file = valid[i]['file_name']
        basename = os.path.basename(file.split('.tiff')[0])
        src_dir = os.path.dirname(file)
        dst_dir = valid_data_path
        shutil.copy(src_dir+'/'+basename+'.tiff', dst_dir+'/'+basename+'.tiff')
        shutil.copy(src_dir+'/'+basename+'.json', dst_dir+'/'+basename+'.json')
    #valid_file = valid_data_path+'/dataset.json'
    #labelme2coco.convert(valid_data_path, valid_data_path)
    #valid_dataset = detectron2.data.datasets.load_coco_json(valid_file,
    #                    valid_data_path, 'valid_data')
    #register_coco_instances("valid_data", {}, valid_file, '')


    ### TEST DATASET
    if len(test) >0:

        test_data_path = image_path+'/test_data'
        os.makedirs(test_data_path, exist_ok=True)
        for i in range(len(test)):
            file = valid[i]['file_name']
            basename = os.path.basename(file.split('.tiff')[0])
            src_dir = os.path.dirname(file)
            dst_dir = test_data_path
            shutil.copy(src_dir+'/'+basename+'.tiff', dst_dir+'/'+basename+'.tiff')
            shutil.copy(src_dir+'/'+basename+'.json', dst_dir+'/'+basename+'.json')
     #   test_file = test_data_path+'/dataset.json'
     #   labelme2coco.convert(test_data_path, test_data_path)
     #   test_dataset = detectron2.data.datasets.load_coco_json(test_file,
     #                       test_data_path, 'test_data')
     #   register_coco_instances("test_data", {}, test_file, '')