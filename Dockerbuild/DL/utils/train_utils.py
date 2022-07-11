#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: giacomo.nodjoumi@hyranet.info - g.nodjoumi@jacobs-university.de
"""
from colour import Color
import detectron2
from detectron2.data.datasets import register_coco_instances
from detectron2.data import MetadataCatalog
import labelme2coco
import os
import pandas as pd
from sklearn.model_selection import train_test_split
import shutil
from utils.GenUtils import dir_checker, get_paths, folder_file_size, chunk_creator
import json
from utils.ImageAugmenter import noiser, blurrer, Gamma, LogCorrect, LEqualizer, AdaptEqualizer, ImageAugmenter

def label2coco(base_dir, image_dir):
    #json_path = base_dir+'/custom_dataset.json'
#    image_path = image_dir
    train_dir = image_dir+'/train'
    os.makedirs(train_dir, exist_ok=True)    
    dataset_name = 'dataset'
    labelme2coco.convert(image_dir, train_dir)
    json_path = train_dir+'/dataset.json'
    return(dataset_name, image_dir, json_path, train_dir)

def classDump(meta,train_dir):
    #Dump classes
    classes = meta.thing_classes
    class_file = train_dir +'/trained_classes.csv'
    ddf = pd.DataFrame(classes)
    ddf.to_csv(class_file, index=False)
    return(classes)

def datasetReg(base_dir, image_dir):
    #dir_checker(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    dataset_name, image_path, json_path, train_dir = label2coco(base_dir, image_dir)
    dataset = detectron2.data.datasets.load_coco_json(json_path,
                        image_path, dataset_name)
    register_coco_instances(dataset_name, {}, json_path, image_path)
    meta = MetadataCatalog.get(dataset_name)
    classes = classDump(meta, train_dir)
    blue = Color("blue")
    green = Color("green")
    colors = list(blue.range_to(green, len(classes)))
    meta.set(thing_colors=colors)
    return(dataset, meta, classes, train_dir, image_path)

def getmeta(dataset_name, data_dir):
    meta = MetadataCatalog.get(dataset_name)
    classes = classDump(meta, data_dir)
    blue = Color("blue")
    green = Color("green")
    colors = list(blue.range_to(green, len(classes)))
    meta.set(thing_colors=colors)
    return(meta, classes)


def dsReg(data_path, ds_name, dataset_dir):
    file = data_path+'/dataset.json'
    labelme2coco.convert(data_path, data_path)
    dataset = detectron2.data.datasets.load_coco_json(file,
                            data_path, ds_name)
    register_coco_instances(ds_name, {}, file, data_path)
    meta = MetadataCatalog.get(ds_name)
    classes = classDump(meta, dataset_dir)
    blue = Color("blue")
    green = Color("green")
    colors = list(blue.range_to(green, len(classes)))
    meta.set(thing_colors=colors)
    return (dataset, meta, classes)

def data_split(dataset, valid, test):
    train, valid = train_test_split(dataset, test_size=valid, random_state=1,shuffle=True)
    valid, test = train_test_split(valid, test_size=test, random_state=1,shuffle=True)
    #test=None
    return(train, valid, test)

def categories_gen(dataset):
    categories = []
    for d in dataset:
        for ann in d['annotations']:
            categories.append(ann['category_id'])
    return(categories)


def classes_distribution(categories, datatype, classes):
    classes_dis=[]
    for cat in categories:
    #    print(classes[cat])
        classes_dis.append(classes[cat])
    classes_dis =list(zip(classes_dis,[datatype for i in range(len(classes_dis))]))
    df_dis = pd.DataFrame(classes_dis, columns=['Class','Dataset'])

    return(df_dis)

def dataframes_gen(classes, dataset,valid_size, test_size):
    train, valid, test = data_split(dataset,valid_size, test_size)
    train_categories = categories_gen(train)
    train_df_dis = classes_distribution(train_categories, 'Train', classes)

    valid_categories = categories_gen(valid)
    valid_df_dis = classes_distribution(valid_categories, 'Valid', classes)

    test_categories = categories_gen(test)
    test_df_dis = classes_distribution(test_categories, 'Test', classes)
    return(train_df_dis, valid_df_dis, test_df_dis, train, valid, test)


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

def parallel_augmenter(files, JOBS, img_ext, DSTdir, path):
    from joblib import Parallel, delayed
    Parallel (n_jobs=JOBS)(delayed(ImageAugmenter)(files[i], img_ext, DSTdir, path)
                            for i in range(len(files)))        
        
def trainaugmenter(path,DSTdir):
    img_ext = '.tiff'
    label_list = get_paths(path,'tiff')
    type_list =[]
    for file in label_list:
        jfile = file.split('tiff')[0]+'json'
        try:
            with open(path+'/'+jfile) as f:
                json_data = json.load(f)
                types = []
                shapes = json_data['shapes']
                types = [shape['label'] for shape in shapes]
                type_list.append(jfile)                
        except Exception as e:
            print(e)

    tlist = set(type_list)        
    type_list = list(tlist)            
    total_size, max_size, av_fsize = folder_file_size(path,type_list)

    from tqdm import tqdm
    import psutil

    avram=psutil.virtual_memory().total >> 30
    avcores=psutil.cpu_count(logical=False)
    avthreads=psutil.cpu_count(logical=True)
    ram_thread = avram/avthreads
    req_mem = avthreads*max_size
    if req_mem > avcores and req_mem > avram:
        JOBS = avcores
    else:
        JOBS = avthreads


    if ram_thread > 2:
        JOBS=avthreads
    
    with tqdm(total=len(type_list),
             desc = 'Generating Images',
             unit='File') as pbar:

        filerange = len(type_list)
        chunksize = round(filerange/JOBS)
        if chunksize <1:
            chunksize=1
            JOBS = filerange
        chunks = []
        for c in chunk_creator(type_list, JOBS):
            chunks.append(c)

        for i in range(len(chunks)):
            files = chunks[i]
            parallel_augmenter(files, JOBS, img_ext, DSTdir, path)
            pbar.update(JOBS)


