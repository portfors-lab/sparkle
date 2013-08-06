from __future__ import with_statement
import scipy.io as spio
import numpy as np
import pickle
import json

from os.path import splitext
from copy import deepcopy
from io import open

def mightysave(filename, data, filetype=u'auto'):

    root, ext = splitext(filename)
    if filetype == u'auto':
        # use the filename extension to determine
        # file format
        filetype = ext

    filetype = filetype.replace(u'.', u'')

    if filetype not in [u'txt', u'npy', u'mat', u'pkl', u'json']:
        print u'unsupported format ', filetype
        return -1

    try:
        if ext == u'':
            filename = filename + u'.' + filetype
        print u'saving ', filename
        if filetype == u'txt':
            np.savetxt(filename, data)
        elif filetype == u'npy':
            np.save(filename, data)
        elif filetype == u'mat':
            if not isinstance(data, dict):
                data = {u'matdata': deepcopy(data)}
            spio.savemat(filename, data)
        elif filetype == u'pkl':
            with open(filename, u'wb') as pf:
                pickle.dump(data, pf)
        elif filetype == u'json':
            if isinstance(data,np.ndarray):
                data = deepcopy(data).tolist()
            elif isinstance(data, dict):
                data = np2native(deepcopy(data))
            with open(filename, u'w') as jf:
                json.dump(data, jf)
    except:
        print u'saving failed'
        raise
        return -2

    return 0

def mightyload(filename, filetype=u'auto'):
    root, ext = splitext(filename)
    if filetype == u'auto':
        # use the filename extenspion to determine
        # file format
        filetype = ext

    filetype = filetype.replace(u'.', u'')

    if filetype not in [u'txt', u'npy', u'mat', u'pkl', u'json', u'hdf5']:
        print u'unsupported format ', filetype
        return -1

    try:
        print u'loading ', filename
        if filetype == u'txt':
            data = np.loadtxt(filename)
        elif filetype == u'npy':
            data = np.load(filename)
            data = data.item()
        elif filetype == u'mat':
            data = loadmat(filename)
        elif filetype == u'pkl':
            with open(filename, u'rb') as pf:
                data = pickle.load(pf)
        elif filetype == u'json':
            with open(filename, u'r') as jf:
                data = json.load(jf)
        else:
            print u'unsupported format ', filetype
            return -1
        
    except:
        print u'Loading failed'
        raise
        return None

    return data

def np2native(d):
    for key, item in d.items():
        if isinstance(item, dict):
            item = np2native(item)        
        elif isinstance(item,np.ndarray):
            item = item.tolist()
        elif type(item).__module__ == np.__name__:
            item = np.asscalar(item)
        d[key] = item

    return d

def loadmat(filename):
    u'''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    u'''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict        

def _todict(matobj):
    u'''
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
