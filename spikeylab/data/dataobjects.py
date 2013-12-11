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
    known, but the number of traces to acquire is not
    3. Continuous acquisition, this is a 'chart' function where data is
    acquired continuously without break until the user stops the operation
    """
    def __init__(self, filename):
        # check that filename ends with '.hdf5', appending if necessary
        self.hdf5 = h5py.File(filename, 'w')
        self.datasets = {}
        self.meta = {}

        self.open_set_size = 32
        self.chunk_size = 2**16 # better to have a multiple of fs?

    def close(self):
        # consolidate fractured data sets before closing file
        self.hdf5.close()

    def init_data(self, key, dims=None, mode='finite'):
        """
        Initize a new dataset

        :param key: the dataset name
        :type key: str
        :param dims: dimensions of dataset,
        * if mode == 'finite', this is the total size
        * if mode == 'open', this is the dimension of a single trace
        * if mode == 'continuous', this is ignored
        :type dims: tuple
        :param mode: the kind of acquisition taking place
        :type mode: str
        """
        if mode == 'finite':
            self.datasets[key] = self.hdf5.create_dataset(key, dims)
            self.meta[key] = {'mode':mode, 'cursor':[0]*len(dims)}
        elif mode == 'open':
            if len(dims) > 1:
                print "open acquisition only for single dimension data"
                return
            self.datasets[key] = self.hdf5.create_dataset(key, ((self.open_set_size,) + dims), maxshape=((None,) + dims))
            self.meta[key] = {'mode':mode, 'datalen':dims[0], 'cursor':0}
        elif mode == 'continuous':
            self.datasets[key+'_set0'] = self.hdf5.create_dataset(key+'_set0', (self.chunk_size,))
            self.meta[key] = {'mode':mode, 'set_counter':0, 'cursor':0}
        else:
            raise Exception("Unknown acquisition mode")

    def append(self, key, data):
        """
        Inserts data sequentially to structure in repeated calls.
        """
        mode = self.meta[key]['mode']
        if mode == 'finite':
            current_location = self.meta[key]['cursor']
            if data.shape == (1,):
                index = current_location
            else:
                index = current_location[:-len(data.shape)]
            # if data does crosses dimensions of datastructure, raise error
            # turn the index into a tuple so not to trigger advanced indexing
            self.datasets[key][tuple(index)] = data[:]
            dims = self.datasets[key].shape
            increment(current_location, dims, data.shape)
        elif mode =='open':
            current_index = self.meta[key]['cursor']
            self.datasets[key][current_index] = data
            current_index += 1
            if current_index == self.datasets[key].shape[0]:
                self.datasets[key].resize(current_index+self.open_set_size, axis=0)
            self.meta[key]['cursor'] = current_index
        elif mode =='continuous':
            print "TODO: add continuous append"

    def insert(self, key, index, data):
        """
        Inserts data to index location. For 'finite' mode only. Does not affect
        appending location marker.
        """
        mode = self.meta[key]['mode']
        if mode == 'finite':
            # turn the index into a tuple so not to trigger advanced indexing
            index = tuple(index)
            self.datasets[key][index] = data[:]
        else:
            print "insert not supported for mode: ", mode

    def get(self, key, index=None):
        if index is not None:
            index = tuple(index)
            data = self.datasets[key][index]
        else:
            data = self.datasets[key][:]
        return data

    def trim(self, key):
        """
        Removes empty rows from dataset
        """
        current_index = self.meta[key]['cursor']
        self.datasets[key].resize(current_index, axis=0)

    def consolidate(self, key):
        """
        Collapse a 'continuous' acqusition into a single dataset.
        This must be performed before calling get function for key in these 
        modes.
        """
        if self.meta[key]['mode'] not in ['open', 'continuous']:
            print "consolidation not supported for mode: ", self.meta[key]['mode']
            return
        print 'metadata for ', key, self.meta[key]
        setnum = self.meta[key]['set_counter']
        current_index = self.meta[key]['cursor']
        data_length = self.meta[key]['datalen']
        total_traces = setnum*self.open_set_size + current_index
        self.datasets[key] = self.hdf5.create_dataset(key, 
                                (total_traces, data_length))

        for iset in range(setnum):
            self.datasets[key][iset*self.open_set_size:(iset+1)*self.open_set_size,:] = self.datasets[key+'_set'+str(iset)][:]

        # last set may not be complete
        if current_index != 0:
            self.datasets[key][setnum*self.open_set_size:(setnum*self.open_set_size)+current_index,:] = self.datasets[key+'_set'+str(setnum)][:current_index]

        # now go ahead and delete fractional sets.
        for iset in range(setnum+1):
            del self.datasets[key+'_set'+str(iset)]

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
