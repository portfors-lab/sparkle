import threading
import Queue
import os
import pickle
import re
import win32com.client
from multiprocessing import Process
from audiolab.data.datatypes import CurveObject

from audiolab.io.fileio import mightysave
from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite
from audiolab.tools.audiotools import *
from audiolab.config.info import caldata_filename, calfreq_filename


SAVE_OUTPUT = False
PRINT_WARNINGS = False
SAVE_FFT_DATA = True
VERBOSE = True
SAVE_DATA_TRACES = False
SAVE_NOISE = False

FFT_FNAME = u'_ffttraces'
PEAKS_FNAME =  u'_fftpeaks'
DB_FNAME = u'_resultdb'
INDEX_FNAME = u'_index'
DATA_FNAME = u'_rawdata'
NOISE_FNAME = u'_noise'
OUTPUT_FNAME = u'_outtones'


class PlayerBase():
    def __init__(self, dbv=(100,0.1)):

        self.tone = []
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

    def set_calibration(self, db_boost_array, frequencies):
        # use supplied array of intensity adjustment to adjust tone output
        if db_boost_array.shape != frequencies.shape:
            print u"ERROR: calibration array and frequency array must have same dimensions"
            return

        self.calibration_vector = db_boost_array
        self.calibration_frequencies = frequencies
        print self.calibration_vector
        print self.calibration_frequencies

    def set_tone(self,f,db,dur,rft,sr):

        if self.calibration_vector is not None:
            adjdb = self.caldb - self.calibration_vector[self.calibration_frequencies == f][0]
        else:
            adjdb = 0

        tone, timevals, atten = make_tone(f,db,dur,rft,sr, self.caldb, self.calv, adjustdb=adjdb)

        if PRINT_WARNINGS:
            if np.amax(abs(tone)) < 0.005:
                print u"WARNING : ENTIRE OUTPUT TONE VOLTAGE LESS THAN DEVICE MINIMUM"

        self.tone_lock.acquire()
        self.tone = tone
        self.sr = sr
        self.aitime = dur
        self.atten = atten
        self.tone_lock.release()

        return tone, timevals

    def get_samplerate(self):
        return self.sr

    def get_caldb(self):
        return self.caldb

    def set_aisr(self, aisr):
        self.aisr = aisr

    def set_caldb(self, caldb):
        self.caldb = caldb

    def set_calv(self, calv):
        self.calv

class TonePlayer(PlayerBase):
    def __init__(self, dbv=(100,0.1)):
        PlayerBase.__init__(self, dbv)

    def start(self, aochan, aichan):

        # this shouldn't actually be possible still...
        if self.aitask is not None:
            self.stop()
            print u"FIX ME : NESTED START OPERATIONS ALLOWED"

        self.daq_lock.acquire()

        self.ngenerated = 0
        self.nacquired = 0
       
        response_npts = int(self.aitime*self.aisr)
        npts = self.tone.size
        try:
            self.aitask = AITaskFinite(aichan, self.aisr, response_npts)
            self.aotask = AOTaskFinite(aochan, self.sr, npts, trigsrc=u"ai/StartTrigger")
            self.aotask.write(self.tone)

            if SAVE_OUTPUT:
                self.played_tones = [self.tone[:]]

        except:
            print u'ERROR! TERMINATE!'
            self.stop()
            raise

        # save for later -- allow not to be changed?
        self.aochan = aochan
        self.aichan = aichan

        self.daq_lock.release()

    def read(self):
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
       
        self.tone_lock.acquire()

        npts =  self.tone.size
        response_npts = int(self.aitime*self.aisr)

        try:
            self.aitask = AITaskFinite(self.aichan, self.aisr, response_npts)
            self.aotask = AOTaskFinite(self.aochan, self.sr, npts, trigsrc=u"ai/StartTrigger")
            self.aotask.write(self.tone)
            try:
                self.attenuator.SetAtten(self.atten)
            except:
                print "ERROR: attenuation not set!"

            self.ngenerated +=1

            if SAVE_OUTPUT:
                self.played_tones.append(self.tone[:])
        except:
            print u'ERROR! TERMINATE!'
            self.daq_lock.release()
            self.tone_lock.release()
            self.stop
            raise

        self.daq_lock.release()
        self.tone_lock.release()

    def stop(self):
        try:
            self.aitask.stop()
            self.aotask.stop()
        except:     
            print u"No task running"
        self.aitask = None
        self.aotask = None
    

class ToneCurve():
    def __init__(self, duration_s, samplerate, risefall_s, nreps, freqs, 
                 intensities, dbv=(100,0.1), calf=None, filename=u'temp.hdf5',
                 samplerate_acq=None, duration_acq_s=None, mode='calibration'):
        u"""
        Set up a tone curve which loops through frequencies (outer) and intensities (inner)
        """

        self.data_lock = threading.Lock()

        self.ngenerated = 0
        self.nacquired = 0

        if mode == 'calibration':
            self.response_data = CurveObject(filename, freqs, intensities, 
                                   samplerate, duration_s, 
                                   risefall_s, nreps,v=dbv[1])
        else:
            self.reponse_data = AquisitionDataObject(filename)
        self.dur = duration_s
        self.sr = samplerate
        self.rft = risefall_s
        self.nreps = nreps
        self.calf = calf
        if samplerate_acq == None:
            self.aisr = samplerate
        else:
            self.aisr = samplerate_acq
        if duration_acq_s == None:
            self.aidur = duration_s
        else:
            self.aidur = duration_acq_s

        self.aitimes = np.linspace(0, self.aidur, self.aidur*self.aisr)

        self.response_data.init_data(u'peaks', 2)
        self.response_data.init_data(u'vmax', 2)

        if SAVE_FFT_DATA:
            # 4D array nfrequencies x nintensities x nreps x npoints
            #self.full_fft_data = np.zeros((len(freqs),len(intensities),nreps,int((duration_s*samplerate)/2)))
            self.response_data.init_data(u'spectrums',4)

        if SAVE_DATA_TRACES:
            #self.data_traces = np.zeros((len(freqs),len(intensities),nreps,int(duration_s*samplerate)))
            self.response_data.init_data(u'raw_traces',4)
        
        self.reject_list = []

        self.work_queue = Queue.Queue()
        for ifreq, f in enumerate(freqs):
            for idb, db in enumerate(intensities):
                for irep in xrange(nreps):
                    self.work_queue.put((f,db,irep))
    
        #self.freqs = [x for x in freqs]
        #self.intensities = [x for x in intensities]

        self.player = TonePlayer(dbv)
        self.player.set_aisr(self.aisr)
        self.signal = None

    def assign_signal(self, signal):
        u"""
        Accepts a PyQt signal, which it will emit the parameters 
        (f, db, data, spectrum, freq) after each read operation
        """
        # allow this object to signal to GUI data to update
        self.signal = signal

    def arm(self, aochan, aichan):
        u"""
        Prepare the tone curve to play. This must be done before the first read
        """
        try:
            # load first item in queue
            f, db, rep = self.work_queue.get()

            tone, t = self.player.set_tone(f, db, self.dur, self.rft, self.sr)

            self.player.start(aochan, aichan)
            self.current_fdb = (f, db, rep)
            self.current_tone = (tone, t)
            success = 1
        except:
            success = 0
        return success

    def next(self):
        u"""
        Simultaneously present and read the next prepped stimulus, and reload.

        Internally stores acquired data. 
        Returns played_tone, data, times, played_f, played_db
        """

        print u'reading'
        data = self.player.read()
        print u'read'

        # save data here
        played_f, played_db, r = self.current_fdb

        # spin off thread for saving data, and move on to reset tone
        t = threading.Thread(target=self._storedata, 
                             args=(data[:], self.current_fdb))
        #t = Process(target=self._storesimple, args=(data, self.current_fdb))
        #t.daemon = True
        t.start()
        #self._storedata(data, self.current_fdb)

        # t will not change in tuning curve
        played_tone = self.current_tone

        # also includes times in response data
        data = (data, self.aitimes)

        # reset so ready to go for next time
        if self.haswork():
            f, db, rep = self.work_queue.get()

            sr = self.sr
            dur = self.dur
            rft = self.rft

            new_tone, t = self.player.set_tone(f,db,dur,rft,sr)
            self.player.reset()

            # keep track of current playing ... we want to return
            # this data the next time this function is called
            self.current_fdb = (f, db, rep)
            self.current_tone = (new_tone, t)
        
        return played_tone, data, played_f, played_db

    def haswork(self):
        return not self.work_queue.empty()


    def set_calibration(self, db_boost_array, frequencies):
        self.player.set_calibration(db_boost_array, frequencies)


    def stop(self):
        self.player.stop()
        #self.response_data.close()


    def _storedata(self, data, fdb):
        sr = self.player.get_samplerate()
        f, db, rep = fdb

        # extract information from acquired tone, and save
        freq, spectrum = calc_spectrum(data, sr)

        # take the abs (should I do this?), and get the highest peak
        spectrum = abs(spectrum)

        spec_max, max_freq = get_fft_peak(spectrum, freq)
        spec_peak_at_f = spectrum[freq == f]

        vmax = np.amax(abs(data))

        if self.signal is not None:
            self.signal.emit(f, db, data, spectrum, freq)

        if vmax < 0.005:
            if PRINT_WARNINGS:
                print u"WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR"

        #tolerance of 1 Hz for frequency matching
        if max_freq < f-1 or max_freq > f+1:
            if PRINT_WARNINGS:
                print u"WARNING : MAX SPECTRAL FREQUENCY DOES NOT MATCH STIMULUS"
                print u"\tTarget : {}, Received : {}".format(f, max_freq)
                ifreq = self.freqs.index(f)
                idb = self.intensities.index(db)
                self.reject_list.append((f, db, ifreq, idb))            

        if VERBOSE:
            print u"%.5f AI V" % (vmax)
            print u"%.6f FFT peak, at %d Hz\n" % (spec_max, max_freq)

        try:
            #self.data_lock.acquire()
            self.response_data.put(u'peaks', (f, db, rep), spec_peak_at_f)
            self.response_data.put(u'vmax', (f, db, rep), vmax)

            if SAVE_FFT_DATA:

                self.response_data.put(u'spectrums', (f, db, rep), spectrum)

                if SAVE_DATA_TRACES: 
                    self.data_traces[ifreq][idb][rep] = data
            #self.data_lock.release()
        except Exception, e:
            print u"ERROR: unable to save recorded data"
            print e
            raise
            #self.data_lock.release()

    def save_to_file(self, calf, sfolder, sfilename, keepcal=False, saveformat=u'npy', calpeak=None):
        #After running curve do calculations and save data to file
        
        print u"Saving..."
        
        print u'rejects : ', self.reject_list
        # go through FFT peaks and calculate playback resultant dB
        # for freq in self.fft_peaks
        vfunc = np.vectorize(calc_db)
        caldb = self.player.caldb
        calv = self.player.calv

        try:
            self.data_lock.acquire()

            cal_fft_peak = self.response_data.get(u'peaks', (calf, caldb))
            cal_vmax =  self.response_data.get(u'vmax', (calf, caldb))

            #self.data_lock.release()
            print u"Using FFT peak data from ", caldb, u" dB, ", calf, u" Hz tone to calculate calibration curve"
        except:
            print u"ERROR : could not retrieve data from specified calibration frequency, %d Hz, and intensity, %d dB" % (calf, caldb)
            cal_fft_peak = 0
            cal_vmax = 0

        #fft_peaks = self.response_data.data['peaks']
        #resultant_dB = vfunc(fft_peaks, caldb, cal_fft_peak)

        vin = self.response_data.data[u'vmax'].value
        print vin, caldb, calpeak
        resultant_dB = vfunc(vin, caldb, calpeak)

        self.response_data.data[u'frequency_rolloff'] = self.response_data.hdf5.create_dataset(u'frequency_rolloff', 
                                                                                  resultant_dB.shape)
        self.response_data.data[u'frequency_rolloff'][...] = resultant_dB
        self.response_data.attrs[u'dbmethod'] = calc_db.__doc__ + u" peak: max V"

        fname = sfilename
        while os.path.isfile(os.path.join(sfolder, fname + u'.' + saveformat)):
            # increment filename until we come across one that 
            # doesn't exist
            if not fname[-1].isdigit():
                fname = fname + u'0'
            else:
                currentno = re.search(u'(\d+)$', fname).group(0)
                prefix = fname[:-(len(currentno))]
                currentno = int(currentno) + 1
                fname = prefix + unicode(currentno)

        filename = os.path.join(sfolder, fname)

        if saveformat != u'hdf5':
            print u'SAVENAME ', filename
            self.response_data.export(filename, filetype=saveformat)

        if keepcal:
            # get vector of calibration intensity only
            caldb_idx = self.response_data.stim[u'intensities'].index(self.player.caldb)
            calibration_vector = resultant_dB[:,caldb_idx]
            np.save(caldata_filename(),calibration_vector)
            freqs = self.response_data.stim[u'frequencies']
            np.save(calfreq_filename(), freqs)

        
        if SAVE_NOISE:
            #noise_vfunc = np.vectorize(calc_noise)
            #noise_array = noise_vfunc(self.full_fft_data,0,2000)
            noise_array = np.zeros((len(self.freqs),len(self.intensities),self.nreps))
            for ifreq in xrange(len(self.freqs)):
                for idb in xrange(len(self.intensities)):
                    for irep in xrange(self.nreps):
                        noise_array[ifreq,idb,irep] = calc_noise(self.full_fft_data[ifreq,idb,irep], 0, 2000)

            np.save(sfolder + fname + NOISE_FNAME, noise_array)

        return resultant_dB

class Tone():
    def __init__(self):
        self.played = None
        self.recorded = None
