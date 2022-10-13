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
        for obj in objs:
            d['class'], d['box_w'], d['box_h'], d['box_s'] = parse_obj(obj)
            return d
    else:
        d['class'], d['box_w'], d['box_h'], d['box_s'] = parse_obj(objs)
        return d

def make_xmlist(dir):
    xmlist = []
    filenames = os.listdir(dir)
    for filename in filenames:
        name = os.path.join(dir,filename)
        if os.path.isdir(name):
            temp = make_xmlist(name)
            xmlist += temp
        else:
            ext = os.path.splitext(name)[-1]
            if ext == '.xml':
                xmlist.append(name)
                
    return xmlist

def label_counter(xml_dir):
    xml_df = pd.DataFrame(columns=['class', 'box_w', 'box_h', 'box_s', 'img_w', 'img_h', 'dir', 'f_name'])

    for i, f in enumerate(make_xmlist(xml_dir)):
        xml_df = pd.concat(xml_df, convert_label(f))
        print("data file : {} ".format(i))
    
    # print output !
    print("Total bndbox : {}".format(xml_df['class'].count()))
    print("Class count")
    for i, val in enumerate(xml_df['class'].value_counts()):
        print("{} : {}".format(xml_df['class'].value_counts().index[i], val))

    print(xml_df.info())
    print(xml_df.describe())
    print(xml_df['class'].value_counts())

if __name__ == '__main__':
    # input the target directory (ex. set_k_train)
    start = time.time()

    label_counter(sys.argv[1])

    print("time : {} s".format(round(time.time() - start, 3)))