import os
import sys
import time
import xmltodict
import pandas as pd
import numpy as np

def parse_obj(obj):
    cl = obj['name']
    bw = int(obj['bndbox']['xmax']) - int(obj['bndbox']['xmin'])
    bh = int(obj['bndbox']['ymax']) - int(obj['bndbox']['ymin'])
    bs = bw * bh

    return cl, bw, bh, bs

def convert_label(in_file_name):
    in_file = open(in_file_name, 'r')
    xml_dict = xmltodict.parse(in_file.read())
    in_file.close()
    size = xml_dict['annotation'].get('size', None)
    objs = xml_dict['annotation'].get('object', None)
    
    d = pd.DataFrame({
        'class': [None], 'box_w': [None], 'box_h': [None], 'box_s': [None],
        'img_w': [None], 'img_h': [None], 'dir': [None], 'f_name': [None]
        })
    
    d['img_w'] = size['width']
    d['img_h'] = size['height']
    path_split = os.path.split(in_file_name)
    d['dir'] = path_split[0]
    d['f_name'] = path_split[1]

    if not objs:
        return d
    
    elif type(objs) == list:
        d_list = {
            'class': [], 'box_w': [], 'box_h': [], 'box_s': [],
            'img_w': [], 'img_h': [], 'dir': [], 'f_name': []
            }
        for i, obj in enumerate(objs):
            d_list['img_w'].append(size['width'])
            d_list['img_h'].append(size['height'])
            d_list['dir'].append(path_split[0])
            d_list['f_name'].append(path_split[1])
            cl, bw, bh, bs = parse_obj(obj)
            d_list['class'].append(cl)
            d_list['box_w'].append(bw)
            d_list['box_h'].append(bh)
            d_list['box_s'].append(bs)
        return pd.DataFrame(d_list)
    
    else:
        d['class'], d['box_w'], d['box_h'], d['box_s'] = parse_obj(objs)
        return d

def make_xmlist(dir):
    print("Gathering xml directories...")
    xmlist = np.array([])
    # filenames = os.listdir(dir)
    # for filename in filenames:
    #     name = os.path.join(dir,filename)
    #     if os.path.isdir(name):
    #         temp = make_xmlist(name)
    #         xmlist = np.concatenate((xmlist, temp))
    #     else:
    #         if '.xml' in name:
    #             xmlist = np.append(xmlist, name)
    
    for path, dir, files in os.walk(dir):
        for file in files:
            if '.xml' in file:
                xmlist = np.append(xmlist, os.path.join(path, file))
    
    return xmlist

def label_counter(xmlist):
    xml_df = pd.DataFrame(columns=['class', 'box_w', 'box_h', 'box_s', 'img_w', 'img_h', 'dir', 'f_name'])

    for i, f in enumerate(xmlist):
        xml_df = pd.concat([xml_df, convert_label(f)])
        print("data file : {} ".format(i))
    
    return xml_df

if __name__ == '__main__':
    # input the target directory (ex. set_k_train)
    start = time.time()

    xmlist = make_xmlist(sys.argv[1])
    xmlist1 = 
    xml_df = label_counter(xmlist)

    # save
    xml_df.to_csv('test.csv')

    # print output !
    print("Total bndbox : {}".format(xml_df['class'].count()))
    print(xml_df.info())
    print(xml_df.describe())
    print(xml_df['class'].value_counts())
    print("time : {} s".format(round(time.time() - start, 3)))