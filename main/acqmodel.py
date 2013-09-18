import os, time
import threading
import numpy as np
import scipy.io.wavfile as wv

from audiolab.calibration.calibration import TonePlayer, ToneCurve
from audiolab.tools.audiotools import spectrogram, calc_spectrum

class AcquisitionModel():
    def __init__(self):
        self.signals = {}
        self.toneplayer = None

    def set_calibration(self, cal_fname):
        print "FIX ME"
        try:
            caldata = mightyload(cal_fname)
            calibration_vector = caldata['intensities']
            calibration_freqs = caldata['frequencies']
        except:
            print "Error: unable to load calibration data from file: ", cal_fname
        # calibration_vector = np.load(os.path.join(caldata_filename()))
        # calibration_freqs = np.load(os.path.join(calfreq_filename()))

    def set_save_params(self, savefolder, savename):
        self.savefolder = savefolder
        self.savename = savename

    def register_signal(self, signal, name):
        # saves a reference to specific types of pyqt signals for GUI
        # communication. Allowed names are 
        self.signals[name] = signal

    def set_explore_params(self, **kwargs):
        if self.toneplayer is None:
            self.toneplayer = TonePlayer()

        if kwargs['wavfile']:
            sr, wavdata = wv.read(kwargs['wavfile'])
            wavdata = wavdata.astype('float')
            #normalize
            mx = np.amax(wavdata)
            wavdata = wavdata/mx

            # self.current_gen_rate = sr
            # self.current_signal = wavdata
            self.toneplayer.set_stim(wavdata,sr)
        if kwargs['acqtime']:
            self.toneplayer.set_aidur(kwargs['acqtime'])
        if kwargs['aisr']:
            self.toneplayer.set_aisr(kwargs['aisr'])
        if kwargs['aochan']:
            self.aochan = kwargs['aochan']
        if kwargs['aichan']:
            self.aichan = kwargs['aichan']
        if kwargs['aisr'] and kwargs['acqtime']:
            self.aitimes = np.linspace(0, kwargs['acqtime'], kwargs['acqtime']*float(kwargs['aisr']))

    def run_explore(self, interval):
        self.halt = False
        
        # TODO: some error checking to make sure valid paramenters are set

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.acq_thread = threading.Thread(target=self._explore_worker)

        # arm the first read
        self.toneplayer.start(self.aochan, self.aichan)

        # and go!
        self.acq_thread.start()

    def _explore_worker(self):
        while not self.halt:
            print 'explore worker'
            try:
                # calculate time since last interation and wait to acheive desired interval
                now = time.time()
                elapsed = (now - self.last_tick)*1000
                #print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
                if elapsed < self.interval:
                    #print('sleep ', (self.interval-elapsed))
                    time.sleep((self.interval-elapsed)/1000)
                    now = time.time()
                elif elapsed > self.interval:
                    print u"WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed)
                self.last_tick = now

                response = self.toneplayer.read()
                # do something to display response - signal?

                self.signals['response_collected'].emit(self.aitimes, response)

                self.toneplayer.reset()
            except:
                raise
        self.toneplayer.stop()

    def halt_explore(self):
        self.halt = True


    def setup_curve(self, dur, sr, rft, nreps, freqs, intensities, aisr, aichan, aochan, interval):

        self.ngenerated = 0
        self.nacquired = 0
        self.halt = False

        fname = os.path.join(self.savefolder,self.savename+'.hdf5')
        
        self.tonecurve = ToneCurve(dur, sr, rft, nreps, freqs, 
                                            intensities, 
                                           filename=fname,
                                           samplerate_acq=aisr, mode='tuning')

        # self.tonecurve.assign_signal(self.signals.spectrum_analyzed)
        self.calval = self.tonecurve.arm(aochan, aichan)
        self.ngenerated +=1

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.acq_thread = threading.Thread(target=self._curve_worker)

    def run_curve(self):
        self.acq_thread.start()

    def _curve_worker(self):
        print "worker"
        while not self.halt:
            try:
                # this thread runs only for the tuning curve

                # calculate time since last interation and wait to acheive desired interval
                now = time.time()
                elapsed = (now - self.last_tick)*1000
                #print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
                if elapsed < self.interval:
                    #print('sleep ', (self.interval-elapsed))
                    time.sleep((self.interval-elapsed)/1000)
                    now = time.time()
                elif elapsed > self.interval:
                    print u"WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed)
                self.last_tick = now

                if not self.tonecurve.haswork():
                    # no more work left in the queue, collect last stim written.
                    self.halt = True
                else:
                    self.ngenerated +=1

                tone, response, f, db = self.tonecurve.next()

                # self.ui.flabel.setText(u"Frequency : %d" % (f))
                # self.ui.dblabel.setText(u"Intensity : %d" % (db))

                xfft, yfft = calc_spectrum(tone[0], self.tonecurve.player.get_samplerate())
                if self.signals["stim_generated"]:
                    self.signals["stim_generated"].emit((f,db),tone[1], tone[0], 
                                                        xfft, abs(yfft))
                    self.signals['response_collected'].emit(response[1], response[0])
                else:
                    print "Frequency : %d, Intensity : %d" % (f, db)
                    print "AO Vmax : %.5f" % (np.amax(abs(tone)))
            except:
                self.tonecurve.closedata()
                raise

    def halt_curve(self):
        self.halt = True

    def closedata(self):
        self.tonecurve.closedata()