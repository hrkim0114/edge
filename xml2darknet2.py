import os
import sys
import xmltodict
from itertools import chain
from collections import OrderedDict

COCO_CLASSES = [
    '0',
    '1', '2', '3', '4', '5', '6', '8', '9', '10', '11', '12', '13', '14', '15', '16', '18', '19', '20',
    '21', '22', '23', '24', '25', '26', '28', '29', '30', '31', '32', '33', '34', '35', '36', '38', '39', '40',
    '41', '42', '43', '44', '45', '46', '48', '49', '50', '51', '52', '53', '54', '55', '56', '58', '59', '60',
    '61', '62', '63', '64', '65', '66', '68', '69', '70', '71', '72', '73', '74', '75', '76', '78', '79', '80',
    '81', '82', '83', '84', '85', '86', '88', '89', '90', '91'
]

COCO_FILTERED_CLASSES = [
    '0','1','2','3','4','5','6','7','8','9'
]


#CLASSES = COCO_CLASSES
CLASSES = COCO_FILTERED_CLASSES

def parse_obj(obj, width, height):
    cls = CLASSES.index(str(obj['name']))
    w = round(((float(obj['bndbox']['xmax']) - float(obj['bndbox']['xmin'])) / width), 6)
    h = round(((float(obj['bndbox']['ymax']) - float(obj['bndbox']['ymin'])) / height), 6)
    x = round((float(obj['bndbox']['xmin']) / width) + (w / 2), 6)
    y = round((float(obj['bndbox']['ymin']) / height) + (h / 2), 6)
    if(x>1.0):
        x=1.0
    if(y>1.0):
        y=1.0
    if(w>1.0):
        w=1.0
    if(h>1.0):
        h=1.0
    return cls, x, y, w, h

def convert_label(in_file_name):
    in_file = open(in_file_name, 'r')
    xml_dict = xmltodict.parse(in_file.read())
    in_file.close()
    objs = xml_dict['annotation'].get('object', None)
    sz = xml_dict['annotation'].get('size', None)
    width = float(sz['width'])
    height = float(sz['height'])

    if not objs:
        print (in_file_name + ' no object')
        return ''

    if type(objs) == list:
        labels = ''
        for obj in objs:
            cls, x, y, w, h = parse_obj(obj, width, height)
            labels += '{} {} {} {} {}\n'.format(cls, x, y, w, h)
        return labels

    cls, x, y, w, h = parse_obj(objs, width, height)
    return '{} {} {} {} {}'.format(cls, x, y, w, h)


def iter_conv_labels(xml_dir, darknet_labels_dir):
    for f in os.listdir(xml_dir):
        if '.xml' in f:
            print(f)
            in_file_name = '{}/{}'.format(xml_dir, f)
            out_file_name = '{}/{}'.format(darknet_labels_dir, f.replace('.xml', '.txt'))
            out_file = open(out_file_name, 'w')
            out_file.write(convert_label(in_file_name))
            out_file.close()

if __name__ == '__main__':
    #if len(sys.argv) != 3:
    #    debug('Not enough arguments.')
    #    debug('Usage: python %s [in:pascal_xml_dir] [out:darknet_labels_dir]' % sys.argv[0])
    #    exit()

    #xml_dir = sys.argv[1]
    #darknet_labels_dir = sys.argv[2]
    #dirnames = ["ffish","vertical","vocperson","voccarr","voc","val2017","train2017","negative","lprdata","cocoperson","cococar","car2"]
    #dirnames = ["../Violence/compelete/AIHub_Violence","../Violence/compelete/KISA_overseas","../Violence/compelete/KISA_Violence"]
    #dirnames = ["../../dataset/Its_vmsoft_relabel/train", "../../dataset/Its_vmsoft_relabel/valid"]
    #for dirname in dirnames :
    #    iter_conv_labels(dirname, dirname)

    iter_conv_labels(sys.argv[1], sys.argv[1])



