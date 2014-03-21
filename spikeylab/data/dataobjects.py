import numpy as np
import h5py
import time
import json
import os

from spikeylab.tools.exceptions import DataIndexError
from spikeylab.tools.util import convert2native

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
    def __init__(self, filename, user='unknown'):
        # check that filename ends with '.hdf5', appending if necessary
        self.hdf5 = h5py.File(filename, 'w')
        self.filename = filename
        self.groups = {}
        self.datasets = {}
        self.meta = {}

        self.open_set_size = 32
        self.chunk_size = 2**24 # better to have a multiple of fs?

        self.hdf5.attrs['date'] = time.strftime('%Y-%m-%d')
        self.hdf5.attrs['who'] = user
        self.hdf5.attrs['computername'] = os.environ['COMPUTERNAME']

        self.test_count = -1
        self.needs_repack = False

    def close(self):
        for key in self.datasets.keys():
            if 'stim' in self.datasets[key].attrs.keys():
                self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'][:-1] + ']'
        for key in self.groups.keys():
            if 'stim' in self.groups[key].attrs.keys():
                self.groups[key].attrs['stim'] = self.groups[key].attrs['stim'][:-1] + ']'
        
        fname = self.hdf5.filename
        self.hdf5.close()

        if self.needs_repack:
            repack(fname)
        
    def init_group(self, key):
        """create a high level group"""
        if key == 'calibration':
            # calibration in it's own file, so the file will be the group
            self.groups[key] = self.hdf5
            self.meta[key] = {'mode': 'calibration'}
            self.set_metadata('', {'start': time.strftime('%H:%M:%S'), 
                              'mode':'calibration', 'stim': '[ '})
        else:
            self.groups[key] = self.hdf5.create_group(key)
            self.meta[key] = {'mode': 'finite'}

    def init_data(self, key, dims=None, mode='finite', nested_name=None):
        """
        Initize a new dataset

        :param key: the dataset or group name
        :type key: str
        :param dims: dimensions of dataset,
        * if mode == 'finite', this is the total size
        * if mode == 'open', this is the dimension of a single trace
        * if mode == 'continuous', this is ignored
        :type dims: tuple
        :param mode: the kind of acquisition taking place
        :type mode: str
        """
        if mode == 'calibration':
            self.datasets[nested_name] = self.groups[key].create_dataset(nested_name, dims)
            self.meta[nested_name] = {'cursor':[0]*len(dims)}
        elif mode == 'finite':
            self.test_count +=1
            setname = 'test_'+str(self.test_count)
            setpath ='/'.join([key, setname])
            if not key in self.groups:
                self.init_group(key)
            self.datasets[setname] = self.groups[key].create_dataset(setname, dims)
            self.meta[setname] = {'cursor':[0]*len(dims)}
            self.set_metadata(setpath, {'start': time.strftime('%H:%M:%S'), 
                              'mode':mode, 'stim': '[ '})
        elif mode == 'open':
            if len(dims) > 1:
                print "open acquisition only for single dimension data"
                return
            self.datasets[key] = self.hdf5.create_dataset(key, ((self.open_set_size,) + dims), maxshape=((None,) + dims))
            self.meta[key] = {'mode':mode, 'cursor':0}
            setpath = key
            self.set_metadata(setpath, {'start': time.strftime('%H:%M:%S'), 
                              'mode':mode, 'stim': '[ '})
        elif mode == 'continuous':
            self.datasets[key+'_set0'] = self.hdf5.create_dataset(key+'_set0', (self.chunk_size,))
            self.datasets[key+'_set0'].attrs['stim'] = ''
            self.meta[key] = {'mode':mode, 'set_counter':0, 'cursor':0, 'start': time.strftime('%H:%M:%S')}
        else:
            raise Exception("Unknown acquisition mode")
        

    def append(self, key, data, nested_name=None):
        """
        Inserts data sequentially to structure in repeated calls.
        """
        mode = self.meta[key]['mode']
        if mode == 'finite' or mode == 'calibration':
            if nested_name is None:
                setname = 'test_'+str(self.test_count)
            else:
                setname = nested_name
            current_location = self.meta[setname]['cursor']
            if data.shape == (1,):
                index = current_location
            else:
                index = current_location[:-len(data.shape)]
            # if data does crosses dimensions of datastructure, raise error
            # turn the index into a tuple so not to trigger advanced indexing
            self.datasets[setname][tuple(index)] = data[:]
            dims = self.datasets[setname].shape
            increment(current_location, dims, data.shape)
        elif mode =='open':
            current_index = self.meta[key]['cursor']
            self.datasets[key][current_index] = data
            current_index += 1
            if current_index == self.datasets[key].shape[0]:
                self.datasets[key].resize(current_index+self.open_set_size, axis=0)
            self.meta[key]['cursor'] = current_index
        elif mode =='continuous':
            # assumes size of data < chunk size
            setnum = self.meta[key]['set_counter']
            current_index = self.meta[key]['cursor']
            end_index = current_index + data.size
            if end_index < self.chunk_size:
                self.datasets[key+'_set'+str(setnum)][current_index:end_index] = data
            else:
                nleft = self.chunk_size - current_index
                if nleft > 0:
                # fill the rest of this data set
                    self.datasets[key+'_set'+str(setnum)][current_index:] = data[:nleft]

                print 'starting new set'
                setnum +=1
                current_index = 0
                end_index = data[nleft:].size
                self.datasets[key+'_set'+str(setnum)] = self.hdf5.create_dataset(key+'_set'+str(setnum), (self.chunk_size,))
                self.datasets[key+'_set'+str(setnum)][current_index:end_index] = data[nleft:]
                self.datasets[key+'_set'+str(setnum)].attrs['stim'] = ''

            self.meta[key]['set_counter'] = setnum
            self.meta[key]['cursor'] = end_index

    def insert(self, key, index, data):
        """
        Inserts data to index location. For 'finite' mode only. Does not affect
        appending location marker.
        """
        mode = self.meta[key]['mode']
        if mode == 'finite':
            setname = 'test_'+str(self.test_count)
            # turn the index into a tuple so not to trigger advanced indexing
            index = tuple(index)
            self.datasets[setname][index] = data[:]
        else:
            print "insert not supported for mode: ", mode

    def get(self, key, index=None):
        """
        Return data for key at specified index
        """
        if index is not None:
            index = tuple(index)
            data = self.datasets[key][index]
        else:
            data = self.datasets[key][:]
        return data

    def get_info(self, key):
        return self.hdf5[key].attrs.items()

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
        if self.meta[key]['mode'] not in ['continuous']:
            print "consolidation not supported for mode: ", self.meta[key]['mode']
            return
        setnum = self.meta[key]['set_counter']
        current_index = self.meta[key]['cursor']
        total_samples = (self.chunk_size * setnum) + current_index
        self.datasets[key] = self.hdf5.create_dataset(key, (total_samples,))
        self.datasets[key].attrs['stim'] = '[ ' # space in case empty, closing replaces the space and not the [
        self.datasets[key].attrs['start'] = self.meta[key]['start']
        self.datasets[key].attrs['mode'] = 'continuous'

        for iset in range(setnum):
            self.datasets[key][iset*self.chunk_size:(iset+1)*self.chunk_size] = self.datasets[key+'_set'+str(iset)][:]
            self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'] + self.datasets[key+'_set'+str(iset)].attrs['stim']
        
        # last set may not be complete
        if current_index != 0:
            self.datasets[key][setnum*self.chunk_size:(setnum*self.chunk_size)+current_index] = self.datasets[key+'_set'+str(setnum)][:current_index]
            self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'] + self.datasets[key+'_set'+str(setnum)].attrs['stim']

        # now go ahead and delete fractional sets.
        for iset in range(setnum+1):
            del self.datasets[key+'_set'+str(iset)]
            del self.hdf5[key+'_set'+str(iset)]

        print 'consolidated', self.hdf5.keys()
        self.needs_repack = True

    def set_metadata(self, key, attrdict):
        # key is an iterable of group keys (str), with the last
        # string being the attribute name
        if key == '':
             for attr, val in attrdict.iteritems():
                self.hdf5.attrs[attr] = val
        else:
            for attr, val in attrdict.iteritems():
                self.hdf5[key].attrs[attr] = val
        

    def append_trace_info(self, key, stim_data):
        # append data to json list?
        if not isinstance(stim_data, basestring):
            stim_data = json.dumps(convert2native(stim_data))
        mode = self.meta[key]['mode']
        if mode == 'open':
            self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'] + stim_data + ','
        if mode == 'finite':
            setname = 'test_'+str(self.test_count)
            self.datasets[setname].attrs['stim'] = self.datasets[setname].attrs['stim'] + stim_data + ','
        elif mode =='continuous':
            setnum = self.meta[key]['set_counter']
            self.datasets[key+'_set'+str(setnum)].attrs['stim'] = self.datasets[key+'_set'+str(setnum)].attrs['stim'] + stim_data + ','
        elif mode == 'calibration':
            self.groups[key].attrs['stim'] = self.groups[key].attrs['stim'] + stim_data + ','

def increment(index, dims, data_shape):
    data_shape = data_shape

    # check dimensions of data match structure
    inc_to_match = data_shape[1:]
    for dim_a, dim_b in zip(inc_to_match, dims[-1*(len(inc_to_match)):]):
        if dim_a != dim_b:
            raise DataIndexError()

    # now we can safely discard all but the highest dimension
    inc_index = len(index) - len(data_shape)
    inc_amount = data_shape[0]
    # make the index and increment amount dimensions match
    index[inc_index] += inc_amount

    # finally check that we did not run over allowed dimension
    if index[inc_index] > dims[inc_index]:
        raise DataIndexError()

    while inc_index > 0 and index[inc_index] == dims[inc_index]:
        index[inc_index-1] +=1
        index[inc_index:] = [0]*len(index[inc_index:])
        inc_index -=1
    return index

def load_calibration_file(filename, reffreq):
    print 'calibration filename', filename
    calfile = h5py.File(filename, 'r')
    cal_vector = calfile['calibration_intensities'].value
    calset = calfile['calibration_intensities']
    frequencies = calset.attrs['frequencies']
    # adjust to current ref frequency (should be zero if same as calibration)
    offset = cal_vector[frequencies == reffreq]
    print 'frequencies', frequencies
    print 'calvector', cal_vector
    print 'calfile frequency', calset.attrs['calibration_frequency'], 'current frequency', reffreq, 'offset', offset
    cal_vector -= offset
    caldb = calset.attrs['calibration_dB']
    calv = calset.attrs['calibration_voltage']
    calfile.close()
    return (cal_vector, frequencies)

def repack(h5file):
    """
    Repack archive to remove freespace.
               
    Returns
    -------
    file : h5py File or None
        If the input is a h5py.File then a h5py File instance of the
        repacked archive is returned. The input File instance will no longer
        be useable. 
    """
    f1, opened = _openfile(h5file) 
    filename1 = f1.filename
    filename2 = filename1 + '_repack_tmp'
    f2 = h5py.File(filename2, 'w')
    for key in f1.keys():
        # print 'copying', key
        f1.copy(key, f2)
    f1.close()
    f2.close()
    filename_tmp = filename1 + '_repack_rename_tmp'
    os.rename(filename1, filename_tmp)
    os.rename(filename2, filename1) 
    if opened:
        f = None  
    else:
        f = h5py.File(filename1)
    os.remove(filename_tmp)
    return f   

def _openfile(h5file):
    """
    Open an archive if input is a path.
    
    Parameters
    ----------
    h5file : str or h5py.File
        Filename or h5py.File instance of the archive.
        
    Returns
    ------- 
    f : h5py.File
        Returns a h5py.File instance.
    opened : bool
        True is `h5file` is a path; False if `h5file` is a h5py.File object.   
    
    """
    if isinstance(h5file, h5py.File):
        f = h5file
        opened = False
    elif isinstance(h5file, basestring):
        f = h5py.File(h5file)
        opened = True
    else:
        msg = "h5file must be a h5py.File object or a string (path)."
        raise TypeError, msg    
    return f, opened                 
