import numpy as np
import h5py
import datetime


class AcquisitionDataObject():
    def __init__(self, filename):
        self.hdf5 = h5py.File(filename, 'w')
        self.datasets = {}

    def close(self):
        self.hdf5.close()

    def init_data(self, key, dims):
        self.datasets[key] = self.hdf5.create_dataset(key, dims)

    def put(self, key, ix, data):
        self.datasets[key][ix] = data[:]

    def get(self, key, ix):
        data = self.datasets[key][ix]
        return data

    def set_meta(self, key, value):
        # key is an iterable of group keys, with the last
        # string being the attribute name
        if len(key) == 3:
            self.hdf5[key[0]][key[1]].attrs[key[2]] = value
        elif len(key) == 2:
            self.hdf5[key[0]].attrs[key[1]] = value
        elif len(key) == 1:
            self.hdf5.attrs[key[0]] = value
        else:
            raise Exception("invalid number of keys for AcquisitionDataObject metadata")
            
    def get_meta(self, key):
        pass