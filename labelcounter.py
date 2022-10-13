import os
import sys
import xmltodict
import pandas as pd
import numpy as np

xml_df = pd.DataFrame(columns=['class', 'box_w', 'box_h', 'box_s', 'img_w', 'img_h', 'dir', 'f_name'])

def parse_obj(obj):
    cl = objs['name']
    bw = int(objs['bndbox']['xmax']) - int(objs['bndbox']['xmin'])
    bh = int(objs['bndbox']['ymax']) - int(objs['bndbox']['ymin'])
    bs = bw * bh

    return cl, bw, bh, bs

def convert_label(in_file_name):
    in_file = open(in_file_name, 'r')
    xml_dict = xmltodict.parse(in_file.read())
    in_file.close()
    size = xml_dict['annotation'].get('size', None)
    objs = xml_dict['annotation'].get('object', None)
    
    d = pd.DataFrame({
        'class': [], 'box_w': [], 'box_h': [], 'box_s': [],
        'img_w': [], 'img_h': [], 'dir': [], 'f_name': []
        })
    
    d['img_w'] = size['width']
    d['img_h'] = size['height']
    path_split = os.path.split(in_file_name)
    d['dir'] = path_split[0]
    d['f_name'] = path_split[1]

    if not objs:
        d['class'] = None
        d['box_w'] = None
        d['box_h'] = None
        d['box_s'] = None
        df = df.concat([df, d])
    elif type(objs) == list:
        for obj in objs:
            d['class'], d['box_w'], d['box_h'], d['box_s'] = parse_obj(obj)
            df = df.concat([df, d])
    else:
        d['class'], d['box_w'], d['box_h'], d['box_s'] = parse_obj(obj)
        df = df.concat([df, d])

def make_xmlist(dir):
        xmlist =[]
        filenames = os.listdir(dir)
        for filename in filenames:
            name = os.path.join(dir,filename)
            if os.path.isdir(name):
                temp =make_xmlist(name)
                xmlist+=temp
            else:
                ext = os.path.splitext(name)[-1]
                if ext == '.xml':
                    print(name)
                    xmlist.append(name)
                    
        return xmlist

def label_counter(xml_dir):
    for f in make_xmlist(xml_dir):
        convert_label(f)
    # print output !
    # print output !
    df.head()

if __name__ == '__main__':
    # input the target directory (ex. set_k_train)

    label_counter(sys.argv[1])