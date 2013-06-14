from daq_tasks import *
from audiotools import *
import threading
import queue
import os
import pickle

from PyDAQmx import *

SAVE_OUTPUT = False
PRINT_WARNINGS = True
SAVE_FFT_DATA = True
VERBOSE = False
SAVE_DATA_TRACES = True
SAVE_NOISE = False


FFT_FNAME = '_ffttraces'
PEAKS_FNAME =  '_fftpeaks'
DB_FNAME = '_resultdb'
INDEX_FNAME = '_index'
DATA_FNAME = "_rawdata"
NOISE_FNAME = "_noise"
OUTPUT_FNAME = "_outtones"

class TonePlayer():
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

    def start(self, aochan, aichan):

        # this shouldn't actually be possible still...
        if self.aitask is not None:
            self.on_stop()
            print("FIX ME : NESTED START OPERATIONS ALLOWED")

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
            self.on_stop
            raise

        # save for later -- allow not to be changed?
        self.aochan = aochan
        self.aichan = aichan

    def set_calibration(self, db_boost_array, frequencies):
        # use supplied array of intensity adjustment to adjust tone output
        if db_boost_array.shape != frequencies.shape:
            print("ERROR: calibration array and frequency array must have same dimensions")
            return

        self.calibration_vector = db_boost_array
        self.calibration_frequencies = frequencies

    def set_tone(self,f,db,dur,rft,sr):

        if self.calibration_vector is not None:
            adjdb = self.calibration_vector[self.calibration_frequencies == f]
        else:
            adjdb = 0

        tone, timevals = make_tone(f,db,dur,rft,sr, self.caldb, self.calv, adjustdb=adjdb)

        if PRINT_WARNINGS:
            if np.amax(abs(tone)) < 0.005:
                print("WARNING : ENTIRE OUTPUT TONE VOLTAGE LESS THAN DEVICE MINIMUM")

        self.tone_lock.acquire()
        self.tone = tone
        self.sr = sr
        self.aitime = dur
        self.aisr = sr
        self.tone_lock.release()

        return tone, timevals

    def read(self):
        try:
            # acquire data and reset task to be read for next timer event
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
            self.stop
            raise

        #self.daq_lock.release()
        return data

    def reset(self):
        print('reset')
        self.tone_lock.acquire()
        #self.daq_lock.acquire()

        npts =  self.tone.size
        response_npts = int(self.aitime*self.aisr)

        try:
            self.aitask = AITaskFinite(self.aichan, self.aisr, response_npts)
            self.aotask = AOTaskFinite(self.aochan, self.sr, npts, trigsrc=b"ai/StartTrigger")
            self.aotask.write(self.tone)
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
        except DAQError:
            print("No task running")
        except:
            raise
        self.aitask = None
        self.aotask = None

    def get_samplerate(self):
        return self.sr

    def get_caldb(self):
        return self.caldb

    def set_caldb(self, caldb):
        self.caldb = caldb

    def set_calv(self, calv):
        self.calv


class ToneCurve():
    def __init__(self, duration, samplerate, risefall, nreps, freqs, intensities, dbv=(100,0.1)):

        self.data_lock = threading.Lock()

        self.ngenerated = 0
        self.nacquired = 0

        self.dur = duration
        self.sr = samplerate
        self.rft = risefall
        self.nreps = nreps

        # data structure to store the averages of the resultant FFT peaks
        self.fft_peaks = np.zeros((len(freqs),len(intensities)))
        self.playback_dB = np.zeros((len(freqs),len(intensities)))
        self.vin = np.zeros((len(freqs),len(intensities)))
        self.fft_vals_lookup = {}
        self.fft_vals_index = np.zeros((len(freqs),len(intensities)))

        if SAVE_FFT_DATA:
            # 4D array nfrequencies x nintensities x nreps x npoints
            self.full_fft_data = np.zeros((len(freqs),len(intensities),nreps,int((duration*samplerate)/2)))
            
        if SAVE_DATA_TRACES:
            self.data_traces = np.zeros((len(freqs),len(intensities),nreps,int(duration*samplerate)))

        # data structure to hold repetitions, for averaging
        self.rep_temp = []
        self.vrep_temp = []
        self.reject_list = []
        
        self.freq_index = [x for x in freqs]

        self.work_queue = queue.Queue()
        for ifreq, f in enumerate(freqs):
            for idb, db in enumerate(intensities):
                for irep in range(nreps):
                    self.work_queue.put((f,db,irep))
    
        self.freqs = [x for x in freqs]
        self.intensities = [x for x in intensities]

        self.player = TonePlayer(dbv)

    def arm(self, aochan, aichan):

        # load first item in queue
        f, db, rep = self.work_queue.get()

        tone, t = self.player.set_tone(f,db,self.dur, self.rft, self.sr)
        self.player.start(aochan, aichan)
        self.current_fdb = (f, db, rep)
        self.current_tone = (tone, t)

    def next(self):

        print('reading')
        data = self.player.read()
        print('read')

        # save data here
        played_f, played_db, r = self.current_fdb
        self._storedata(data, self.current_fdb)
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

        spec_max, max_freq = get_fft_peak(spectrum,freq)
        spec_peak_at_f = spectrum[freq == f]

        vmax = np.amax(abs(data))

        if vmax < 0.005:
            if PRINT_WARNINGS:
                print("WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")

        #tolerance of 1 Hz for frequency matching
        if max_freq < f-1 or max_freq > f+1:
            if PRINT_WARNINGS:
                print("WARNING : MAX SPECTRAL FREQUENCY DOES NOT MATCH STIMULUS")
                print("\tTarget : {}, Received : {}".format(f, max_freq))
  
                ifreq, idb = self.fft_vals_lookup[(f,db)]
                self.reject_list.append((f, db, ifreq, idb))            

        if VERBOSE:
            print("%.5f AI V" % (vmax))
            print("%.6f FFT peak, at %d Hz\n" % (spec_max, max_freq))

        try:
            self.data_lock.acquire()
            self.rep_temp.append(spec_peak_at_f)
            self.vrep_temp.append(vmax)
            if rep == self.nreps-1:
                ifreq = self.freqs.index(f)
                idb = self.intensities.index(db)
                self.fft_peaks[ifreq][idb] =  np.mean(self.rep_temp)
                self.vin[ifreq][idb] = np.mean(self.vrep_temp)
                if VERBOSE:
                    print('\n' + '*'*40)
                    print("Rep values: {}\nRep mean: {}".format(self.rep_temp, np.mean(self.rep_temp)))
                    print("V rep values: {}\nV rep mean: {}".format(self.vrep_temp, np.mean(self.vrep_temp)))
                    print('*'*40 + '\n')
                self.rep_temp = []
                self.vrep_temp = []

            if SAVE_FFT_DATA:
                ifreq = self.freqs.index(f)
                idb = self.intensities.index(db)
                #ifreq, idb = self.fft_vals_lookup[(f,db)]
                self.full_fft_data[ifreq][idb][rep] = spectrum

                if SAVE_DATA_TRACES: 
                    self.data_traces[ifreq][idb][rep] = data
            self.data_lock.release()
        except Exception as e:
            print("ERROR: unable to save recorded data")
            print(e)
            self.data_lock.release()

    def save_to_file(self, calf, sfolder, sfilename, keepcal=False):
        #After running curve do calculations and save data to file
        
        print("Saving...")
        #print('fft peaks ', self.fft_peaks)
        print('rejects : ', self.reject_list)
        # go through FFT peaks and calculate playback resultant dB
        #for freq in self.fft_peaks
        vfunc = np.vectorize(calc_db)
        caldb = self.player.caldb
        calv = self.player.calv
        #dB_from_v_vfunc = np.vectorize(calc_db_from_v)

        try:
            self.data_lock.acquire()
            ifreq = self.freqs.index(calf)
            idb = self.intensities.index(caldb)
            cal_fft_peak = self.fft_peaks[ifreq][idb]
            cal_vmax =  self.vin[ifreq][idb]
            #self.data_lock.release()
            print("Using FFT peak data from ", caldb, " dB, ", 
                  calf, " Hz tone to calculate calibration curve")
        except:
            print("ERROR : could not retrieve data from specified calibration frequency, %d Hz, and intensity, %d dB" % (calf, caldb))
            cal_fft_peak = 0
            cal_vmax = 0

        #resultant_dB = vfunc(self.fft_peaks, self.caldb, cal_fft_peak)
        resultant_dB = vfunc(self.vin, caldb, cal_vmax)

        fname = sfilename
        while os.path.isfile(os.path.join(sfolder, fname + INDEX_FNAME + ".pkl")):
            # increment filename until we come across one that 
            # doesn't exist
            if not fname[-1].isdigit():
                fname = fname + '0'
            else:
                currentno = re.search('(\d+)$', fname).group(0)
                prefix = fname[:-(len(currentno))]
                currentno = int(currentno) +1
                fname = prefix + str(currentno)

        if SAVE_FFT_DATA:
            filename = os.path.join(sfolder, fname + FFT_FNAME)
            np.save(filename, self.full_fft_data)

            filename = os.path.join(sfolder, fname + PEAKS_FNAME)
            np.save(filename, self.fft_peaks)

            with open(os.path.join(sfolder, fname + INDEX_FNAME + ".pkl"), 'wb') as cfo:
                # make a dictionary of the other paramters used to 
                # generate this roll-off curve
                params = {'calV': calv, 'caldB' : caldb, 
                          'calf' : calf, 'rft' : self.rft, 
                          'samplerate' : self.sr, 'duration' : self.dur}
                pickle.dump([self.freqs, self.intensities, self.reject_list, params], cfo)

            if SAVE_DATA_TRACES:
                filename = os.path.join(sfolder, fname + DATA_FNAME)
                np.save(filename, self.data_traces)

            if SAVE_OUTPUT:
                filename = os.path.join(sfolder, fname + OUTPUT_FNAME)
                np.save(filename, self.tone_array)

        filename = os.path.join(sfolder, fname + DB_FNAME)
        np.save(filename, resultant_dB)
        np.savetxt(filename + ".txt", resultant_dB)

        if keepcal:
            filename = "calibration_data"
            calibration_vector = resultant_dB[:,0]
            np.save(filename,calibration_vector)
            with open("calibration_index.pkl",'wb') as pkf:
                pickle.dump(self.freq_index, pkf)
        

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
