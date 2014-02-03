import os, time
import threading
import json
import numpy as np
import scipy.io.wavfile as wv

from spikeylab.io.players import FinitePlayer, ContinuousPlayer
from spikeylab.tools.audiotools import spectrogram, calc_spectrum, get_fft_peak, calc_db
from spikeylab.tools import spikestats
from spikeylab.tools.qthreading import ProtocolSignals
from spikeylab.tools.util import increment_title, create_unique_path
from spikeylab.data.dataobjects import AcquisitionData, load_calibration_file
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types import get_stimuli_models
from spikeylab.main.protocol_model import ProtocolTabelModel
from spikeylab.stim.tceditor import CCFactory

SAVE_EXPLORE = True

class Broken(Exception): pass

class AcquisitionModel():
    """Holds state information for an experimental session"""
    def __init__(self, threshold=None):
        self.signals = {}
        self.threshold = threshold
        self.signals = ProtocolSignals()
        self.finite_player = FinitePlayer()
        self.chart_player = ContinuousPlayer()
        self.chart_player.set_read_function(self.emit_ncollected)

        self.datafile = None
        self.savefolder = None
        self.savename = None
        self.calname = 'calibration'
        self.saveall = True
        self.set_name = 'explore_0'
        self.group_name = 'segment_0'
        self.chart_name = 'chart_0'
        self.caldb = 100
        self.calv = 0.1
        self.calf = 20000

        self.protocol_model = ProtocolTabelModel()
        # stimulus for explore function
        self.stimulus = StimulusModel()
        self.calibration_stimulus = StimulusModel()
        CCFactory.init_stim(self.calibration_stimulus)
        self.signals.samplerateChanged = self.stimulus.samplerateChanged
        self.update_reference_voltage()
        self.set_calibration(None)

        stimuli_types = get_stimuli_models()
        self.explore_stimuli = [x() for x in stimuli_types if x.explore]

        self.binsz = 0.005

    def update_reference_voltage(self):
        self.stimulus.setReferenceVoltage(self.caldb, self.calv)
        self.calibration_stimulus.setReferenceVoltage(self.caldb, self.calv)
        self.protocol_model.setReferenceVoltage(self.caldb, self.calv)

    def stimuli_list(self):
        return self.explore_stimuli

    def set_calibration(self, cal_fname):
        if cal_fname is None:
            self.calibration_vector, self.calibration_freqs = None, None
        else:    
            try:
                cal = load_calibration_file(cal_fname)
            except:
                print "Error: unable to load calibration data from file: ", cal_fname
                raise
            self.calibration_vector, self.calibration_freqs = cal
        self.update_reference_voltage()
        # set the calibration for the player objects
        self.stimulus.set_calibration(self.calibration_vector, self.calibration_freqs)
        self.calibration_stimulus.set_calibration(self.calibration_vector, self.calibration_freqs)

    def create_data_file(self):
        # find first available file name
        if self.savefolder is None or self.savename is None:
            print "You must first set a save folder and filename"
        fname = create_unique_path(self.savefolder, self.savename)
        self.datafile = AcquisitionData(fname)
        return fname

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

    def set_calibration_file_name(self, savename):
        """Filename for which to save calibrations to"""
        self.calname = savename

    def set_params(self, **kwargs):

        if 'acqtime' in kwargs:
            self.finite_player.set_aidur(kwargs['acqtime'])
        if 'aisr' in kwargs:
            self.finite_player.set_aisr(kwargs['aisr'])
            self.chart_player.set_aisr(kwargs['aisr'])
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
        if 'savechart' in kwargs:
            self.saveall = kwargs['savechart']
        if 'caldb' in kwargs:
            self.caldb = kwargs['caldb']
        if 'calv' in kwargs:
            self.calv = kwargs['calv']
        if 'calf' in kwargs:
            self.calf = kwargs['calf']
        if 'caldb' in kwargs or 'calv' in kwargs:
            self.update_reference_voltage()

    def clear_explore_stimulus(self):
        self.stimulus.clearComponents()

    def set_stim_by_index(self, index):
        # remove any current components
        if self.stimulus.columnCount() > 0:
            self.stimulus.clearComponents()
        self.stimulus.insertComponent(self.explore_stimuli[index])
        signal, atten = self.stimulus.signal()
        self.finite_player.set_stim(signal, self.stimulus.samplerate(), attenuation=atten)
        return signal

    def explore_stim_names(self):
        stim_names = []
        for stim in self.explore_stimuli:
            stim_names.append(stim.name)
        return stim_names

    def run_explore(self, interval):
        """Begin the set-up generation/acquisition

        :param interval: interval between succesive generations (start-to-start), in seconds
        :type interval: float
        """
        self._halt = False
        
        # TODO: some error checking to make sure valid paramenters are set
        if SAVE_EXPLORE:
            # initize data set
            self.current_dataset_name = self.set_name
            self.datafile.init_data(self.current_dataset_name, self.aitimes.shape, mode='open')
            self.set_name = increment_title(self.set_name)

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.acq_thread = threading.Thread(target=self._explore_worker)

        # arm the first read
        self.finite_player.set_aochan(self.aochan)
        self.finite_player.set_aichan(self.aichan)
        self.finite_player.start()

        # and go!
        self.acq_thread.start()

        return self.acq_thread

    def _explore_worker(self):
        spike_counts = []
        spike_latencies = []
        spike_rates = []
        irep = 0
        while not self._halt:
            # print 'explore worker'
            try:
                self.interval_wait()

                response = self.finite_player.run()
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

                if SAVE_EXPLORE:
                    # save response data
                    self.save_data(response)

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
        self.datafile.trim(self.current_dataset_name)

    def set_explore_samplerate(self, fs):
        print 'setting generation rate', fs
        if not self.stimulus.contains('Vocalization'):
            self.stimulus.setSamplerate(fs)
        else:
            print 'ERROR: cannot set samplerate on stimulus containing vocal file'

    def run_protocol(self, interval):
        self._halt = False

        self.current_dataset_name = self.group_name
        self.datafile.init_group(self.current_dataset_name)
        self.group_name = increment_title(self.group_name)
        info = {'samplerate_ad': self.finite_player.aisr}
        self.datafile.set_metadata(self.current_dataset_name, info)

        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.finite_player.set_aochan(self.aochan)
        self.finite_player.set_aichan(self.aichan)
        stimuli = self.protocol_model.stimulusList()

        self.acq_thread = threading.Thread(target=self._protocol_worker, 
                                           args=(self.finite_player, stimuli, self.datafile),
                                           kwargs={'initialize_test':self.init_test, 
                                           'process_response':self.process_response})

        self.acq_thread.start()

        return self.acq_thread

    def _protocol_worker(self, player, stimuli, datafile, initialize_test=None, 
                         process_response=None):
        try:
            for itest, test in enumerate(stimuli):
                # pull out signal from stim model
                test.setReferenceVoltage(self.caldb, self.calv)

                if initialize_test:
                    initialize_test(test)
                traces, doc = test.expandedStim()
                nreps = test.repCount()
                self.nreps = test.repCount() # not sure I like this
                for itrace, (trace, trace_doc) in enumerate(zip(traces, doc)):

                    signal, atten = trace
                    player.set_stim(signal, test.samplerate(), atten)

                    player.start()
                    for irep in range(nreps):
                        self.interval_wait()
                        if self._halt:
                            raise Broken
                        response = player.run()
                        if process_response:
                            process_response(response, trace_doc, irep)
                        if irep == 0:
                            # do this after collection so plots match details
                            self.signals.stim_generated.emit(signal, test.samplerate())
                            self.signals.current_trace.emit(itest,itrace,trace_doc)
                        self.signals.current_rep.emit(irep)

                        player.reset()
                    # always save protocol response
                    datafile.append_trace_info(self.current_dataset_name, trace_doc)

                    player.stop()
        except Broken:
            # save some abortion message
            player.stop()

        self.signals.group_finished.emit(self._halt)

    def init_test(self, test):
        recording_length = self.aitimes.shape[0]
        test.set_calibration(self.calibration_vector, self.calibration_freqs)
        self.datafile.init_data(self.current_dataset_name, 
                                dims=(test.traceCount(), test.repCount(), recording_length),
                                mode='finite')
    def init_chart_test(self, test):
        test.set_calibration(self.calibration_vector, self.calibration_freqs)

    def init_calibration(self, test):
        test.setReorderFunc(self.reorder_calibration_traces)
        self.calfile.init_group(self.current_dataset_name)
        self.calfile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(test.traceCount(), test.repCount()),
                                nested_name='fft_peaks')
        self.calfile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(test.traceCount(), test.repCount()),
                                nested_name='vmax')

    def process_response(self, response, trace_info, irep):
        if irep == 0:
            spike_counts = []
            spike_latencies = []
            spike_rates = []
        else:
            spike_counts = self.spike_counts
            spike_latencies = self.spike_latencies
            spike_rates = self.spike_rates

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

        self.datafile.append(self.current_dataset_name, response)

        if irep == self.nreps-1:
            total_spikes = float(sum(spike_counts))
            avg_count = total_spikes/len(spike_counts)
            avg_latency = sum(spike_latencies)/len(spike_latencies)
            avg_rate = sum(spike_rates)/len(spike_rates)
            self.signals.trace_finished.emit(total_spikes, avg_count, avg_latency, avg_rate)
    
        self.spike_counts = spike_counts
        self.spike_latencies = spike_latencies
        self.spike_rates = spike_rates

    def interval_wait(self):
        # calculate time since last interation and wait to acheive desired interval
        now = time.time()
        elapsed = (now - self.last_tick)*1000
        #print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
        if elapsed < self.interval:
            #print('sleep ', (self.interval-elapsed))
            self.signals.warning.emit('')
            time.sleep((self.interval-elapsed)/1000)
            now = time.time()
        elif elapsed > self.interval:
            self.signals.warning.emit("WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed))
        self.last_tick = now

    def save_data(self, data):
        self.datafile.append(self.current_dataset_name, data)
        # save stimulu info
        info = self.stimulus.doc()
        info['samplerate_ad'] = self.finite_player.aisr
        self.datafile.append_trace_info(self.current_dataset_name, info)

    def halt(self):
        """Stop the current on-going generation/acquisition"""
        self._halt = True

    def close_data(self):
        if self.datafile is not None:
            self.datafile.close()

    def start_chart(self):
        """Begin on-going chart style acqusition"""
        self.current_dataset_name = self.chart_name
        self.datafile.init_data(self.current_dataset_name, mode='continuous')
        self.chart_name = increment_title(self.chart_name)
        
        # stimulus tracker channel hard-coded at last chan for now
        self.chart_player.start_continuous([self.aichan, u"PCI-6259/ai31"])

    def stop_chart(self):
        self.chart_player.stop_all()
        self.datafile.consolidate(self.current_dataset_name)

    def emit_ncollected(self, data):
        # relay emit signal
        response = data[0,:]
        stim_recording = data[1,:]
        self.signals.ncollected.emit(stim_recording, response)
        if self.saveall:
            self.datafile.append(self.current_dataset_name, response)

    def run_chart_protocol(self, interval):
        self._halt = False

        self.chart_player.set_aochan(self.aochan)
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        
        stimuli = self.protocol_model.stimulusList()
        self.acq_thread = threading.Thread(target=self._protocol_worker, 
                                           args=(self.chart_player, stimuli, self.datafile),
                                           kwargs={'initialize_test':self.init_chart_test})

        self.acq_thread.start()
        return self.acq_thread

    def run_calibration(self, interval, apply_cal):
        self._halt = False
        self.current_dataset_name = 'calibration'
        self.calibration_frequencies = []
        self.calibration_indexes = []
        self.trace_counter = 0 # don't like this!!!
        # save the start time and set last tick to expired, so first
        # acquisition loop iteration executes immediately
        self.start_time = time.time()
        self.last_tick = self.start_time - (interval/1000)
        self.interval = interval
        self.finite_player.set_aochan(self.aochan)
        self.finite_player.set_aichan(self.aichan)
        if not apply_cal:
            self.calibration_stimulus.set_calibration(None, None)

        if self.savefolder is None or self.savename is None:
            print "You must first set a save folder and filename"
        fname = create_unique_path(self.savefolder, self.calname)
        print 'calibration file name', fname
        self.calfile = AcquisitionData(fname)

        self.acq_thread = threading.Thread(target=self._protocol_worker, 
                                           args=(self.finite_player, [self.calibration_stimulus],
                                            self.calfile),
                                           kwargs={'initialize_test':self.init_calibration, 
                                           'process_response':self.process_caltone})

        self.acq_thread.start()
        return self.acq_thread, fname

    def process_caltone(self, recorded_tone, trace_info, irep):
        freq, spectrum = calc_spectrum(recorded_tone, self.finite_player.aisr)

        f = trace_info['components'][0]['frequency'] #only the one component (PureTone)
        db = trace_info['components'][0]['intensity']
        # print 'f', f, 'db', db
        if db == self.caldb:
            self.calibration_frequencies.append(f)
            self.calibration_indexes.append(self.trace_counter)
        self.trace_counter +=1
        
        spec_max, max_freq = get_fft_peak(spectrum, freq)
        spec_peak_at_f = spectrum[freq == f]
        if len(spec_peak_at_f) != 1:
            print u"COULD NOT FIND TARGET FREQUENCY ",f
            print 'target', f, 'freqs', freq
            spec_peak_at_f = np.array([-1])
            # self._halt = True

        vmax = np.amax(abs(recorded_tone))

        self.calfile.append(self.current_dataset_name, spec_peak_at_f, 
                             nested_name='fft_peaks')
        self.calfile.append(self.current_dataset_name, np.array([vmax]), 
                             nested_name='vmax')

        self.signals.response_collected.emit(self.aitimes, recorded_tone)
        self.signals.calibration_response_collected.emit((f, db), spectrum, freq, spec_peak_at_f[0], vmax)

    def process_calibration(self, save=True):
        """processes the data gathered in a calibration run (does not work if multiple
            calibrations), returns resultant dB"""
        print 'process the calibration'
        self.calibration_stimulus.set_calibration(self.calibration_vector, self.calibration_freqs)
        dataset_name = 'calibration'

        vfunc = np.vectorize(calc_db)

        peaks = abs(self.calfile.get('fft_peaks'))
        vmaxes = abs(self.calfile.get('vmax'))

        # print 'calibration frequencies', self.calibration_frequencies
        cal_index = self.calibration_indexes[self.calibration_frequencies.index(self.calf)]

        cal_peak = peaks[cal_index]
        cal_vmax = vmaxes[cal_index]

        # print 'vfunc inputs', vmaxes, self.caldb, cal_vmax
        resultant_dB = vfunc(vmaxes, self.caldb, cal_vmax)
        # print 'results', resultant_dB

        calibration_vector = resultant_dB[self.calibration_indexes].squeeze()
        # save a vector of only the calibration intensity results
        fname = self.calfile.filename
        if save:
            self.calfile.init_data(dataset_name, mode='calibration',
                                    dims=calibration_vector.shape,
                                    nested_name='calibration_intensities')
            self.calfile.append(dataset_name, calibration_vector,
                                 nested_name='calibration_intensities')

            relevant_info = {'frequencies':self.calibration_frequencies, 'calibration_dB':self.caldb,
                             'calibration_voltage': self.calv}
            self.calfile.set_metadata(u'calibration_intensities',
                                       relevant_info)
            self.calfile.close()
            self.set_calibration(fname)
            self.signals.calibration_file_changed.emit(fname)
        else:
            # delete the data saved to file thus far.
            self.calfile.close()
            os.remove(fname)
        return resultant_dB

    def reorder_calibration_traces(self, doclist):
        # Pick out the calibration frequency and put it first
        order = range(len(doclist))
        for i, trace in enumerate(doclist):
            if trace['components'][0]['frequency'] == self.calf and trace['components'][0]['intensity'] == self.caldb:
                order.pop(i)
                order.insert(0,i)
                return order
        else:
            #did not find calibration frequency, raise Error
            raise Exception('calibraiton frequency not found in stimulus')