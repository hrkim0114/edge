import os
import sys
import time
import glob
import xmltodict
import pandas as pd
import numpy as np
import multiprocessing as mp
import parmap
from tqdm import tqdm

def make_xmlist(dir):
    print("[INFO] Searching xml directories...\n")
    xmlist = []
    for path, dir, files in os.walk(dir):
        xmlist += glob.glob(os.path.join(path, '*.xml'))
    print("[INFO] Preparing to collect data...\n")
    return xmlist

def label_counter(xmlist, sh0, sh1, sh2, sh3, sh4, sh5, sh6):
    for i, f in enumerate(tqdm(xmlist)):
        convert_label(f, sh0, sh1, sh2, sh3, sh4, sh5, sh6)

def convert_label(in_file_name, sh0, sh1, sh2, sh3, sh4, sh5, sh6):
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
    bs = bw * bh

    return cl, bw, bh, bs

if __name__ == '__main__':
    # input the target directory (ex. set_k_train)
    start = time.time()

    xmlist = np.array(make_xmlist(sys.argv[1]))
    num_cores = mp.cpu_count()
    splited_xmlist = np.array_split(xmlist, num_cores)
    splited_xmlist = [x.tolist() for x in splited_xmlist]

    for i in range(7):
        globals()['sh{}'.format(i)] = mp.Manager().list()

    print("[INFO] Use {} cores of CPU".format(num_cores))
    result = parmap.map(label_counter, splited_xmlist, sh0, sh1, sh2, sh3, sh4, sh5, sh6, pm_pbar=True, pm_processes=num_cores)

    print("[INFO] Converting to DataFrame...")
    d = {'class': list(sh0), 'box_w': list(sh1), 'box_h': list(sh2), 'box_s': list(sh3), 'img_w': list(sh4), 'img_h': list(sh5), 'dir': list(sh6)}
    xml_df = pd.DataFrame(d)

    # save
    xml_df.to_csv('test.csv')
    print("[INFO] Saved csv file\n")

    # print output !
    print("\n---------------------------------------\n")
    print("Total bndbox : {}\n".format(xml_df['class'].count()))
    print("Class count", xml_df['class'].value_counts())
    print("\n", xml_df.head())
    print("\n", xml_df.describe())
    print("Overall time : {} s".format(round(time.time() - start, 3)))
