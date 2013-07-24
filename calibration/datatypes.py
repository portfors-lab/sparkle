import numpy as np
import datetime
import h5py
from os.path import splitext
from threading import Lock

from audiolab.io.fileio import mightysave, mightyload

class AcquisitionObjectx():
    # abstract class for holding data acquitision data and stimulus information
    def __init__(self, sr_out, sr_in, f=None, db=None, v=None, method=None):

        self.stim = {}
        self.response = {}
        self.misc = {}

        self.stim['sr'] = sr_out
        self.response['sr'] = sr_in

        # all data object should have calibration info... even if it is none
        # frequency used to calculate all other dbspl values
        self.stim['calHz'] = f

        # intensity used to calibrate
        self.stim['caldB'] = db

        # max V output at calibration frequency and intensity
        self.stim['calV'] = v

        # date this calibration was conducted
        self.stim['date'] =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # how to store data -- predefined, or dictionary of caller specified?
        self.data = {}
        self.rep_temps = {}
        self.datalock = Lock()

class CalibrationObjectx():
    def __init__(self, freqs=None, dbs=None, sr=None, dur=None, rft=None, nreps=None, f=np.nan, db=np.nan, v=np.nan, method=None):
        #intialize all the required fields to None

        AcquisitionObject.__init__(self, sr, sr, f=f, db=db, v=v, method=method)

        # list of frequencies played -- dim 0 in spectrum and dbspl
        self.stim['frequencies'] = freqs
        #self.frequencies = freqs

        # intensity played -- dim1 in spectrum and dbspl
        self.stim['intensities'] = dbs
        #self.intensities = dbs

        # duration of tone (ms)
        self.stim['duration'] = dur

        # rise fall time of tone (ms)
        self.stim['risefalltime'] = rft

        # number of stimulus repetitions
        self.stim['repetitions'] = nreps

        # metric used to calculate the dB SPL, e.g maxV, peakFFT
        self.misc['dbmethod'] = ''

        # note about what this data represents
        self.misc['note'] = ''


    def init_data(self, key, dims, dim4=None):
        # dims will create a numpy array with the number of dimensions, whose size
        # is determined in the order: frequencies, intensities, reps
        frequencies = self.stim['frequencies']
        intensities = self.stim['intensities']
        nreps = self.stim['repetitions']
        if dims == 4:
            # then we are storing an array of data for each frequency, dimension 
            # and rep e.g. the actual trace

            # if the last dimension size is not provided, assume simulus length
            if dim4 == None:
                dim4 = int((self.stim['duration']*self.stim['sr'])/2)
            self.data[key] = np.zeros((len(frequencies),len(intensities),nreps,
                                       dim4))
        elif dims == 3:
            self.data[key] = np.zeros((len(frequencies),len(intensities),nreps))

        elif dims == 2:
            # if we have 2 dimensions, then assume that we need to temporarily store a third
            # dimension, and average results
            self.data[key] = np.zeros((len(frequencies),len(intensities)))
            self.rep_temps[key] = []
        else:
            raise Exception("number of dimensions, " + str(dims)+ ", currently not supported")


    def put(self, key, ix, data):
        arr = self.data[key]
        dims = arr.shape

        # frequency and intensitiy must be first two elements
        f, db, rep = ix

        ifreq = self.stim['frequencies'].index(f)
        idb = self.stim['intensities'].index(db)

        self.datalock.acquire()

        if len(dims) == 2:
            rep_temp = self.rep_temps[key]
            rep_temp.append(data)

            if rep == (self.stim['repetitions']-1):
                arr[ifreq][idb] = np.mean(rep_temp)
                self.data[key] = arr
                rep_temp = []

            self.rep_temps[key] = rep_temp

        elif len(dims) == 4:
            arr[ifreq][idb][rep] = data
            self.data[key] = arr

        self.datalock.release()


    def get(self, key, ix):

        data = self.data[key]

        ifreq = self.stim['frequencies'].index(ix[0])
        idb = self.stim['intensities'].index(ix[1])

        self.datalock.acquire()

        if len(ix) == 2:
            item = data[ifreq][idb]
                        
        elif len(ix) == 3:
            item = data[ifreq][idb][ix[2]]

        self.datalock.release()

        return item


    def save_to_file(self, fname, filetype='auto'):
        
        if filetype == 'auto':
            # use the filename extension to determine
            # file format
            root, filetype = splitext(fname)
            
        filetype = filetype.replace('.', '')

        self.datalock.acquire()

        if filetype == 'hdf5':
            if not fname.endswith('hdf5'):
                fname = fname + '.hdf5'

            f = h5py.File(fname, "w")
            dgrp = f.create_group("data")
            for dname, data in self.data.items():
                
                dset = dgrp.create_dataset(dname, data.shape)
                dset[...] = data[:]
                
            for att, val in self.stim.items():
                f.attrs[att] = val

            f.close()

        else:

            # convert everything to a dictionary to save in a single file
            master = {}
            master['stim'] = self.stim
            master['response'] = self.response
            master['data'] = self.data
            master['misc'] = self.misc
            
            mightysave(fname, master, filetype=filetype)
        
        self.datalock.release()


    @staticmethod
    def load_from_file(fname, filetype='auto'):

        root, ext = splitext(fname)
        if filetype == 'auto':
            # use the filename extenspion to determine
            # file format
            filetype = ext

        print('FILETYPE ', filetype)
        if filetype.endswith('hdf5'):
           
            with h5py.File(fname, 'r') as hf:
                calobj = CalibrationObject()
                for attr, val in hf.attrs.items():
                    
                    if isinstance(val, np.ndarray):
                        calobj.stim[attr] = list(val)
                    else:
                        calobj.stim[attr] = val

                for dname, dset in hf['data'].items():
                    
                    data = np.zeros(dset.shape)
                    data[...] = dset[:]
                    calobj.data[dname] = data
        else:

            caldict = mightyload(fname, filetype)

            # now intialize into a calObject
            calobj = CalibrationObject()
            calobj.stim = caldict['stim']
            calobj.reponse = caldict['response']
            data = caldict['data']
            calobj.data = data


            if filetype == 'auto':
                root, ext = splitext(fname)
                # use the filename extension to determine
                # file format
                filetype = ext

            if filetype in ['json, pkl']:
                for key, arr in data.items():
                    arr = np.array(arr)
                    data[key] = arr
                    if len(arr.shape) == 2:
                        calobj.rep_temps[key] = []

            else:
                calobj.stim['frequencies'] = list(calobj.stim['frequencies'])
                calobj.stim['intensities'] = list(calobj.stim['intensities'])
            
        return calobj

class AcquisitionObject():
    # abstract class for holding data acquitision data and stimulus information
    def __init__(self, filename, f=None, db=None, v=None, method=None, mode='w'):
        print(filename, mode)
        self.hdf5 = h5py.File(filename, mode)   

        self.attrs = self.hdf5.attrs

        if mode == 'w':
            self.attrs['calhz'] = f
            self.attrs['caldb'] = db
            self.attrs['calv'] = v
            self.attrs['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.data = {}
        else:
            for x in self.hdf5.keys(): print(x)
            self.data = dict(self.hdf5)
        
        self.rep_temps = {}
        self.datalock = Lock()

class CalibrationObject():
    def __init__(self, filename, freqs=None, dbs=None, sr=None, dur=None, rft=None, nreps=1, f=np.nan, db=np.nan, v=np.nan, method=None, mode='w'):

        AcquisitionObject.__init__(self, filename, f=f, db=db, v=v, method=method, mode=mode)
        
        if mode == 'w':
            self.attrs['sr'] = sr

            # duration of tone (ms)
            self.attrs['duration'] = dur

            # list of frequencies played -- dim 0 in spectrum and dbspl
            self.attrs['frequencies'] = freqs

            # intensity played -- dim1 in spectrum and dbspl
            self.attrs['intensities'] = dbs
            
            # rise fall time of tone (ms)
            self.attrs['risefalltime'] = rft

            # number of stimulus repetitions
            self.attrs['repetitions'] = nreps


    def init_data(self, key, dims, dim4=None):

        frequencies = self.attrs['frequencies']
        intensities = self.attrs['intensities']
        nreps = self.attrs['repetitions']

        if dims == 4:
            # then we are storing an array of data for each frequency, dimension 
            # and rep e.g. the actual trace

            # if the last dimension size is not provided, assume simulus length
            if dim4 == None:
                dim4 = int((self.attrs['duration']*self.attrs['sr'])/2)
            self.data[key] = self.hdf5.create_dataset(key, (len(frequencies),len(intensities),nreps,
                                       dim4))

        elif dims == 3:
            self.data[key] = self.hdf5.create_dataset(key, (len(frequencies),len(intensities),nreps))

        elif dims == 2:
            # if we have 2 dimensions, then assume that we need to temporarily store a third
            # dimension, and average results
            self.data[key] = self.hdf5.create_dataset(key, (len(frequencies),len(intensities)))
            self.rep_temps[key] = []
        else:
            raise Exception("number of dimensions, " + str(dims)+ ", currently not supported")

    def put(self, key, ix, data):
        dims = self.data[key].shape

        # frequency and intensitiy must be first two elements
        f, db, rep = ix

        ifreq = np.where(self.attrs['frequencies'] == f)[0][0]
        idb = np.where(self.attrs['intensities'] == db)[0][0]

        self.datalock.acquire()

        if len(dims) == 2:
            rep_temp = self.rep_temps[key]
            rep_temp.append(data)

            if rep == (self.attrs['repetitions']-1):
                self.data[key][ifreq,idb] = np.mean(rep_temp)
                rep_temp = []

            self.rep_temps[key] = rep_temp

        elif len(dims) == 4:
            self.data[key][ifreq,idb,rep] = data[:]

        self.datalock.release()


    def get(self, key, ix):

        data = self.data[key]

        ifreq = np.where(self.attrs['frequencies'] == ix[0])[0][0]
        idb = np.where(self.attrs['intensities'] == ix[1])[0][0]
        
        self.datalock.acquire()

        if len(ix) == 2:
            item = data[ifreq, idb]
                        
        elif len(ix) == 3:
            item = data[ifreq, idb, ix[2]]

        self.datalock.release()

        return item


    def save_to_file(self, fname, filetype='auto'):

        if filetype == 'auto':
            # use the filename extension to determine
            # file format
            root, filetype = splitext(fname)
            
        filetype = filetype.replace('.', '')

        self.datalock.acquire()

        print('filetype', filetype)
        if filetype == 'hdf5':
            #do nothing, it's already saved
            self.hdf5.close()
            
        else:

            # convert everything to a dictionary to save in a single file
            master = {}
            master['data'] = {}
            master['attrs'] = dict(self.attrs)
            for name, dset in self.data.items():
                master['data'][name] = dset.value

                mightysave(fname, master, filetype=filetype)
        
        self.datalock.release()


    @staticmethod
    def load_from_file(fname, filetype='auto'):

        root, ext = splitext(fname)
        if filetype == 'auto':
            # use the filename extenspion to determine
            # file format
            filetype = ext

        print('FILETYPE ', filetype)
        if filetype.endswith('hdf5'):

            calobj = CalibrationObject(fname, mode='r+')

        else:

            caldict = mightyload(fname, filetype)

            # now intialize into a calObject
            calobj = CalibrationObject()
            calobj.attrs = caldict['attrs']
            
            calobj.data = {}
            data = caldict['data']
            for key, array in data.items():
                dset = calobj.hdf5.create_dataset(dname, data.shape)
                dset[...] = data[:]

                calobj.data[key] = dset
            
        return calobj
