from __future__ import division
import numpy as np
import datetime
import h5py
from os.path import splitext
from threading import Lock

from spikeylab.io.fileio import mightysave, mightyload

class AcquisitionObject():
    # abstract class for holding data acquitision data and stimulus information
    def __init__(self, filename, f=None, db=None, v=None, method=None, mode='w'):
        print filename, mode
        self.hdf5 = h5py.File(filename, mode)   

        self.attrs = self.hdf5.attrs
        
        if mode == 'w':
            self.attrs['calhz'] = f
            self.attrs['caldb'] = db
            self.attrs['calv'] = v
            self.attrs['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.data = {}
        else:
            for x in self.hdf5.keys(): print x
            self.data = dict(self.hdf5)
        
        self.rep_temps = {}
        self.datalock = Lock()

    def close(self):
        self.hdf5.close()

    def export(self, fname, filetype=u'auto'):
        print 'export called on ', fname

        self.datalock.acquire()

        # convert everything to a dictionary to save in a single file
        master = {}
        master['data'] = {}
        master['attrs'] = dict(self.attrs)
        print('SPAM!!!!!!!!!')
        for name, dset in self.data.items():
            master['data'][name] = dset.value
            print name, master['data'][name].shape, type(master['data'][name])

        mightysave(fname, master, filetype=filetype)
        
        self.datalock.release()
        print 'EXPORTED!'

    @staticmethod
    def load_from_file(fname, filetype=u'auto'):

        root, ext = splitext(fname)
        if filetype == u'auto':
            # use the filename extenspion to determine
            # file format
            filetype = ext

        print u'FILETYPE ', filetype
        if filetype.endswith(u'hdf5'):

            acqobj = AcquisitionObject(fname, mode=u'r+')

        else:
            hdf5_filename = root + u'.hdf5'

            acqdict = mightyload(fname, filetype)

            # now intialize into a acqobject
            acqobj = AcqusitionObject(hdf5_filename)
            #convert any list objects to numpy arrays, so
            #indexing will work properly
            for att, val in acqdict['attrs'].items():
                if isinstance(val, list):
                    acqobj.attrs[att] = np.array(val)
                else:
                    acqobj.attrs[att] = val
            
            acqobj.data = {}
            data = acqdict['data']
            for dname, array in data.items():
                dset = acqobj.hdf5.create_dataset(dname, shape(array))
                dset[...] = array[:]

                acqobj.data[dname] = dset
            
        return acqobj

class CurveObject(AcquisitionObject):
    def __init__(self, filename, freqs=[], dbs=[], sr=np.nan, dur=np.nan, rft=np.nan, 
                 nreps=1, f=np.nan, db=np.nan, v=np.nan, method=None, mode=u'w'):

        AcquisitionObject.__init__(self, filename, f=f, db=db, v=v, method=method, mode=mode)
        print 'RIGHT AFTER INIT ', self.attrs.keys()
        if mode == u'w':
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
            raise Exception(u"number of dimensions, " + unicode(dims)+ u", currently not supported")

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


def shape(arraylist, s = ()):
    if isinstance(arraylist, np.ndarray):
        return arraylist.shape
    elif isinstance(arraylist, list):
        s = (len(arraylist),) + (shape(arraylist[0],s))
        return s
    else:
        return ()

