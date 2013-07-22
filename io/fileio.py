import scipy.io as spio
import numpy as np
import pickle
import json

from os.path import splitext
from copy import deepcopy

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
                data = {'matdata': deepcopy(data)}
            spio.savemat(filename, data)
        elif filetype == 'pkl':
            with open(filename, 'wb') as pf:
                pickle.dump(data, pf)
        elif filetype == 'json':
            if isinstance(data,np.ndarray):
                data = deepcopy(data).tolist()
            elif isinstance(data, dict):
                data = np2list(deepcopy(data))
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
        # use the filename extenspion to determine
        # file format
        filetype = ext

    filetype = filetype.replace('.', '')

    if filetype not in ['txt', 'npy', 'mat', 'pkl', 'json', 'hdf5']:
        print('unsupported format ', filetype)
        return -1

    try:
        print('loading ', filename)
        if filetype == 'txt':
            data = np.loadtxt(filename)
        elif filetype == 'npy':
            data = np.load(filename)
            data = data.item()
        elif filetype == 'mat':
            data = loadmat(filename)
        elif filetype == 'pkl':
            with open(filename, 'rb') as pf:
                data = pickle.load(pf)
        elif filetype == 'json':
            with open(filename, 'r') as jf:
                data = json.load(jf)
        else:
            print('unsupported format ', filetype)
            return -1
        
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

def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict        

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict
