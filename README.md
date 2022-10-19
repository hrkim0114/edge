# edge statistic tool
Darknet label file (.xml)

usage: labelcounter2.py [-h] [-d DIR] [-o OPT] [-t THRES] [-c COUNT] mode

produce the label list from xml files in the input directory and subfolders, and select part of them according to the bbox size

positional arguments:
mode                  save: search xml files and save .csv file / load: load .csv file

options:
-h, --help                  show this help message and exit
-d DIR, --dir DIR           target directory (save) or .csv file (load)
-o OPT, --opt OPT           0: count class / 1: get a list of large area boxes (load)
-t THRES, --thres THRES     threshold (load)
-c COUNT, --count COUNT     False: nothing / True: dir count 

## Requirement

python

xmltodict

pandas

numpy

parmap

tqdm
