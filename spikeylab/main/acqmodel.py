import os, time
import threading
import numpy as np
import scipy.io.wavfile as wv

from spikeylab.io.players import FinitePlayer, ToneCurve, ContinuousPlayer
from spikeylab.tools.audiotools import spectrogram, calc_spectrum
from spikeylab.tools import spikestats
from spikeylab.tools.qthreading import ProtocolSignals

class AcquisitionModel():
    """Holds state information for an experimental session"""
    def __init__(self, threshold=None):
        self.signals = {}
        self.finite_player = None
        self.threshold = threshold
        self.signals = ProtocolSignals()

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

    def set_threshold(self, threshold):
        """Spike detection threshold

        :param threshold: electrical potential to determine spikes (V)
        :type threshold: float
        """
        self.threshold = threshold

    def set_save_params(self, savefolder, savename):
        """Folder and filename where raw experiment data will be saved to

        :param savefolder: folder for experiment data
        :type savefolder: str
        :param samename: filename template, without extention for individal experiment files
        :type savename: str
        """
        self.savefolder = savefolder
        self.savename = savename

    def set_explore_params(self, **kwargs):
        if self.finite_player is None:
            self.finite_player = FinitePlayer()

        if 'wavfile' in kwargs:
            sr, wavdata = wv.read(kwargs['wavfile'])
            wavdata = wavdata.astype('float')
            #normalize
            mx = np.amax(wavdata)
            wavdata = wavdata/mx

            # self.current_gen_rate = sr
            # self.current_signal = wavdata
            self.finite_player.set_stim(wavdata,sr)
        if 'acqtime' in kwargs:
            self.finite_player.set_aidur(kwargs['acqtime'])
        if 'aisr' in kwargs:
            self.finite_player.set_aisr(kwargs['aisr'])
        if 'aochan' in kwargs:
            self.aochan = kwargs['aochan']
        if 'aichan' in kwargs:
            self.aichan = kwargs['aichan']
        if 'aisr' in kwargs and 'acqtime' in kwargs:
            self.aitimes = np.linspace(0, kwargs['acqtime'], kwargs['acqtime']*float(kwargs['aisr']))
        if 'nreps' in kwargs:
            self.nreps = kwargs['nreps']
        if 'binsz' in kwargs:
            self.binsz = kwargs['binsz']

    def set_tone(self, f,db,dur,rft,sr):
        """Build a tone and set as next tone to be output. Does not call write to hardware"""
        return self.finite_player.set_tone(f,db,dur,rft,sr)

    def run_explore(self, interval):
        """Begin the set-up generation/acquisition

        :param interval: interval between succesive generations (start-to-start), in seconds
        :type interval: float
        """
        self._halt = False
        
        # TODO: some error checking to make sure valid paramenters are set

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.acq_thread = threading.Thread(target=self._explore_worker)

        # arm the first read
        self.finite_player.start(self.aochan, self.aichan)

        # and go!
        self.acq_thread.start()

    def _explore_worker(self):
        spike_counts = []
        spike_latencies = []
        spike_rates = []
        irep = 0
        while not self._halt:
            # print 'explore worker'
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
                    self.signals.warning.emit("WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed))
                self.last_tick = now

                response = self.finite_player.read()
                self.signals.response_collected.emit(self.aitimes, response)

                # process response; calculate spike times
                spike_times = spikestats.spike_times(response, self.threshold, self.finite_player.aisr)
                spike_counts.append(len(spike_times))
                if len(spike_times) > 0:
                    spike_latencies.append(spike_times[0])
                else:
                    spike_latencies.append(np.nan)
                spike_rates.append(spikestats.firing_rate(spike_times, self.finite_player.aitime))

                response_bins = spikestats.bin_spikes(spike_times, self.binsz)
                if len(response_bins) > 0:
                    self.signals.spikes_found.emit(response_bins, irep)

                self.finite_player.reset()

                irep +=1
                if irep == self.nreps:
                    total_spikes = float(sum(spike_counts))
                    avg_count = total_spikes/len(spike_counts)
                    avg_latency = sum(spike_latencies)/len(spike_latencies)
                    avg_rate = sum(spike_rates)/len(spike_rates)
                    irep = 0
                    self.signals.trace_finished.emit(total_spikes, avg_count, avg_latency, avg_rate)
                    spike_counts = []
                    spike_latencies = []
                    spike_rates = []

            except:
                raise
        self.finite_player.stop()

    def halt(self):
        """Stop the current on-going generation/acquisition"""
        self._halt = True


    def setup_curve(self, dur, sr, rft, nreps, freqs, intensities, aisr, aichan, aochan, interval):
        """Prepare a tuning curve"""
        self.ngenerated = 0
        self.nacquired = 0
        self._halt = False

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
        """Execute previously set-up tuning curve"""
        self.acq_thread.start()

    def _curve_worker(self):
        print "worker"
        while not self._halt:
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
                    self.signals.warning.emit("WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed))
                self.last_tick = now

                if not self.tonecurve.haswork():
                    # no more work left in the queue, collect last stim written.
                    self._halt = True
                else:
                    self.ngenerated +=1

                tone, response, f, db = self.tonecurve.next()

                # self.ui.flabel.setText(u"Frequency : %d" % (f))
                # self.ui.dblabel.setText(u"Intensity : %d" % (db))

                xfft, yfft = calc_spectrum(tone[0], self.tonecurve.player.get_samplerate())
                self.signals.stim_generated.emit((f,db),tone[1], tone[0], 
                                                        xfft, abs(yfft))
                self.signals.response_collected.emit(response[1], response[0])
                    # print "Frequency : %d, Intensity : %d" % (f, db)
                    # print "AO Vmax : %.5f" % (np.amax(abs(tone)))
            except:
                self.tonecurve.closedata()
                raise

    def closedata(self):
        self.tonecurve.closedata()

    def start_chart(self, aichan, samplerate):
        """Begin on-going chart style acqusition"""
        self.chart_player = ContinuousPlayer()
        self.chart_player.signals.ncollected.connect(self.emit_ncollected)
        self.chart_player.start(aichan,samplerate)

    def stop_chart(self):
        self.chart_player.stop()

    def emit_ncollected(self, data):
        # relay emit signal
        self.signals.ncollected.emit(data)