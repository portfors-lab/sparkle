import os, yaml
import logging
import numpy as np

from spikeylab.run.list_runner import ListAcquisitionRunner
from spikeylab.stim.types.stimuli_classes import WhiteNoise, FMSweep, PureTone
from spikeylab.tools.audiotools import attenuation_curve, calc_spectrum, get_peak, calc_db
from spikeylab.acq.players import FinitePlayer
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.gui.stim.factory import CCFactory
from spikeylab.tools.util import next_str_num
from spikeylab.tools.systools import get_src_directory

class CalibrationRunner(ListAcquisitionRunner):
    def __init__(self, *args):
        ListAcquisitionRunner.__init__(self, *args)

        self.player = FinitePlayer()

        self.stimulus = StimulusModel()
        # # insert stim component... either noise or chirp
        self.stim_components = [WhiteNoise(), FMSweep()]
        self.stimulus.insertComponent(self.stim_components[0])
        self.protocol_model.insert(self.stimulus, 0)

        save_data = True
        self.group_name = 'calibration_'

        self.calibration_vector = None
        self.calibration_freqs = None
        self.calibration_frange = None

    def get_stims(self):
        return self.stim_components

    def set_stim_by_index(self, index):
        # remove any current components
        self.stimulus.clearComponents()
        # add one to index because of tone curve
        self.stimulus.insertComponent(self.stim_components[index])

    def stash_calibration(self, attenuations, freqs, frange, calname):
        self.calibration_vector = attenuations
        self.calibration_freqs = freqs
        self.calibration_frange = frange
        self.calname = calname

    def stashed_calibration(self):
        return self.calibration_vector, self.calibration_freqs

    def apply_calibration(self, apply_cal):
        self.apply_cal = apply_cal

    def set_duration(self, dur):
        # self.stimulus.data(self.stimulus.index(0,0)).setDuration(dur)
        # this may be set at any time, and is not checked before run, so set
        # all stim components
        for comp in self.stim_components:
            comp.setDuration(dur)

    def set_reps(self, reps):
        self.stimulus.setRepCount(reps)

    def _initialize_run(self):
       
        data_items = self.datafile.keys()
        self.current_dataset_name = next_str_num(self.group_name, data_items)
        
        self.datafile.init_group(self.current_dataset_name, mode='calibration')
        
        logger = logging.getLogger('main')
        logger.debug('Calibrating with fs %s' %  self.stimulus.samplerate())
        
        self.datafile.init_data(self.current_dataset_name, mode='calibration', 
                                dims=(self.stimulus.repCount(), self.stimulus.duration()*self.stimulus.samplerate()))

        info = {'samplerate_ad': self.player.aisr}
        self.datafile.set_metadata(self.current_dataset_name, info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        if self.apply_cal:
            self.protocol_model.setCalibration(self.calibration_vector, self.calibration_freqs, self.calibration_frange)
        else:
            self.stimulus.component(0,0).setIntensity(self.caldb)
            # self.stimulus.data(self.stimulus.index(0,0)).setIntensity(self.caldb)
            self.calname = None
            self.protocol_model.setCalibration(None, None, None)

    def _initialize_test(self, test):
        return

    def _process_response(self, response, trace_info, irep):
        self.datafile.append(self.current_dataset_name, response, 
                             nested_name='signal')

        self.putnotify('response_collected', (self.aitimes, response))
        
    def process_calibration(self, save=True):
        """processes calibration control signal. Determines transfer function
        of speaker to get frequency vs. attenuation curve."""
        avg_signal = np.mean(self.datafile.get(self.current_dataset_name + '/signal'), axis=0)

        diffdB = attenuation_curve(self.stimulus.signal()[0], avg_signal,
                                        self.stimulus.samplerate(), self.calf)
        logger = logging.getLogger('main')
        logger.debug('The maximum dB attenuation is {}, caldB {}'.format(max(diffdB), self.caldb))

        # save a vector of only the calibration intensity results
        if save:
            self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                    dims=diffdB.shape,
                                    nested_name='calibration_intensities')
            self.datafile.append(self.current_dataset_name, diffdB,
                                 nested_name='calibration_intensities')

            relevant_info = {'frequencies': 'all', 'calibration_dB':self.caldb,
                             'calibration_voltage': self.calv, 'calibration_frequency': self.calf,
                             }
            self.datafile.set_metadata('/'.join([self.current_dataset_name, 'calibration_intensities']),
                                       relevant_info)

        else:
            # delete the data saved to file thus far.
            self.datafile.delete_group(self.current_dataset_name)
        return diffdB, self.current_dataset_name, self.calf


# wether to use relative peak level (from FFT), or calculate from
# microphone sensitivity level
USE_FFT = True
with open(os.path.join(get_src_directory(),'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
USE_RMS = config['use_rms']

class CalibrationCurveRunner(ListAcquisitionRunner):
    def __init__(self, *args):
        ListAcquisitionRunner.__init__(self, *args)

        self.group_name = 'calibration_test_'

        self.player = FinitePlayer()

        self.stimulus = StimulusModel()
        CCFactory.init_stim(self.stimulus)

        self.protocol_model.insert(self.stimulus, 0)

        # add in a tone at the calibration frequency and intensity
        control_stim = StimulusModel()
        self.control_tone = PureTone()
        control_stim.insertComponent(self.control_tone)
        self.protocol_model.insert(control_stim, 0)

        save_data = True

    def set_save_params(self, folder=None, name=None):
        """Folder and filename where raw experiment data will be saved to

        :param savefolder: folder for experiment data
        :type savefolder: str
        :param samename: filename template, without extention for individal experiment files
        :type savename: str
        """
        if folder is not None:
            self.savefolder = folder
        if name is not None:
            self.savename = name

    def stash_calibration(self, attenuations, freqs, frange, calname):
        self.calibration_vector = attenuations
        self.calibration_freqs = freqs
        self.calibration_frange = frange
        self.calname = calname

    def apply_calibration(self, apply_cal):
        self.apply_cal = apply_cal

    def set_duration(self, dur):
        self.stimulus.component(0,0).setDuration(dur)
        # self.stimulus.data(self.stimulus.index(0,0)).setDuration(dur)

    def set_reps(self, reps):
        self.stimulus.setRepCount(reps)

    def _initialize_run(self):
        self.calibration_frequencies = []
        self.calibration_indexes = []

        data_items = self.datafile.keys()
        self.current_dataset_name = next_str_num(self.group_name, data_items)

        self.datafile.init_group(self.current_dataset_name, mode='calibration')
        self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(self.stimulus.traceCount(), self.stimulus.repCount()),
                                nested_name='fft_peaks')
        self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(self.stimulus.traceCount(), self.stimulus.repCount()),
                                nested_name='vamp')

        info = {'samplerate_ad': self.player.aisr}
        self.datafile.set_metadata(self.current_dataset_name, info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        self.control_tone.setDuration(self.stimulus.component(0,0).duration())
        self.control_tone.setRisefall(self.stimulus.component(0,0).risefall())
        
        logger = logging.getLogger('main')
        logger.debug('setting calibration frequency'.format(self.calf))
        self.control_tone.setFrequency(self.calf)
        self.control_tone.setIntensity(self.caldb)
        self.calpeak = None
        self.trace_counter = -1 # initialize to -1 instead of 0

        if self.apply_cal:
            self.protocol_model.setCalibration(self.calibration_vector, self.calibration_freqs, self.calibration_frange)
        else:
            self.protocol_model.setCalibration(None, None, None)

    def _initialize_test(self, test):
        self.peak_avg = []

    def _process_response(self, response, trace_info, irep):
        freq, spectrum = calc_spectrum(response, self.player.aisr)

        f = trace_info['components'][0]['frequency'] #only the one component (PureTone)
        db = trace_info['components'][0]['intensity']
        # print 'f', f, 'db', db
        
        # spec_max, max_freq = get_peak(spectrum, freq)
        spec_peak_at_f = spectrum[freq == f]
        if len(spec_peak_at_f) != 1:
            print u"COULD NOT FIND TARGET FREQUENCY ",f
            print 'target', f, 'freqs', freq
            spec_peak_at_f = np.array([-1])
            # self._halt = True
        peak_fft = spec_peak_at_f[0]

        if USE_RMS:
            vamp = np.sqrt(np.mean(pow(response,2))) #/ np.sqrt(2)
        else:
            vamp = np.amax(abs(response))

        if self.trace_counter >= 0:
            if irep == 0:
                if db == self.caldb:
                    self.calibration_frequencies.append(f)
                    self.calibration_indexes.append(self.trace_counter)
                self.trace_counter +=1
                self.peak_avg = []

            self.datafile.append(self.current_dataset_name, spec_peak_at_f, 
                                 nested_name='fft_peaks')
            self.datafile.append(self.current_dataset_name, np.array([vamp]), 
                                 nested_name='vamp')
            self.datafile.append_trace_info(self.current_dataset_name, trace_info)

            self.putnotify('response_collected', (self.aitimes, response))
        
        # calculate resultant dB and emit
        if USE_FFT:
            self.peak_avg.append(peak_fft)
        else:
            self.peak_avg.append(vamp)
        if irep == self.nreps-1:
            mean_peak = np.mean(self.peak_avg)
            if f == self.calf and db == self.caldb and self.trace_counter == -1:
                # this always is the first trace
                self.calpeak = mean_peak
                self.trace_counter +=1
            else:
                # use relative dB
                # resultdb = calc_db(mean_peak, self.calpeak) + self.caldb
                # dB according to microphone sensitivity
                resultdb = calc_db(mean_peak)
                self.putnotify('average_response', (f, db, resultdb))

    def process_calibration(self, save=True):
        """processes the data gathered in a calibration run (does not work if multiple
            calibrations), returns resultant dB"""

        vfunc = np.vectorize(calc_db)

        if USE_FFT:
            peaks = np.mean(abs(self.datafile.get(self.current_dataset_name + '/fft_peaks')), axis=1)
        else:
            peaks = np.mean(abs(self.datafile.get(self.current_dataset_name + '/vamp')), axis=1)

        # print 'calibration frequencies', self.calibration_frequencies
        # cal_index = self.calibration_indexes[self.calibration_frequencies.index(self.calf)]
        # cal_peak = peaks[cal_index]
        # cal_vmax = vmaxes[cal_index]

        # print 'vfunc inputs', vmaxes, self.caldb, cal_vmax

        resultant_dB = vfunc(peaks, self.calpeak) * -1 #db attenuation

        print 'calibration frequences', self.calibration_frequencies, 'indexes', self.calibration_indexes
        print 'attenuations', resultant_dB

        calibration_vector = resultant_dB[self.calibration_indexes].squeeze()
        # save a vector of only the calibration intensity results
            # delete the data saved to file thus far.
        self.datafile.delete_group(self.current_dataset_name)
        return resultant_dB, '', self.calf
