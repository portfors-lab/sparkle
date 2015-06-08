import ctypes
import glob
import json
import logging
import os
import socket
import time

import h5py
import numpy as np

from sparkle.data.acqdata import AcquisitionData, increment
from sparkle.tools.exceptions import DataIndexError, DisallowedFilemodeError, \
    OverwriteFileError, ReadOnlyError
from sparkle.tools.util import convert2native, max_str_num, create_unique_path
from sparkle.tools.doc_inherit import doc_inherit

class HDF5Data(AcquisitionData):
    def __init__(self, filename, user='unknown', filemode='w-'):
        super(HDF5Data, self).__init__(filename, user, filemode)

        logger = logging.getLogger('main')
        try:
            # reload backup files, if present -- it means the program crashed
            # If the data file is corrupted it may still load, but the previously
            # gathered data could be inaccessible, so load from backup to be safe.
            backup_dir, backup_filename, prev_backups = autosave_filenames(filename)
            if len(prev_backups) > 0:
                # reassemble data from pieces
                self.hdf5 = recover_data_from_backup(filename, prev_backups)
                logger.info('Recovered data file %s' % filename)
            else:
                self.hdf5 = h5py.File(filename, filemode)
        except:
            raise

        if filemode == 'w-':
            self.hdf5.attrs['date'] = time.strftime('%Y-%m-%d')
            self.hdf5.attrs['who'] = user
            # self.hdf5.attrs['computername'] = os.environ['COMPUTERNAME']
            self.hdf5.attrs['computername'] = socket.gethostname()
            self.test_count = 0

            logger.info('Created data file %s' % filename)
        else:
            # find highet numbered test.. tight coupling to acquisition classes
            # print 'data file keys', self.hdf5.keys()
            group_prefix = 'segment_'
            dset_prefix = 'test_'
            gnum = max_str_num(group_prefix, self.hdf5.keys())
            if gnum > 0:
                self.test_count = max_str_num(dset_prefix, self.hdf5[group_prefix + str(gnum)].keys())
            else:
                self.test_count = 0

            logger.info('Opened data file %s' % filename)

        if filemode != 'r':
            # immediately make a backup, even if no data data (save attributes)
            copy_backup(self.hdf5)

    @doc_inherit
    def close(self):
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

        # now that data is closed and safe, clean up backupfile
        remove_backup(fname)

    @doc_inherit
    def init_group(self, key, mode='finite'):
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

    @doc_inherit
    def init_data(self, key, dims=None, mode='finite', nested_name=None):
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

    @doc_inherit
    def append(self, key, data, nested_name=None):
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

    @doc_inherit
    def insert(self, key, index, data):
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

    def backup(self, key):
        backup(self.hdf5, key)

    @doc_inherit
    def get_data(self, key, index=None):
        if not hasattr(self.hdf5[key], 'shape'):
            return None
        elif index is not None:
            index = tuple(index)
            data = self.hdf5[key][index]
        else:
            data = self.hdf5[key][:]
        return data

    @doc_inherit
    def get_info(self, key, inherited=False):
        if key == '':
            return dict(self.hdf5.attrs.items())
        else:
            attrs = dict(self.hdf5[key].attrs.items())
            if inherited and hasparent(key):
                attrs.update(self.get_info('/'.join(key.split('/')[:-1]), True))
                return attrs
            else:
                return attrs

    @doc_inherit
    def get_trace_stim(self, key):
        if key in self.hdf5 and 'stim' in self.hdf5[key].attrs:
            return json.loads(self.hdf5[key].attrs['stim'])
        else:
            return None

    @doc_inherit
    def get_calibration(self, key, reffreq):
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

    @doc_inherit
    def calibration_list(self):
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

    @doc_inherit
    def delete_group(self, key):
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        del self.hdf5[key]
        self.needs_repack = True

        logger = logging.getLogger('main')
        logger.info('Deleted data group %s' % key)

    @doc_inherit
    def set_metadata(self, key, attrdict, signal=False):
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

    @doc_inherit
    def append_trace_info(self, key, stim_data):
        if self.hdf5.mode == 'r':
            raise ReadOnlyError(self.filename)
        # append data to json list?
        if not isinstance(stim_data, basestring):
            stim_data = json.dumps(convert2native(stim_data))
        mode = self.meta[key]['mode']
        if mode == 'open':
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

    @doc_inherit
    def keys(self, key=None):
        if key is None or key == self.filename or key == '':
            return self.hdf5.keys()
        elif key in self.hdf5 and hasattr(self.hdf5[key], 'keys'):
            return self.hdf5[key].keys()
        else:
            return None

    @doc_inherit
    def all_datasets(self):
        self._dsets = []
        self.hdf5.visititems(self._gather_datasets)
        # sort into order alpha-numerical
        self._dsets = sorted(self._dsets, key=lambda item: (item.name.partition('_')[0], int(item.name.rpartition('_')[-1]) if item.name[-1].isdigit() else float('inf'))) 
        return self._dsets

    @doc_inherit
    def dataset_names(self):
        self._dset_names = []
        self.hdf5.visititems(self._gather_names)
        # sort into order alpha-numerical
        self._dset_names = sorted(self._dset_names, key=lambda item: (item.partition('_')[0], int(item.rpartition('_')[-1]) if item[-1].isdigit() else float('inf'))) 
        return self._dset_names

    def _gather_datasets(self, name, item):
        if hasattr(item, 'shape'):
            self._dsets.append(item)

    def _gather_names(self, name, item):
        if hasattr(item, 'shape'):
            self._dset_names.append(name)

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

def hasparent(key):
    path = key.split('/')
    if '' in path:
        path.remove('')
    return len(path) > 1

def copy_backup(h5file):
    # assemble backup file filename
    backup_dir, backup_filename, prev_backups = autosave_filenames(h5file.filename)
    logger = logging.getLogger('main')
    logger.debug('Backing up data: %s' % backup_filename)
    
    # open a new hdf5 file for backup
    backup_file = h5py.File(backup_filename, 'w')

    # copy the contents of main data file to the backup
    for group in h5file.keys():
        h5file.copy(group, backup_file)
    # copy the file attributes
    for attr in h5file.attrs:
        backup_file.attrs[attr] = h5file.attrs[attr]

    # importantly, close the file, so it is safe from corruption
    backup_file.close()
    
    logger.debug('Backup safe %s' % backup_filename)        
    #  whole file is backed up, so delete any previous backups to free up space
    for prevf in prev_backups:
        os.remove(prevf)

def autosave_filenames(data_file_name):
    parent_dir, filename = os.path.split(data_file_name)
    backup_dir = os.path.join(parent_dir, '.backup')
    nameparts = os.path.splitext(filename)
    prev_backup_files = glob.glob(os.path.join(backup_dir, nameparts[0] + '_autosave*'))
    basefname, ext = os.path.splitext(filename)
    backup_filename = create_unique_path(os.path.join(backup_dir, basefname + '_autosave'), ext)
    
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
        if os.name == 'nt':
            # mark as hidden in windows
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ret = ctypes.windll.kernel32.SetFileAttributesW(backup_dir,
                                                        FILE_ATTRIBUTE_HIDDEN)

    return backup_dir, backup_filename, prev_backup_files  

def backup(from_h5file, dataset_key):
    backup_dir, backup_filename, prevs = autosave_filenames(from_h5file.filename)
    logger = logging.getLogger('main')
    logger.debug('Backing up data: %s, data set: %s' % (backup_filename, dataset_key))
    backup_file = h5py.File(backup_filename, 'w')
    from_h5file.copy(dataset_key, backup_file, dataset_key)
    
    # copy over any group attrs
    dataset_path = dataset_key.split('/')
    current_path = ''
    for parent in dataset_path[:-1]:
        current_path += '/' + parent
        for attr in from_h5file[current_path].attrs:
            backup_file[current_path].attrs[attr] = from_h5file[current_path].attrs[attr]
    
    backup_file.close()

def remove_backup(filename):
    backup_dir, xx, backup_files = autosave_filenames(filename)

    for backup in backup_files:
        os.remove(backup)

    logger = logging.getLogger('main')
    logger.debug('Removed backup data files: %d' % len(backup_files))

    if os.path.exists(backup_dir) and not os.listdir(backup_dir):
        os.rmdir(backup_dir)

def recover_data_from_backup(filename, backup_files):
    new_data = h5py.File(filename+'tmp', 'w-')
    for backup_fname in backup_files:
        backup = h5py.File(backup_fname, 'r')
        for key in backup.keys():
            # copy with overwrite or ignore existing doesn't exist,
            # in h5py, so create our own
            copy_group(backup, new_data, key)            

        # copy file attributes too
        for attr in backup.attrs:
            new_data.attrs[attr] = backup.attrs[attr]
        backup.close()

    # close this file, so we can change the name
    new_data.close()
    # do some filename shuffling
    basefname, ext = os.path.splitext(filename)
    compromised_fname = create_unique_path(basefname + '_compromised')
    os.rename(filename, compromised_fname)
    os.rename(filename+'tmp', filename)

    new_data = h5py.File(filename, 'a')
    return new_data

def copy_group(from_file, to_file, key):
    """Recursively copy all groups/datasets/attributes from from_file[key] to
    to_file. Datasets are not overwritten, attributes are.
    """
    if not key in to_file:
        from_file.copy(key, to_file, key)
    else:
        # also make sure any additional attributes are copied
        for attr in from_file[key].attrs:
            to_file.attrs[attr] = from_file[key].attrs[attr]
            
        if hasattr(from_file[key], 'keys'):
            for subkey in from_file[key].keys():
                copy_group(from_file, to_file, '/'.join([key,subkey]))

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
