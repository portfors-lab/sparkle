import numpy as np
import h5py
import datetime
from operator import add

from spikeylab.tools.exceptions import DataIndexError

class AcquisitionData():
    """
    Provides convenient access to raw data file; 
    each data file should represent an experimental session.

    Three types of datasets: 
    1. Finite datasets, where the amount of data to be stored in known
    in advance
    2. Open-ended aquisition, where the size of the acqusition window is
    know, but the number of traces to acquire is not
    3. Continuous acquisition, this is a 'chart' function where data is
    acquired continuously without break until the user stops the operation
    """
    def __init__(self, filename):
        # check that filename ends with '.hdf5', appending if necessary
        self.hdf5 = h5py.File(filename, 'w')
        self.datasets = {}
        self.meta = {}

    def close(self):
        self.hdf5.close()

    def init_data(self, key, dims, mode='finite'):
        if mode == 'finite':
            self.datasets[key] = self.hdf5.create_dataset(key, dims)
            self.meta[key] = {'mode':mode, 'cursor':[0]*len(dims)}
        elif mode == 'open':
            pass
        elif mode == 'continuous':
            pass
        else:
            raise Exception("Unknown acquisition mode")

    def append(self, key, data):
        mode = self.meta[key]['mode']
        if mode == 'finite':
            current_location = self.meta[key]['cursor']
            if data.shape == (1,):
                index = current_location
            else:
                index = current_location[:-len(data.shape)]
            # if data does crosses dimensions of datastructure, raise error
            # turn the index into a tuple so not to trigger advanced indexing
            print 'dataset shape', self.datasets[key].shape, 'index', index
            self.datasets[key][tuple(index)] = data[:]
            dims = self.datasets[key].shape
            increment(current_location, dims, data.shape)

    def insert(self, key, index, data):
        mode = self.meta[key]['mode']
        if mode == 'finite':
            # turn the index into a tuple so not to trigger advanced indexing
            index = tuple(index)
            self.datasets[key][index] = data[:]

    def get(self, key, index=None):
        if index is not None:
            index = tuple(index)
            data = self.datasets[key][index]
        else:
            data = self.datasets[key][:]
        return data

    def set_stim_info(self, key, value):
        # key is an iterable of group keys (str), with the last
        # string being the attribute name
        attrname = key[-1]
        fullkey = '/'.join(key[:-1])
        self.hdf5[fullkey].attrs[attrname] = value

def increment(index, dims, data_shape):
    inc_amount = data_shape

    # check dimensions of data match structure
    inc_to_match = inc_amount[1:]
    for dim_a, dim_b in zip(inc_to_match, dims[-1*(len(inc_to_match)):]):
        if dim_a != dim_b:
            raise DataIndexError()

    # now we can safely discard all but the highest dimension
    inc_index = len(index) - len(inc_amount)
    inc_amount = inc_amount[0]
    # make the index and increment amount dimensions match
    index[inc_index] += inc_amount

    # finally check that we did not run over allowed dimension
    if index[inc_index] > dims[inc_index]:
        raise DataIndexError()

    # increment dimension, if now full
    if index[inc_index] == dims[inc_index]:
        index[inc_index-1] +=1
        index[inc_index:] = [0]*len(index[inc_index:])

    return index
