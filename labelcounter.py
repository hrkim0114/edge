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
    for i in range(7):
        globals()['sh{}'.format(i)] = mp.Manager().list()

    print("[INFO] Use {} cores of CPU".format(num_cores))
    result = parmap.map(convert_label, splited_xmlist, sh0, sh1, sh2, sh3, sh4, sh5, sh6, pm_pbar=True, pm_processes=num_cores)

    print("[INFO] Converting to DataFrame...\n")
    dsh = dict()
    keys = ['class', 'box_w', 'box_h', 'box_s', 'img_w', 'img_h', 'dir']
    for i, l in enumerate([sh0, sh1, sh2, sh3, sh4, sh5, sh6]):
        dsh[keys[i]] = l.__deepcopy__({})
    
    xml_df = pd.DataFrame(dsh)

    xml_df.to_csv('{}.csv'.format(dir_name))
    print("[INFO] Saved file: {}/{}.csv\n".format(os.getcwd(), dir_name))

def make_xmlist(dir):
    xmlist = []
    for path, dir, files in os.walk(dir):
        xmlist += glob.glob(os.path.join(path, '*.xml'))
    return xmlist

def convert_label(xmlist, sh0, sh1, sh2, sh3, sh4, sh5, sh6):
    for in_file_name in xmlist:
        in_file = open(in_file_name, 'r')
        xml_dict = xmltodict.parse(in_file.read())
        in_file.close()
        size = xml_dict['annotation'].get('size', None)
        objs = xml_dict['annotation'].get('object', None)

        if not objs:
            sh0.append(-1)
            sh1.append(-1)
            sh2.append(-1)
            sh3.append(-1)
            sh4.append(size['width'])
            sh5.append(size['height'])
            sh6.append(in_file_name)
        elif type(objs) == list:
            for obj in objs:
                cl, bw, bh, bs = parse_obj(obj)
                sh0.append(cl)
                sh1.append(bw)
                sh2.append(bh)
                sh3.append(bs)
                sh4.append(size['width'])
                sh5.append(size['height'])
                sh6.append(in_file_name)
        else:
            cl, bw, bh, bs = parse_obj(objs)
            sh0.append(cl)
            sh1.append(bw)
            sh2.append(bh)
            sh3.append(bs)
            sh4.append(size['width'])
            sh5.append(size['height'])
            sh6.append(in_file_name)

def parse_obj(obj):
    cl = obj['name']
    bw = int(obj['bndbox']['xmax']) - int(obj['bndbox']['xmin'])
    bh = int(obj['bndbox']['ymax']) - int(obj['bndbox']['ymin'])
    bs = math.sqrt(bw * bh)
    return cl, bw, bh, bs

def loader(file_name, option, th):
    xml_df = pd.read_csv(file_name)
    
    if option == 0:
        print("**Data : {}\n".format(file_name))
        print("**Total bndbox : {}\n".format(xml_df['class'].count()))
        print("**Class count\n", xml_df['class'].value_counts())
    elif option == 1:
        list = get_list_large_box(xml_df, th)
        print(list)

def get_list_large_box(xml_df, th):
    islarge = xml_df['box_s'] >= th
    large_list = xml_df[islarge]['dir'].replace('.xml','')
    return large_list

def main():
    print("main")

if __name__ == '__main__':
    start = time.time()
    
    if (sys.argv[1] == 'search') & (len(sys.argv) == 3):
        label_counter(sys.argv[2])
        print("[INFO] Overall time : {} s".format(round(time.time() - start, 3)))
    elif (sys.argv[1] == 'load') & (len(sys.argv) >= 3):
        if not sys.argv[3]:
            loader(sys.argv[2], 0, 0)
        else:
            loader(sys.argv[2], sys.argv[3], sys.argv[4])
        print("[INFO] Overall time : {} s".format(round(time.time() - start, 3)))
    else:
        print("----------Usage----------\n")
        print("labelcounter.py (search 'directory' / load 'file_name.csv' [option1] [option2])")
        print("[option1]: 0 -> count class (default) / 1 -> get list of large boxes (area)")
        print("[option2]: threshold")