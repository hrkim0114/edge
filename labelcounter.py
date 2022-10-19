import os
import sys
import time
import glob
import math
import xmltodict
import pandas as pd
import numpy as np
import multiprocessing as mp
import parmap
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(
    description='produce the label list from xml files in the input directory and subfolders,\
 and select part of them according to the bbox size')
parser.add_argument('mode', type=str, help='save: search xml files and save .csv file / load: load .csv file')
parser.add_argument('-d', '--dir', type=str, help='target directory (save) or .csv file (load)')
parser.add_argument('-o', '--opt', type=int, default=0, help='0: count class / 1: get a list of large area boxes (load)')
parser.add_argument('-t', '--thres', type=int, default=0, help='threshold (load)')
parser.add_argument('-c', '--count', type=bool, default=False, help='False: nothing / True: dir count')
args = parser.parse_args()

pd.set_option('display.max_rows', 100) # display limit

def label_counter(dir_name):
    if not os.path.isdir(dir_name):
        print("Input directory does not exist!")
        return
    
    print("[INFO] Searching xml directories...\n")
    xmlist = np.array(make_xmlist(dir_name))
    num_cores = mp.cpu_count()
    splited_xmlist = np.array_split(xmlist, num_cores)
    splited_xmlist = [x.tolist() for x in splited_xmlist]

    print("[INFO] Preparing to collect data...\n")
    sh = mp.Manager().list()

    print("[INFO] Use {} cores of CPU".format(num_cores))
    result = parmap.map(convert_label, splited_xmlist, sh, pm_pbar=True, pm_processes=num_cores)
    
    print("[INFO] Converting to DataFrame...\n")
    xml_df = pd.DataFrame(sh.__deepcopy__({}), columns=['class', 'box_w', 'box_h', 'box_s', 'img_w', 'img_h', 'dir'])
    
    xml_df.to_csv('{}.csv'.format(dir_name))
    print("[INFO] Saved file: {}/{}.csv\n".format(os.getcwd(), dir_name))

def make_xmlist(dir):
    xmlist = []
    for path, dir, files in os.walk(dir):
        xmlist += glob.glob(os.path.join(path, '*.xml'))
    return xmlist

def convert_label(xmlist, sh):
    for in_file_name in tqdm(xmlist):
        in_file = open(in_file_name, 'r')
        xml_dict = xmltodict.parse(in_file.read())
        in_file.close()
        size = xml_dict['annotation'].get('size', None)
        objs = xml_dict['annotation'].get('object', None)

        if not objs:
            sh.append([None, None, None, None, size['width'], size['height'], in_file_name])
        elif type(objs) == list:
            for obj in objs:
                cl, bw, bh, bs = parse_obj(obj)
                sh.append([cl, bw, bh, bs, size['width'], size['height'], in_file_name])
        else:
            cl, bw, bh, bs = parse_obj(objs)
            sh.append([cl, bw, bh, bs, size['width'], size['height'], in_file_name])

def parse_obj(obj):
    cl = obj['name']
    bw = int(obj['bndbox']['xmax']) - int(obj['bndbox']['xmin'])
    bh = int(obj['bndbox']['ymax']) - int(obj['bndbox']['ymin'])
    bs = math.sqrt(bw * bh)
    return cl, bw, bh, bs

def loader(file_name, option, th, cnt):
    xml_df = pd.read_csv(file_name)

    xml_df['dir_split'] = xml_df['dir'].str.split('\\').str[-4:-1]
    
    if option == 0: # bounding box count
        print("\n<All bounding boxes>\n")
        print("**Data : {}\n".format(file_name))
        print("**Total bndbox : {}\n".format(xml_df['dir'].count()))
        print("**Class count (bndbox)\n", xml_df['class'].value_counts(dropna=False)) # class count
        if cnt:
            print("\n**Dir count (bndbox)\n", xml_df['dir_split'].value_counts(dropna=False)) # dir count (args.count == True)
    elif option == 1: # image file count
        xml_list = get_list_large_box_image(xml_df, th, cnt)
        print("\nsave this list? (y/n)")
        ans = input()
        if (ans == 'Y') | (ans == 'y'):
            with open('train.txt', 'w', encoding='UTF-8') as f:
                for file in xml_list:
                    f.write(file+'\n')
            print("[INFO] Saved file: {}/train.txt".format(os.getcwd()))

def get_list_large_box_image(xml_df, th, cnt):
    xml_df.sort_values(by=['box_s'], inplace=True)
    isdupl = xml_df.duplicated(['dir'])
    unique_df = xml_df[~isdupl]
    filtered_df = unique_df[(unique_df['box_s'] >= th) | (unique_df['box_s'].isnull())]

    large_list = list(set(filtered_df['dir']))
    large_list.sort()
    xml_total = set(xml_df['dir'])
    
    for i, s in enumerate(large_list):
        large_list[i] = os.path.join(os.getcwd(), s.replace('.xml', '.jpg'))

    print("\n<Get files not including small boxes>\n")
    print("**threshold (area)\t: {}".format(th))
    print("**files\t\t\t: {} / {}\n".format(len(large_list), len(xml_total)))
    print("**Class count (files)\n", filtered_df['class'].value_counts(dropna=False)) # class count
    if cnt:
        print("\n**Dir count (files)\n", filtered_df['dir_split'].value_counts(dropna=False)) # dir count (args.count == True)

    return large_list

if __name__ == '__main__':
    start = time.time()
    
    if (args.mode == 'save') & bool(args.dir):
        print(args.dir)
        label_counter(args.dir)
        print("[INFO] Overall time : {} s".format(round(time.time() - start, 3)))
    elif (args.mode == 'load') & bool(args.dir):
        loader(args.dir, args.opt, args.thres, args.count)
    else:
        print("usage: labelcounter.py [-h] [-d DIR] [-o OPT] [-t THRES] [-c COUNT] mode")
