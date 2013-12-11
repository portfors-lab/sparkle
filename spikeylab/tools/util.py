import re
import os

def increment_title(title):
    """
    Increments a string that ends in a number
    """
    count = re.search('\d+$', title).group(0)
    new_title = title[:-(len(count))] + str(int(count)+1)
    return new_title

def create_unique_path(folder, file_template, ext='hdf5'):
    counter = 0
    while(os.path.isfile(os.path.join(folder, file_template+str(counter)+'.'+ext))):
        counter += 1
    path = os.path.join(folder, file_template+str(counter)+'.'+ext)
    return path


