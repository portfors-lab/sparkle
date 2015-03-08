import numpy as np
import h5py
import time
import json
import os
import socket
import logging

from neurosound.data.acqdata import AcquisitionData, increment
from neurosound.tools.exceptions import DataIndexError, DisallowedFilemodeError, \
                                        ReadOnlyError, OverwriteFileError
from neurosound.tools.util import convert2native, max_str_num

class HDF5Data(AcquisitionData):
    def __init__(self, filename, user='unknown', filemode='w-'):
        super(HDF5Data, self).__init__(filename, user, filemode)

        self.hdf5 = h5py.File(filename, filemode)

        if filemode == 'w-':
            self.hdf5.attrs['date'] = time.strftime('%Y-%m-%d')
            self.hdf5.attrs['who'] = user
            # self.hdf5.attrs['computername'] = os.environ['COMPUTERNAME']
            self.hdf5.attrs['computername'] = socket.gethostname()
            self.test_count = 0

            logger = logging.getLogger('main')
            logger.info('Created data file %s' % filename)
        else:
            # find highets numbered test.. tight coupling to acquisition classes
            # print 'data file keys', self.hdf5.keys()
            group_prefix = 'segment_'
            dset_prefix = 'test_'
            gnum = max_str_num(group_prefix, self.hdf5.keys())
            if gnum > 0:
                self.test_count = max_str_num(dset_prefix, self.hdf5[group_prefix + str(gnum)].keys())
            else:
                self.test_count = 0

            logger = logging.getLogger('main')
            logger.info('Opened data file %s' % filename)

    def close(self):
        """Closes the datafile, only one reference to a file may be 
        open at one time.

        If there is no data in the file, it will delete itself"""
        # bad hack!
        if 'closed' in self.hdf5.__repr__().lower():
            return

        fname = self.hdf5.filename

        # if there was no data saved, just remove the file
        if len(self.hdf5.keys()) == 0:
            remove = True
        else:
            remove = False

        self.hdf5.close()

        logger = logging.getLogger('main')
        logger.debug('Closed data file %s' % fname)

        if remove:
            os.remove(fname)
        else:
            if self.needs_repack:
                _repack(fname)

    def init_group(self, key, mode='finite'):
        """Create a group hierarchy level

        :param key: The name of the group, may be nested e.g. 'topgroup/subgroub'
        :type key: str
        :param mode: The type of acquisition this group is for. Options are: 'finite', 'calibration', 'open', 'continuous'
        :type mode: str
        """
        # regular error thrown for write attempt on read only not informative enough for me
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        # self.groups[key] = self.hdf5.create_group(key)
        self.hdf5.create_group(key)
        self.meta[key] = {'mode': mode}
        if mode == 'calibration':
            self.set_metadata(key, {'start': time.strftime('%H:%M:%S'), 
                              'mode':'calibration'})

        logger = logging.getLogger('main')
        logger.info('Created data group %s' % key)

    def init_data(self, key, dims=None, mode='finite', nested_name=None):
        """
        Initializes a new dataset

        :param key: The dataset or group name. If finite, this will create a group (if none exists), and will sequentially name datasets under this group test_#
        :type key: str
        :type dims: tuple
        :param dims: 
            Dimensions of dataset:
            
            * if mode == 'finite', this is the total size
            * if mode == 'open', this is the dimension of a single trace
            * if mode == 'continuous', this is ignored
            * if mode == 'calibration', this is the total size
        :param mode: The kind of acquisition taking place
        :type mode: str
        :param nested_name: If mode is calibration, then this will be the dataset name created under the group key. Ignored for other modes.
        :type nested_name: str
        """
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        if mode == 'calibration':
            if nested_name is None:
                nested_name = 'signal'
            setname = nested_name
            setpath ='/'.join([key, setname])
            self.hdf5[key].create_dataset(setname, dims)
            self.meta[nested_name] = {'cursor':[0]*len(dims)}
            if nested_name == 'signal' or 'reference_tone':
                self.set_metadata(setpath, {'stim': '[]'})
        elif mode == 'finite':
            self.test_count +=1
            setname = 'test_'+str(self.test_count)
            setpath ='/'.join([key, setname])
            if not key in self.hdf5:
                self.init_group(key)
            self.hdf5[key].create_dataset(setname, dims)
            self.meta[setname] = {'cursor':[0]*len(dims)}
            self.set_metadata(setpath, {'start': time.strftime('%H:%M:%S'), 
                              'mode':mode, 'stim': '[]'})
        elif mode == 'open':
            if len(dims) > 1:
                print "open acquisition only for single dimension data"
                return
            setname = key
            self.hdf5.create_dataset(setname, ((self.open_set_size,) + dims), maxshape=((None,) + dims))
            self.meta[key] = {'mode':mode, 'cursor':0}
            setpath = key
            self.set_metadata(setpath, {'start': time.strftime('%H:%M:%S'), 
                              'mode':mode, 'stim': '[]'})
        elif mode == 'continuous':
            self.datasets[key+'_set1'] = self.hdf5.create_dataset(key+'_set1', (self.chunk_size,))
            self.datasets[key+'_set1'].attrs['stim'] = ''
            self.meta[key] = {'mode':mode, 'set_counter':1, 'cursor':0, 'start': time.strftime('%H:%M:%S')}
            # create a dataset for the key itself, so to allow setting attributes, 
            # that will get copied after consolidation
            setname = key
            self.hdf5.create_dataset(key, (1,))
        else:
            raise Exception("Unknown acquisition mode")
        
        logger = logging.getLogger('main')
        logger.info('Created data set %s' % setname)

    def append(self, key, data, nested_name=None):
        """
        Inserts data sequentially to structure in repeated calls. 
        Depending on how the dataset was initialized:

        * If mode == 'finite': If *nested_name* is ``None``, data is appended to the current automatically incremented *test_#* dataset under the given group. Otherwise data is appended to the group *key*, dataset *nested_name*.
        * If mode == 'calibration': Must provide a *nested_name* for a dataset to append data to under group *key*
        * If mode == 'open': Appends chunk to dataset *key*
        * If mode == 'continuous': Appends to dataset *key* forever

        For 'Finite' and 'calibration' modes, an attempt to append past the 
        initialized dataset size will result in an error

        :param key: name of the dataset/group to append to
        :type key: str
        :param data: data to add to file
        :type data: numpy.ndarray
        :param nested_name: If mode is 'calibration' or 'finite', then this will be the dataset name created under the group key. Ignored for other modes.
        :type nested_name: str
        """
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        # make sure data is numpy array
        data = np.array(data)
        mode = self.meta[key]['mode']
        if mode == 'finite' or mode == 'calibration':
            if nested_name is None and mode == 'finite':
                setname = 'test_'+str(self.test_count)
            elif nested_name is not None:
                setname = nested_name
            else:
                setname = 'signal'
            current_location = self.meta[setname]['cursor']
            if data.shape == (1,):
                index = current_location
            else:
                index = current_location[:-len(data.shape)]
            # if data does crosses dimensions of datastructure, raise error
            # turn the index into a tuple so not to trigger advanced indexing
            self.hdf5[key][setname][tuple(index)] = data[:]
            dims = self.hdf5[key][setname].shape
            increment(current_location, dims, data.shape)
        elif mode =='open':
            current_index = self.meta[key]['cursor']
            self.hdf5[key][current_index] = data
            current_index += 1
            if current_index == self.hdf5[key].shape[0]:
                self.hdf5[key].resize(current_index+self.open_set_size, axis=0)
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
        Inserts data to index location. For 'finite' mode only. Does not 
        affect appending location marker. Will Overwrite existing data.

        :param key: Group name to insert to
        :type key: str
        :param index: location that the data should be inserted
        :type index: tuple
        :param data: data to add to file
        :type data: numpy.ndarray
        """
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        mode = self.meta[key]['mode']
        if mode == 'finite':
            setname = 'test_'+str(self.test_count)
            # turn the index into a tuple so not to trigger advanced indexing
            index = tuple(index)
            self.hdf5[key][setname][index] = data[:]
        else:
            print "insert not supported for mode: ", mode

    def get(self, key, index=None):
        """
        Returns data for key at specified index

        :param key: name of the dataset to retrieve, may be nested
        :type key: str
        :param index: slice of of the data to retrieve, ``None`` gets whole data set. Numpy style indexing.
        :type index: tuple
        """
        if not hasattr(self.hdf5[key], 'shape'):
            return None
        elif index is not None:
            index = tuple(index)
            data = self.hdf5[key][index]
        else:
            data = self.hdf5[key][:]
        return data

    def get_info(self, key):
        """Retrieves all saved attributes for the group or dataset

        :param key: The name of group or dataset to get info for
        :type key: str
        """
        if key == '':
            return dict(self.hdf5.attrs.items())
        else:
            return dict(self.hdf5[key].attrs.items())

    def get_trace_info(self, key):
        """Retrives the stimulus info saved to the given dataset. Works for finite dataset keys only

        :param key: The name of dataset to get stimulus info for
        :type key: str
        """
        if key in self.hdf5 and 'stim' in self.hdf5[key].attrs:
            return json.loads(self.hdf5[key].attrs['stim'])
        else:
            return None

    def get_calibration(self, key, reffreq):
        """Gets a saved calibration, in attenuation from a refernece frequency point

        :param key: The name of the calibration to retrieve
        :type key: str
        :param reffreq: The frequency for which to set as zero, all other frequencies will then be in attenuation difference from this frequency
        :type reffreq: int
        :returns: (numpy.ndarray, numpy.ndarray) -- frequencies of the attenuation vector, attenuation values
        """
        cal_vector = self.hdf5[key]['calibration_intensities'].value
        stim_info = json.loads(self.hdf5[key+'/signal'].attrs['stim'])
        fs = stim_info[0]['samplerate_da']
        npts = len(cal_vector)
        frequencies = np.arange(npts)/(float((npts-1)*2)/fs)
        if reffreq in frequencies:
            offset = cal_vector[frequencies == reffreq]
        else:
            offset = np.interp(reffreq, frequencies, cal_vector)
        # print 'offset', offset, reffreq
        cal_vector -= offset

        return (cal_vector, frequencies)

    def calibration_list(self):
        """Lists the calibrations present in this file

        :returns: list<str> -- the keys for the calibration groups
        """
        cal_names = []
        for grpky in self.hdf5.keys():
            if 'calibration' in grpky:
                cal_names.append(grpky)
        return cal_names

    def trim(self, key):
        """
        Removes empty rows from dataset... I am still wanting to use this???

        :param key: the dataset to trim
        :type key: str
        """
        current_index = self.meta[key]['cursor']
        self.hdf5[key].resize(current_index, axis=0)

    def consolidate(self, key):
        """
        Collapses a 'continuous' acquisition into a single dataset.
        This must be performed before calling *get* function for *key* in these 
        modes.

        :param key: name of the dataset to consolidate.
        :type key: str
        """
        if self.meta[key]['mode'] not in ['continuous']:
            print "consolidation not supported for mode: ", self.meta[key]['mode']
            return

        # get a copy of the attributes saved, then delete placeholder
        attr_tmp = self.hdf5[key].attrs.items()
        del self.hdf5[key]

        setnum = self.meta[key]['set_counter']
        setnum -= 1 # convert from 1-indexed to 0-indexed
        current_index = self.meta[key]['cursor']
        total_samples = (self.chunk_size * setnum) + current_index
        self.datasets[key] = self.hdf5.create_dataset(key, (total_samples,))
        self.datasets[key].attrs['stim'] = '[ ' # space in case empty, closing replaces the space and not the [
        self.datasets[key].attrs['start'] = self.meta[key]['start']
        self.datasets[key].attrs['mode'] = 'continuous'

        for iset in range(0, setnum):
            self.datasets[key][iset*self.chunk_size:(iset+1)*self.chunk_size] = self.datasets[key+'_set'+str(iset+1)][:]
            self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'] + self.datasets[key+'_set'+str(iset+1)].attrs['stim']
        
        # last set may not be complete
        if current_index != 0:
            self.datasets[key][setnum*self.chunk_size:(setnum*self.chunk_size)+current_index] = self.datasets[key+'_set'+str(setnum+1)][:current_index]
            self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'] + self.datasets[key+'_set'+str(setnum+1)].attrs['stim']

        # make sure we have a closing bracket
        if self.datasets[key].attrs['stim'][-1] != ']':
            self.datasets[key].attrs['stim'] = self.datasets[key].attrs['stim'] + ']'
        
        # copy back attributes from placeholder
        for k, v in attr_tmp:
            self.datasets[key].attrs[k] = v

        # now go ahead and delete fractional sets.
        for iset in range(setnum+1):
            del self.datasets[key+'_set'+str(iset+1)]
            del self.hdf5[key+'_set'+str(iset+1)]

        print 'consolidated', self.hdf5.keys()
        print 'stim attr', self.datasets[key].attrs['stim']
        print
        self.needs_repack = True

    def delete_group(self, key):
        """Removes the group from the file, deleting all data under it

        :param key: Name of group to remove
        :type key: str
        """
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        del self.hdf5[key]
        self.needs_repack = True

        logger = logging.getLogger('main')
        logger.info('Deleted data group %s' % key)

    def set_metadata(self, key, attrdict, signal=False):
        """Sets attributes for a dataset or group

        :param key: name of group or dataset
        :type key: str
        :param attrdict: A collection of name:value pairs to save as metadata
        :type attrdict: dict
        """
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        # key is an iterable of group keys (str), with the last
        # string being the attribute name
        if key == '':
             for attr, val in attrdict.iteritems():
                self.hdf5.attrs[attr] = val
        else:
            for attr, val in attrdict.iteritems():
                if val is None:
                    val = '' # can't save None attribute value to HDF5
                if signal:
                    mode = self.meta[key]['mode']
                    if mode == 'finite':
                        setname = key + '/' + 'test_'+str(self.test_count)
                    elif mode == 'calibration':
                        setname = key + '/signal'
                    self.hdf5[setname].attrs[attr] = val
                else:
                    self.hdf5[key].attrs[attr] = val
 
    def append_trace_info(self, key, stim_data):
        """Sets the stimulus documentation for the given dataset/groupname. If key is for a finite group, sets for current test

        :param key: Group or dataset name
        :type key: str
        :param stim_data: JSON formatted data to append to a list
        :type stim_data: str
        """
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        # append data to json list?
        if not isinstance(stim_data, basestring):
            stim_data = json.dumps(convert2native(stim_data))
        mode = self.meta[key]['mode']
        if mode == 'open':
            print 'appending stim in open'
            _append_stim(self.hdf5, key, stim_data)
        if mode == 'finite':
            setname = key + '/' + 'test_'+str(self.test_count)
            _append_stim(self.hdf5, setname, stim_data)
        elif mode =='continuous':
            setnum = self.meta[key]['set_counter']
            setname = key+'_set'+str(setnum)
            _append_stim(self.hdf5, setname, stim_data)
        elif mode == 'calibration':
            if 'Pure Tone' in stim_data:
                setname =  key + '/' + 'reference_tone'
            else:
                setname = key + '/' + 'signal'
            _append_stim(self.hdf5, setname, stim_data)

    def keys(self, key=None):
        """The high-level keys for this file

        :returns: list<str> -- list of the keys
        """
        if key is None or key == self.filename or key == '':
            return self.hdf5.keys()
        elif key in self.hdf5 and hasattr(self.hdf5[key], 'keys'):
            return self.hdf5[key].keys()
        else:
            return None

    def all_datasets(self):
        """Go through file and get all datasets"""
        self._dsets = []
        self.hdf5.visititems(self._gather_datasets)
        # sort into order alpha-numerical
        self._dsets = sorted(self._dsets, key=lambda item: (item.name.partition('_')[0], int(item.name.rpartition('_')[-1]) if item.name[-1].isdigit() else float('inf'))) 
        return self._dsets

    def _gather_datasets(self, name, item):
        if hasattr(item, 'shape'):
            self._dsets.append(item)

    def _repr_html_(self):
        # display the contents of this file in HTML for viewing in ipython notebooks
        self._printstr = '<p>'
        self.hdf5.visititems(self._report_item)
        self._printstr += '</p>'
        return self._printstr

    def _report_item(self, name, item):
        self._printstr += name
        if hasattr(item, 'shape'):
            self._printstr += ' ' + str(item.shape)
        self._printstr += '<br>'


def _append_stim(container, key, stim_data):
    if container[key].attrs['stim'] == '[]':
         # first addition
        existing_stim = '['
    elif container[key].attrs['stim'] == '':
        existing_stim = ''
    else:
        # removing closing bracket and add comma
        existing_stim = container[key].attrs['stim'][:-1] + ','
    container[key].attrs['stim'] = existing_stim + stim_data + ']'


def _repack(h5file):
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
