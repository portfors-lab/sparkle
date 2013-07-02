import scipy.io as sio
import numpy as np
import pickle
import json

from os.path import splitext

def mightysave(filename, data, filetype='auto'):

    root, ext = splitext(filename)
    if filetype == 'auto':
        # use the filename extension to determine
        # file format
        filetype = ext

    filetype = filetype.replace('.', '')

    if filetype not in ['txt', 'npy', 'mat', 'pkl', 'json']:
        print('unsupported format ', filetype)
        return -1

    try:
        if ext == '':
            filename = filename + '.' + filetype
        print('saving ', filename)
        if filetype == 'txt':
            np.savetxt(filename, data)
        elif filetype == 'npy':
            np.save(filename, data)
        elif filetype == 'mat':
            if not isinstance(data, dict):
                data = {'data':data}
            sio.savemat(filename, data)
        elif filetype == 'pkl':
            with open(filename, 'wb') as pf:
                pickle.dump(data, pf)
        elif filetype == 'json':
            if isinstance(data,np.ndarray):
                data = data.tolist()
            elif isinstance(data, dict):
                data = np2list(data)
            with open(filename, 'w') as jf:
                json.dump(data, jf)
    except:
        print('saving failed')
        raise
        return -2

    return 0

def mightyload(filename, filetype='auto'):
    root, ext = splitext(filename)
    if filetype == 'auto':
        # use the filename extension to determine
        # file format
        filetype = ext

    filetype = filetype.replace('.', '')

    if filetype not in ['txt', 'npy', 'mat', 'pkl', 'json']:
        print('unsupported format ', filetype)
        return -1

    try:
        print('loading ', filename)
        if filetype == 'txt':
            data = np.loadtxt(filename)
        elif filetype == 'npy':
            data = np.load(filename)
        elif filetype == 'mat':
            data = sio.loadmat(filename, data)
        elif filetype == 'pkl':
            with open(filename, 'rb') as pf:
                data = pickle.load(pf)
        elif filetype == 'json':
            with open(filename, 'r') as jf:
                data = json.load(jf)
    except:
        print('Loading failed')
        raise
        return None

    return data

def np2list(d):
    for key, item in d.items():
        if isinstance(item, dict):
            item = np2list(item)        
        elif isinstance(item,np.ndarray):
            item = item.tolist()
        d[key] = item

    return d
