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

def max_str_num(prefix, strlist):
    exp = prefix + '(\d+)'
    searchfun = lambda x: re.search(exp, x)
    matches = map(searchfun, strlist)
    nums = [int(x.group(1)) for x in matches if x is not None]
    if len(nums) > 0:
        return max(nums)
    else:
        return 0

def next_str_num(prefix, strlist):
    n = max_str_num(prefix, strlist)
    return prefix + str(n + 1)

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
