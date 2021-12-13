#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Mon Sep 28 18:45:02 2020
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
"""
import os
import shutil
from datetime import datetime

def dir_checker(directory):
    try:
        os.makedirs(directory)
    except Exception as e:
        print(e)
        qst = directory + ' Folder exist, remove it? '
        answ = question(qst,['yes','y','no','n'])
        if answ in ['yes', 'y']:
            shutil.rmtree(directory)
            os.makedirs(directory)
            print(directory, 'Folder created')
        else:
            pass


def question(question, answers):
    answ = None
    while answ not in answers:
        print('Please enter only: ')
        print(*answers, sep=', ')

        answ = input('\n'+question+'  Answer: ')
    return(answ)

def make_folder(path, name):
    # os.getcwd()
    folder = path+'/'+name
    if os.path.exists(folder):
           qst = name + ' Folder exist, remove it? '
           answ = question(qst,['yes','y','no','n'])
           if answ in ['yes', 'y']:
               shutil.rmtree(folder)
               os.mkdir(folder)
               print(name, 'Folder created')
           else:
               now = datetime.now()
               folder = name +'_' + now.strftime("%d-%m-%Y_%H-%M-%S")
               print(folder, ' Folder not exist, creating.')
               os.mkdir(folder)
               print('Created new ', name,' Folder')
    else:
        print(name, ' Folder not exist, creating.')
        os.mkdir(folder)
        print('Created new ', name,' Folder')
    return(folder)

# def get_paths(PATH, ixt):
#     import glob
#     os.chdir(PATH)
#     filename = [i for i in glob.glob('**/*.'+ixt,recursive=True)]
#     return(filename)


def get_paths(PATH, ixt):
    import re
    import fnmatch
    #os.chdir(PATH)
    ext='*.'+ixt
    chkCase = re.compile(fnmatch.translate(ext), re.IGNORECASE)
    files = [f for f in os.listdir(PATH) if chkCase.match(f)]
    return(files)

def folder_file_size(path, image_list):
    from statistics import mean
    sizes =[]
    gb = 1024*1024*1024
    mb=1024*1024
    for path, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(path, f)
            #sizes += os.path.getsize(fp)
            sizes.append((os.path.getsize(fp))/gb)
    max_size = max(sizes)
    av_fsize=mean(sizes)
    total_size = sum(sizes)
    return (total_size, max_size, av_fsize)

def intInput(w):
    while True:
        ask='Insert '+w+': '
        intInpt = int(input(ask))
        if type(intInpt) != int:
            print('Please insert only one integer')
            # continue
        if isinstance(intInpt, int):
                    break
    return(intInpt)


def chunk_creator(item_list, chunksize):
    import itertools
    it = iter(item_list)
    while True:
        chunk = tuple(itertools.islice(it, chunksize))
        if not chunk:
            break
        yield chunk

def get_types(folder):
    files  = get_paths(folder, '*')
    types = []
    for f in files:
        types.append(f.split('.')[1])
    uni_vals = set(types)
    return(uni_vals)

def askFile(f):
    ask = 'Insert path to '+ f
    while True:
        file = str(input(ask))
        if os.path.isfile(file) == True:
            print(file, 'is valid')
            break
        else:
            print(file, 'is not a valid path')
    return(file)

def askPath(p):
    ask = 'Insert path to ' + p
    while True:
        path = str(input(ask))
        if os.path.isdir(path) == True:
            print(path, 'is valid')
            break
        else:
            print(path,'is not a valid path')
    return(path)

def askInt(p):
    ask = 'Insert integer for '+ p
    while True:
        try:
            integ = int(input(ask))
            break
        except Exception as e:
            print(e)
    return(integ)

def askFloat(p):
    ask = 'Insert float for ' + p
    while True:
        try:
            flt = float(input(ask))
            break
        except Exception as e:
            print(e)
    return(flt)
