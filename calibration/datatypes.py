import numpy as np
import datetime

class AcquisitionObject():
    # abstract class for holding data acquitision data and stimulus information
    def __init__(self, sr_out, sr_in, f=None, db=None, v=None, method=None):

        self.stim = {}
        self.response = {}

        self.stim['sr'] = sr_out
        self.response['sr'] = sr_in

        # all data object should have calibration info... even if it is none
        # frequency used to calculate all other dbspl values
        self.stim['calHz'] = f

        # intensity used to calibrate
        self.stim['caldB'] = db

        # max V output at calibration frequency and intensity
        self.stim['calV'] = v

class CalibrationObject():
    def __init__(self, freqs, dbs, sr, dur, rft, nreps, f=None, db=None, v=None, method=None):
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
        self.nreps = nreps

        # metric used to calculate the dB SPL, e.g maxV, peakFFT
        self.dbmethod = None

        # note about what this data represents
        self.note = None

        # date this calibration was conducted
        self.date =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # how to store data -- predefined, or dictionary of caller specified?
        self.data = {}
        self.rep_temps = {}

        """
        # ffts of recorded tones
        self.spectrums = np.zeros((len(freqs),len(dbs),nreps,int((dur*sr)/2)))

        # calculated db from recorded tones
        self.dbspl = np.zeros((len(freqs),len(dbs)))
        """

    def init_data(self, key, dims, dim4=None):
        # dims will create a numpy array with the number of dimensions, whose size
        # is determined in the order: frequencies, intensities, reps
        frequencies = self.stim['frequencies']
        intensities = self.stim['intensities']
        if dims == 4:
            # then we are storing an array of data for each frequency, dimension 
            # and rep e.g. the actual trace

            # if the last dimension size is not provided, assume simulus length
            if dim4 == None:
                dim4 = int((self.stim['duration']*self.stim['sr'])/2)
            self.data[key] = np.zeros((len(frequencies),len(intensities),self.nreps,
                                       dim4))
        elif dims == 3:
            self.data[key] = np.zeros((len(frequencies),len(intensities),self.nreps))

        elif dims == 2:
            # if we have 2 dimensions, then assume that we need to temporarily store a thrid
            # dimension, and average results
            self.data[key] = np.zeros((len(frequencies),len(intensities)))
            self.rep_temps[key] = []
        else:
            raise Exception("number of dimensions, " + str(dims)+ ", currently not supported")
        
    def put(self, key, ix, data):
        arr = self.data[key]
        dims = arr.shape

        # frequency and intensitiy must be first two elements, 
        f, db, rep = ix

        ifreq = self.stim['frequencies'].index(f)
        idb = self.stim['intensities'].index(db)

        if len(dims) == 2:
            rep_temp = self.rep_temps[key]
            rep_temp.append(data)

            if rep == self.nreps:
                arr[ifreq][idb] = np.mean(rep_temp)
                self.data[key] = arr
                rep_temp = []

            self.rep_temps[key] = rep_temp

        elif len(dims) == 3:
            arr[ifreq][idb][rep] = data

    def get(self, key, ix):

        data = self.data[key]

        ifreq = self.stim['frequencies'].index(ix[0])
        idb = self.stim['intensities'].index(ix[1])

        if len(ix) == 2:
            item = data[ifreq][idb]
                        
        elif len(ix) == 3:
            item = data[ifreq][idb][ix[2]]

        return item
