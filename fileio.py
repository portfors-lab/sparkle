import scipy.io as sio
import numpy as np
import pickle
import json

from os.path import splitext

def mightysave(filename, data, filetype='auto'):

    if filetype == 'auto':
        # use the filename extension to determine
        # file format
        root, filetype = splitext(filename)

    filetype = filetype.replace('.', '')

    if filetype not in ['txt', 'npy', 'mat', 'pkl', 'json']:
        print('unsupported format ', filetype)
        return -1

    try:
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
            with open(filename, 'w') as jf:
                json.dump(data, jf)
        print('saved')
    except:
        print('saving failed')
        raise
        return -2

    return 0
