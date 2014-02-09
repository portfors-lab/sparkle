import re
import os

import numpy as np

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

def convert2native(obj):
    if hasattr(obj, '__iter__'):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            if isinstance(obj, dict):
                # does not convert dict keys
                for key, value in obj.items():
                    obj[key] = convert2native(value)
                return obj
            else:
                objtype = type(obj)
                return objtype([convert2native(item) for item in obj])
    elif type(obj).__module__ == np.__name__:
        return np.asscalar(obj)
    else:
        return obj
