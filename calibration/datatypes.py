import numpy as np
import datetime

class CalibrationObject():
    def __init__(self, freqs, dbs, sr, dur, rft, nreps, f=None, db=None, v=None, method=None):
        #intialize all the required fields to None

        # list of frequencies played -- dim 0 in spectrum and dbspl
        self.frequencies = freqs

        # intensity played -- dim1 in spectrum and dbspl
        self.intensites = dbs

        # frequency used to calculate all other dbspl values
        self.calf = f

        # intensity used to calibrate
        self.caldb = db

        # max V output at calibration frequency and intensity
        self.calv = v

        # sample rate of tone played and recorded (must be the same)
        self.samplerate = sr

        # duration of tone (ms)
        self.duration = dur

        # rise fall time of tone (ms)
        self.risefalltime = rft

        # metric used to calculate the dB SPL, e.g maxV, peakFFT
        self.dbmethod = None

        # note about what this data represents
        self.note = None

        # date this calibration was conducted
        self.date =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # ffts of recorded tones
        self.spectrums = np.zeros((len(freqs),len(dbs),nreps,int((dur*sr)/2)))

        # calculated db from recorded tones
        self.dbspl = np.zeros((len(freqs),len(dbs)))

