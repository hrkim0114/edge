import os
import sys
import xmltodict

CLASSES = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
]

# ddddd

# 1. search directories
# 2. find and read xml files
# 3. make lists ()
# 4. pleasure and joy
# 5. hello
# 6. 바보메롱

def make_xmlist(dir):
        xmlist =[]
        filenames = os.listdir(dir)
        for filename in filenames:
            name = os.path.join(dir,filename)
            if os.path.isdir(name):
                temp =print_file(name)
                xmlist+=temp
            else:
                ext = os.path.splitext(name)[-1]
                if ext == '.xml':
                    print(name)
                    xmlist.append(name)
                    
        return xmlist

def label_counter(xml_dir):
    for f in os.listdir(xml_dir):
        if '.xml' in f:
            in_file_name = '{}/{}'.format(xml_dir, f)
            out_file_name = '{}/{}'.format(os.getcwd(), f.replace('.xml', '.txt'))
            out_file = open(out_file_name, 'w')
            out_file.write()

if __name__ == '__main__':
    # input the top directory (ex. set_k_train)

    label_counter(sys.argv[1])