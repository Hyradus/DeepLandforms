#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 15:34:37 2022

@author: hyradus
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 16:43:59 2021

@author: hyradus
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: 
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de



Created on Tue Feb  9 00:30:48 2021
@author: @author: Giacomo Nodjoumi g.nodjoumi@jacobs-unversity.de
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
# try:
#     DF_in.groupby(['Classes']).count().plot(kind='bar')
#     DF_in.groupby(['Classes']).count()#.plot(kind='bar')
# except:
#     pass
# try:
#     DF_out.groupby(['Classes']).count().plot(kind='bar')
#     DF_out.groupby(['Classes']).count()#.plot(kind='bar')
#     DF_out.groupby(['Json']).count()#.plot(kind='bar')
# except:
#     pass    



        
#     with open(label) as f:
#                 json_data = json.load(f)
#                 types = []
#                 shapes = json_data['shapes']
#                 types = [shape['label'] for shape in shapes]
#                 # if all(e =='Crater' for e in types):
#                 if all(e in valid_classes for e in types):          
#                     # print(types, label)
#                     # continue
#                     valid_json_in.append(label)
#                     tmp_list = list(zip([label for typ in types], types))
#                     temp_df_in = pd.DataFrame.from_records(tmp_list,columns=['Json','Classes'])         
#                     DF_in = DF_in.append(temp_df_in, ignore_index=True)          
#                 # elif all(e in valid_classes for e in types):
                # else:
                #     valid_json_out.append(label)
                #     tmp_list = list(zip([label for typ in types], types))
                #     temp_df_out = pd.DataFrame.from_records(tmp_list,columns=['Json','Classes'])         
                #     DF_out = DF_out.append(temp_df_out, ignore_index=True)          
                # for typ in types:
                #     if re.search(valid_classes, typ):
                #         valid_json.append(label)
#                 f.close()
# val_in = list(set(DF_in['Json']))
# val_out = list(set(DF_out['Json']))
# try:
#     DF_in.groupby(['Classes']).count().plot(kind='bar')
#     DF_in.groupby(['Classes']).count()#.plot(kind='bar')
# except:
#     pass
# try:
#     DF_out.groupby(['Classes']).count().plot(kind='bar')
#     DF_out.groupby(['Classes']).count()#.plot(kind='bar')
#     DF_out.groupby(['Json']).count()#.plot(kind='bar')
# except:
#     pass    


# dst_dir = make_folder(src_dir, 'filtered_in')

# for jsf in valid_json_in:
#      with open(jsf) as f:
#         json_data = json.load(f)
#         basename = os.path.basename(jsf).split('.json')[0]
#         dst_jsf = dst_dir+'/'+basename+'.json'
#         json_data['imagePath'] = basename+'.json'
#         out_file = open(dst_jsf, 'w')
#         json.dump(json_data,out_file,indent=2)
#         out_file.close()   
#         src_image = jsf.split('.json')[0]+'.tiff'
#         dst_image = dst_dir+'/'+basename+'.tiff'
#         # shutil.copy(jsf,dst_jsf)
#         shutil.copy(src_image,dst_image)

# dst_dir2 = make_folder(src_dir, 'filtered_out')

# for jsf in valid_json_out:
#      with open(jsf) as f:
#         json_data = json.load(f)
#         basename = os.path.basename(jsf).split('.json')[0]
#         dst_jsf = dst_dir2+'/'+basename+'.json'
#         json_data['imagePath'] = basename+'_5m.json'
#         out_file = open(dst_jsf, 'w')
#         json.dump(json_data,out_file,indent=2)
#         out_file.close()   
#         src_image = jsf.split('.json')[0]+'.tiff'
#         dst_image = dst_dir+'/'+basename+'.tiff'
#         # shutil.copy(jsf,dst_jsf)
#         shutil.copy(src_image,dst_image)
#     # basename = os.path.basename(jsf).split('.json')[0]
#     # dst_jsf = dst_dir2+'/'+basename+'.json'
#     # src_image = jsf.split('.json')[0]+'.tiff'
#     # dst_image = dst_dir2+'/'+basename+'.tiff'
#     # shutil.copy(jsf,dst_jsf)
#     # shutil.copy(src_image,dst_image)


# # dst_dir2 = make_folder(src_dir, 'filtered2')    

# # for jsf in fff:
# #     basename = os.path.basename(jsf).split('.json')[0]
# #     dst_jsf = dst_dir2+'/'+basename+'_crater.json'
# #     src_image = jsf.split('.json')[0]+'.tiff'
# #     dst_image = dst_dir2+'/'+basename+'_crater.tiff'
# #     shutil.copy(jsf,dst_jsf)
# #     shutil.copy(src_image,dst_image)    

# # eee = ddd.loc[ddd['Classes']>(ddd['Classes'].max()/2)]
           