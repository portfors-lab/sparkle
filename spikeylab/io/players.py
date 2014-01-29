import threading
import Queue
import os
import pickle
import re
import datetime
import win32com.client
from multiprocessing import Process

from spikeylab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask
from spikeylab.config.info import caldata_filename, calfreq_filename

from spikeylab.tools.qthreading import ProtocolSignals

SAVE_OUTPUT = False
PRINT_WARNINGS = False
VERBOSE = True
SAVE_NOISE = False

FFT_FNAME = u'_ffttraces'
PEAKS_FNAME =  u'_fftpeaks'
DB_FNAME = u'_resultdb'
INDEX_FNAME = u'_index'
DATA_FNAME = u'_rawdata'
NOISE_FNAME = u'_noise'
OUTPUT_FNAME = u'_outtones'


class PlayerBase():
    """Holds state information for current acquisition/generation task"""
    def __init__(self, dbv=(100,0.1)):

        self.stim = []
        self.caldb = dbv[0]
        self.calv = dbv[1]
        self.calf = None
        self.calibration_vector = None

        self.ngenerated = 0
        self.nacquired = 0

        self.aitask = None

        self.tone_lock = threading.Lock()
        self.daq_lock = threading.Lock()

        self.aitask = None
        self.aotask = None

        # establish connection to the attenuator
        try:
            pa5 = win32com.client.Dispatch("PA5.x")
            success = pa5.ConnectPA5('GB', 1)
            if success == 1:
                print 'Connection to PA5 attenuator established'
            else:
                print 'Connection to PA5 attenuator failed'
                errmsg = pa5.GetError()
                print u"Error: ", errmsg
                raise Exception(u"Attenuator connection failed")
        except:
            print "Error connecting to attenuator"
            pa5 = None

        self.attenuator = pa5

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def reset_generation(self, trigger):
        self.tone_lock.acquire()

        npts =  self.stim.size
        try:
            self.aotask = AOTaskFinite(self.aochan, self.sr, npts, trigsrc=trigger)
            self.aotask.write(self.stim)
            try:
                self.attenuator.SetAtten(self.atten)
            except:
                print "ERROR: attenuation not set!"
                # raise

            self.ngenerated +=1

            if SAVE_OUTPUT:
                self.played_tones.append(self.stim[:])
        except:
            print u'ERROR! TERMINATE!'
            self.tone_lock.release()
            raise

        self.tone_lock.release()

    def set_calibration(self, db_boost_array, frequencies):
        # use supplied array of intensity adjustment to adjust tone output
        if db_boost_array.shape != frequencies.shape:
            print u"ERROR: calibration array and frequency array must have same dimensions"
            return

        self.calibration_vector = db_boost_array
        self.calibration_frequencies = frequencies
        print self.calibration_vector
        print self.calibration_frequencies

    def set_stim(self, signal, sr, attenuation=0):
        """Sets any vector as the next stimulus to be output. Does not call write to hardware"""
        self.tone_lock.acquire()
        self.stim = signal
        self.sr = sr
        self.atten = attenuation
        # dur = float(len(signal))/sr
        # self.aitime = dur
        # timevals = np.arange(npts).astype(float)/samplerate
        self.tone_lock.release()

        # return timevals

    def get_samplerate(self):
        return self.sr

    def get_caldb(self):
        return self.caldb

    def set_aisr(self, aisr):
        self.aisr = aisr

    def set_aidur(self,dur):
        self.aitime = dur

    def set_caldb(self, caldb):
        self.caldb = caldb

    def set_calv(self, calv):
        self.calv

    def set_aochan(self, aochan):
        self.aochan = aochan

    def set_aichan(self, aichan):
        self.aichan = aichan

class FinitePlayer(PlayerBase):
    """For finite generation/acquisition tasks"""
    def __init__(self, dbv=(100,0.1)):
        PlayerBase.__init__(self, dbv)

    def start(self):
        """Write output buffer and settings to device"""

        # this shouldn't actually be possible still...
        if self.aitask is not None:
            self.stop()
            raise Exception("FIX ME : NESTED START OPERATIONS ALLOWED")

        self.daq_lock.acquire()

        self.ngenerated = 0
        self.nacquired = 0

        self.reset()

    def run(self):
        """Begin simultaneous generation/acquisition, returns read samples"""
        try:
            if self.aotask is None:
                print u"You must arm the calibration first"
                return
            # acquire data and stop task, lock must have been release by
            # previous reset
            self.daq_lock.acquire()
            self.aotask.StartTask()
            self.aitask.StartTask()

            # blocking read
            data = self.aitask.read()

            # write task should always be shorter than read
            # self.aotask.WaitUntilTaskDone(10)

            self.nacquired += 1
            
            self.aitask.stop()
            self.aotask.stop()
            
        except:
            print u'ERROR! TERMINATE!'
            self.daq_lock.release()
            self.stop()
            raise

        return data

    def reset(self):
        """Rearms the gen/acq task, to the same channels as before"""

        response_npts = int(self.aitime*self.aisr)
        try:
            self.aitask = AITaskFinite(self.aichan, self.aisr, response_npts)
            self.reset_generation(u"ai/StartTrigger")
        except:
            print u'ERROR! TERMINATE!'
            self.daq_lock.release()
            self.stop()
            raise

        self.daq_lock.release()

    def stop(self):
        try:
            self.aitask.stop()
            self.aotask.stop()
        except:     
            print u"No task running"
        self.aitask = None
        self.aotask = None


class ContinuousPlayer(PlayerBase):
    """This is a continuous player for a chart acquitision operation"""
    def __init__(self, dbv=(100,0.1)):
        PlayerBase.__init__(self, dbv)
        self.on_read = lambda x: x # placeholder

    def start_continuous(self, aichans, update_hz=10):
        """Begins a continuous analog generation, emitting an ncollected 
        signal at a rate of 10Hz"""
        self.daq_lock.acquire()

        self.ngenerated = 0 # number of stimuli presented during chart run
        npts = int(self.aisr/update_hz) #update display at 10Hz rate
        nchans = len(aichans)
        self.aitask = AITask(aichans, self.aisr, npts*5*nchans)
        self.aitask.register_callback(self._read_continuous, npts)
        self.aitask.start()

    def set_read_function(self, fun):
        self.on_read = fun

    def _read_continuous(self, task):
        inbuffer = task.read().squeeze()
        self.on_read(inbuffer)

    def run(self):
        self.aotask.StartTask()
        self.aotask.wait() # don't return until generation finished
        self.aotask.stop()
        self.aotask = None

    def start(self):
        self.reset()

    def reset(self):
        try:
            self.reset_generation(u"")
        except:
            print u'ERROR! GENERATION FAILED!'
            # self.stop()
            raise

    def stop(self):
        try:
            self.aotask.stop()
        except:     
            print u"No task running"
        self.aotask = None

    def stop_all(self):
        if self.aotask is not None:
            self.aotask.stop()
        self.aitask.stop()
        self.daq_lock.release()
        self.aitask = None
        self.aotask = None

    def generation_count(self):
        #not safe
        return self.ngenerated