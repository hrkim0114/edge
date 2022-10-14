import os
import sys
import time
import glob
import xmltodict
import pandas as pd
import numpy as np
from multiprocessing import Process, freeze_support, Manager

xml_df = pd.DataFrame(columns=['class', 'box_w', 'box_h', 'box_s', 'img_w', 'img_h', 'dir', 'f_name'])

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
    xmlist = []
    for path, dir, files in os.walk(dir):
        xmlist += glob.glob(os.path.join(path, '*.xml'))
    
    return xmlist

def label_counter(xmlist):
    global xml_df
    for i, f in enumerate(xmlist):
        xml_df = pd.concat([xml_df, convert_label(f)])
        print("count : {} ".format(i))
    
    # return xml_df

if __name__ == '__main__':
    freeze_support()
    # input the target directory (ex. set_k_train)
    start = time.time()
    
    manager = Manager()
    ns = manager.Namespace()
    ns.df = xml_df

    xmlist = make_xmlist(sys.argv[1])
    n = 4
    
    sp = len(xmlist)//n
    xmlists = [xmlist[:sp]]
    if n > 2:
        for i in range(n):
            xmlists.append(xmlist[sp*(n-2):sp*(n-1)])
    xmlists.append(xmlist[sp*(n-1):])
    
    for i, num in enumerate(n):
        proc = Process(target=label_counter, args=(xmlists[i]))
        procs.append(proc)
        proc.start()
    
    for proc in procs:
        proc.join()
    
    # save
    xml_df.to_csv('test.csv')

    # print output !
    print("Total bndbox : {}".format(xml_df['class'].count()))
    print(xml_df.info())
    print(xml_df.describe())
    print(xml_df['class'].value_counts())
    print("time : {} s".format(round(time.time() - start, 3)))