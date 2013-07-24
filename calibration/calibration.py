import threading
import queue
import os
import pickle
import re
import win32com.client
from multiprocessing import Process
from audiolab.calibration.datatypes import CalibrationObject

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

FFT_FNAME = '_ffttraces'
PEAKS_FNAME =  '_fftpeaks'
DB_FNAME = '_resultdb'
INDEX_FNAME = '_index'
DATA_FNAME = '_rawdata'
NOISE_FNAME = '_noise'
OUTPUT_FNAME = '_outtones'


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
        pa5 = win32com.client.Dispatch("PA5.x")
        success  = pa5.ConnectPA5('GB',1)
        if success == 1:
            print('Connection to PA5 attenuator established')
        else:
            print('Connection to PA5 attenuator failed')
            errmsg = pa5.GetError()
            print("Error: ", errmsg)
            raise Exception("Attenuator connection failed")

        self.attenuator = pa5

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def set_calibration(self, db_boost_array, frequencies):
        # use supplied array of intensity adjustment to adjust tone output
        if db_boost_array.shape != frequencies.shape:
            print("ERROR: calibration array and frequency array must have same dimensions")
            return

        self.calibration_vector = db_boost_array
        self.calibration_frequencies = frequencies
        print(self.calibration_vector)
        print(self.calibration_frequencies)

    def set_tone(self,f,db,dur,rft,sr):

        if self.calibration_vector is not None:
            adjdb = self.caldb - self.calibration_vector[self.calibration_frequencies == f][0]
        else:
            adjdb = 0

        tone, timevals, atten = make_tone(f,db,dur,rft,sr, self.caldb, self.calv, adjustdb=adjdb)

        if PRINT_WARNINGS:
            if np.amax(abs(tone)) < 0.005:
                print("WARNING : ENTIRE OUTPUT TONE VOLTAGE LESS THAN DEVICE MINIMUM")


        self.tone_lock.acquire()
        self.tone = tone
        self.sr = sr
        self.aitime = dur
        self.aisr = sr
        self.atten = atten
        self.tone_lock.release()

        return tone, timevals

    def get_samplerate(self):
        return self.sr

    def get_caldb(self):
        return self.caldb

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
            print("FIX ME : NESTED START OPERATIONS ALLOWED")

        self.daq_lock.acquire()

        self.ngenerated = 0
        self.nacquired = 0
       
        response_npts = int(self.aitime*self.aisr)
        npts = self.tone.size
        try:
            self.aitask = AITaskFinite(aichan, self.aisr, response_npts)
            self.aotask = AOTaskFinite(aochan, self.sr, npts, trigsrc=b"ai/StartTrigger")
            self.aotask.write(self.tone)

            if SAVE_OUTPUT:
                self.played_tones = [self.tone[:]]

        except:
            print('ERROR! TERMINATE!')
            self.stop()
            raise

        # save for later -- allow not to be changed?
        self.aochan = aochan
        self.aichan = aichan

        self.daq_lock.release()

    def read(self):
        try:
            if self.aotask is None:
                print("You must arm the calibration first")
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
            print('ERROR! TERMINATE!')
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
            self.aotask = AOTaskFinite(self.aochan, self.sr, npts, trigsrc=b"ai/StartTrigger")
            self.aotask.write(self.tone)
            self.attenuator.SetAtten(self.atten)
            self.ngenerated +=1

            if SAVE_OUTPUT:
                self.played_tones.append(self.tone[:])
        except:
            print('ERROR! TERMINATE!')
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
            print("No task running")
        self.aitask = None
        self.aotask = None
    
class ContinuousTone(PlayerBase):
    def __init__(self, aichan, aochan, sr, npts, ainpts, dbv):
        PlayerBase.__init__(self, dbv)
        # use continuous acquisition task, using NIDAQ everyncallback
        self.aitask = AITask(aichan, sr, ainpts)
        self.aotask = AOTask(aochan, sr, npts, trigsrc=b"ai/StartTrigger")
        self.aitask.register_callback(self.every_n_callback, ainpts)
                        
        if SAVE_OUTPUT:
            self.tone_array.append(self.tone[:])

        self.sr = sr
        self.signal=None

    def start(self):
        self.aotask.write(self.tone)
        self.aotask.StartTask()
        self.aitask.StartTask()

    def stop(self):
        try:
            self.aitask.stop()
            self.aotask.stop()
        except DAQError:
            print("No task running")
        except:
            raise
        self.aitask = None
        self.aotask = None

    def use_signal(self, signal):
        self.signal = signal

    def every_n_callback(self,task):
        
        # read in the data as it is acquired and append to data structure
        try:
            read = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,
                               inbuffer,task.n,byref(read),None)
            if SAVE_DATA_CHART:
                self.a.extend(inbuffer.tolist())
                # for now use stimulus data size also for acquisition
                #ainpts = len(self.tone)

            self.signal.ncollected.emit(inbuffer.tolist())
            self.ndata += read.value
            #print(self.ndata)
            
            n = read.value
            lims = self.display.axs[1].axis()
            #print("lims {}".format(lims))
            #print("ndata {}".format(self.ndata))
            
            # for display purposes only
            ndata = len(self.current_line_data)
            aisr = self.aisr

            #print(self.aisr, self.aitime, ndata/aisr)
            if ndata/aisr >= self.aitime:
                if len(self.current_line_data) != self.aitime*self.aisr:
                    print("incorrect number of data points saved")
                if SAVE_DATA_TRACES:
                    self.a.append(self.current_line_data)
                self.current_line_data = []
            
            self.current_line_data.extend(inbuffer.tolist())

        except MemoryError:
            print("data size: {}, elements: {}"
                  .format(sys.getsizeof(self.a)/(1024*1024), len(self.a)))
            self.aitask.stop()
            self.aotask.stop()
            raise

        except: 
            print('ERROR! TERMINATE!')
            #print("data size: {}, elements: {}".format(sys.getsizeof(self.a)/(1024*1024), len(self.a)))
            self.aitask.stop()
            self.aotask.stop()
            raise

class ToneCurve():
    def __init__(self, duration_s, samplerate, risefall_s, nreps, freqs, intensities, dbv=(100,0.1), calf=None, filename='temp.hdf5'):
        """
        Set up a tone curve which loops through frequencies (outer) and intensities (inner)
        """

        self.data_lock = threading.Lock()

        self.ngenerated = 0
        self.nacquired = 0

        self.caldata = CalibrationObject(filename, freqs, intensities, samplerate, duration_s, 
                                         risefall_s, nreps,v=dbv[1])
        self.dur = duration_s
        self.sr = samplerate
        self.rft = risefall_s
        self.nreps = nreps
        self.calf = calf

        self.caldata.init_data('peaks', 2)
        self.caldata.init_data('vmax', 2)

        if SAVE_FFT_DATA:
            # 4D array nfrequencies x nintensities x nreps x npoints
            #self.full_fft_data = np.zeros((len(freqs),len(intensities),nreps,int((duration_s*samplerate)/2)))
            self.caldata.init_data('spectrums',4)

        if SAVE_DATA_TRACES:
            #self.data_traces = np.zeros((len(freqs),len(intensities),nreps,int(duration_s*samplerate)))
            self.caldata.init_data('raw_traces',4)
        
        self.reject_list = []

        self.work_queue = queue.Queue()
        for ifreq, f in enumerate(freqs):
            for idb, db in enumerate(intensities):
                for irep in range(nreps):
                    self.work_queue.put((f,db,irep))
    
        #self.freqs = [x for x in freqs]
        #self.intensities = [x for x in intensities]

        self.player = TonePlayer(dbv)
        self.signal = None

    def assign_signal(self, signal):
        """
        Accepts a PyQt signal, which it will emit the parameters 
        (f, db, data, spectrum, freq) after each read operation
        """
        # allow this object to signal to GUI data to update
        self.signal = signal

    def arm(self, aochan, aichan):
        """
        Prepare the tone curve to play. This must be done before the first read
        """

        # first play the calibration frequency and intensity
        caltemp = []
        #if self.player.calibration_vector is not None:
        tone, t = self.player.set_tone(self.calf,self.player.caldb,self.dur, self.rft, self.sr)

        self.player.start(aochan, aichan)
        for irep in range(self.nreps):
            data = self.player.read()
            caltemp.append(np.amax(abs(data)))
            self.player.reset()

        self.calpeak = np.mean(caltemp)
        self.player.stop()

        # load first item in queue
        f, db, rep = self.work_queue.get()

        tone, t = self.player.set_tone(f,db,self.dur, self.rft, self.sr)

        self.player.start(aochan, aichan)
        self.current_fdb = (f, db, rep)
        self.current_tone = (tone, t)

        return self.calpeak

    def next(self):
        """
        Simultaneously present and read the next prepped stimulus, and reload.

        Internally stores acquired data. 
        Returns played_tone, data, times, played_f, played_db
        """

        print('reading')
        data = self.player.read()
        print('read')

        # save data here
        played_f, played_db, r = self.current_fdb

        # spin off thread for saving data, and move on to reset tone
        t = threading.Thread(target=self._storedata, args=(data[:], self.current_fdb))
        #t = Process(target=self._storesimple, args=(data, self.current_fdb))
        #t.daemon = True
        t.start()
        #self._storedata(data, self.current_fdb)

        # t will not change in tuning curve
        played_tone, t = self.current_tone

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
        
        return played_tone, data, t, played_f, played_db

    def haswork(self):
        return not self.work_queue.empty()

    def set_calibration(self, db_boost_array, frequencies):
        self.player.set_calibration(db_boost_array, frequencies)

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
                print("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")

        #tolerance of 1 Hz for frequency matching
        if max_freq < f-1 or max_freq > f+1:
            if PRINT_WARNINGS:
                print("WARNING : MAX SPECTRAL FREQUENCY DOES NOT MATCH STIMULUS")
                print("\tTarget : {}, Received : {}".format(f, max_freq))
                ifreq = self.freqs.index(f)
                idb = self.intensities.index(db)
                self.reject_list.append((f, db, ifreq, idb))            

        if VERBOSE:
            print("%.5f AI V" % (vmax))
            print("%.6f FFT peak, at %d Hz\n" % (spec_max, max_freq))

        try:
            #self.data_lock.acquire()
            self.caldata.put('peaks', (f, db, rep), spec_peak_at_f)
            self.caldata.put('vmax', (f, db, rep), vmax)

            if SAVE_FFT_DATA:

                self.caldata.put('spectrums', (f, db, rep), spectrum)

                if SAVE_DATA_TRACES: 
                    self.data_traces[ifreq][idb][rep] = data
            #self.data_lock.release()
        except Exception as e:
            print("ERROR: unable to save recorded data")
            print(e)
            raise
            #self.data_lock.release()

    def save_to_file(self, calf, sfolder, sfilename, keepcal=False, saveformat='npy'):
        #After running curve do calculations and save data to file
        
        print("Saving...")
        
        print('rejects : ', self.reject_list)
        # go through FFT peaks and calculate playback resultant dB
        # for freq in self.fft_peaks
        vfunc = np.vectorize(calc_db)
        caldb = self.player.caldb
        calv = self.player.calv

        try:
            self.data_lock.acquire()

            cal_fft_peak = self.caldata.get('peaks', (calf, caldb))
            cal_vmax =  self.caldata.get('vmax', (calf, caldb))

            #self.data_lock.release()
            print("Using FFT peak data from ", caldb, " dB, ", 
                  calf, " Hz tone to calculate calibration curve")
        except:
            print("ERROR : could not retrieve data from specified calibration frequency, %d Hz, and intensity, %d dB" % (calf, caldb))
            cal_fft_peak = 0
            cal_vmax = 0

        #fft_peaks = self.caldata.data['peaks']
        #resultant_dB = vfunc(fft_peaks, caldb, cal_fft_peak)

        vin = self.caldata.data['vmax'].value
        print(vin, caldb, self.calpeak)
        resultant_dB = vfunc(vin, caldb, self.calpeak)

        self.caldata.data['frequency_rolloff'] = resultant_dB
        self.caldata.attrs['dbmethod'] = calc_db.__doc__ + " peak: max V"

        fname = sfilename
        while os.path.isfile(os.path.join(sfolder, fname + '.' + saveformat)):
            # increment filename until we come across one that 
            # doesn't exist
            if not fname[-1].isdigit():
                fname = fname + '0'
            else:
                currentno = re.search('(\d+)$', fname).group(0)
                prefix = fname[:-(len(currentno))]
                currentno = int(currentno) + 1
                fname = prefix + str(currentno)

        filename = os.path.join(sfolder, fname)
        print('SAVENAME ', filename)

        self.caldata.save_to_file(filename, filetype=saveformat)

        if keepcal:
            # get vector of calibration intensity only
            caldb_idx = self.caldata.stim['intensities'].index(self.player.caldb)
            calibration_vector = resultant_dB[:,caldb_idx]
            np.save(caldata_filename(),calibration_vector)
            freqs = self.caldata.stim['frequencies']
            np.save(calfreq_filename(), freqs)

        
        if SAVE_NOISE:
            #noise_vfunc = np.vectorize(calc_noise)
            #noise_array = noise_vfunc(self.full_fft_data,0,2000)
            noise_array = np.zeros((len(self.freqs),len(self.intensities),self.nreps))
            for ifreq in range(len(self.freqs)):
                for idb in range(len(self.intensities)):
                    for irep in range(self.nreps):
                        noise_array[ifreq,idb,irep] = calc_noise(self.full_fft_data[ifreq,idb,irep], 0, 2000)

            np.save(sfolder + fname + NOISE_FNAME, noise_array)

        return resultant_dB

class Tone():
    def __init__(self):
        self.played = None
        self.recorded = None
