import logging
import os

import numpy as np
import yaml

from sparkle.acq.players import FinitePlayer
from sparkle.gui.stim.factory import CCFactory
from sparkle.run.list_runner import ListAcquisitionRunner
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import FMSweep, PureTone, WhiteNoise
from sparkle.tools.audiotools import attenuation_curve, calc_db, \
    calc_spectrum, signal_amplitude
from sparkle.tools.systools import get_src_directory
from sparkle.tools.util import next_str_num


class AbstractCalibrationRunner(ListAcquisitionRunner):
    """Provides some common fucntionality for calibration presentation"""
    def stash_calibration(self, attenuations, freqs, frange, calname):
        """Save it for later"""
        self.calibration_vector = attenuations
        self.calibration_freqs = freqs
        self.calibration_frange = frange
        self.calname = calname

    def stashed_calibration(self):
        """Gets a stashed calibration

        :returns: numpy.ndarray, numpy.ndarray -- frequency response values, frequencies
        """
        return self.calibration_vector, self.calibration_freqs

    def apply_calibration(self, apply_cal):
        """Whether to apply a stashed calibration to the outgoing stimulus

        :param apply_cal: True if calibration should be applied
        :type apply_cal: bool
        """
        self.apply_cal = apply_cal

    def set_mphone_calibration(self, sens, db):
        self.mphonesens = sens
        self.mphonedb = db

    def set_duration(self, dur):
        """Sets the duration of the stimulus (seconds)

        :param dur: desired duration of the stimulus
        :type dur: float
        """
        raise NotImplementedError


class CalibrationRunner(AbstractCalibrationRunner):
    """Handles Calibration acquistion, where there is a single unique 
    stimulus used to capture the frequency response of the system.
    This class may hold many different types of stimuli (currently 2),
    but only one is presented per calibration run."""
    def __init__(self, *args):
        super(AbstractCalibrationRunner, self).__init__(*args)

        self.player = FinitePlayer()

        self.stimulus = StimulusModel()
        # # insert stim component... either noise or chirp
        self.stim_components = [WhiteNoise(), FMSweep()]
        self.stimulus.insertComponent(self.stim_components[0])
        self.protocol_model.insert(self.stimulus, 0)

        # reference tone for setting the refence voltage==db
        self.refstim = StimulusModel()
        tone = PureTone()
        tone.setRisefall(0.001)
        self.refstim.insertComponent(tone, 0,0)
        self.reftone = tone

        self.save_data = True
        self.group_name = 'calibration_'

        self.calibration_vector = None
        self.calibration_freqs = None
        self.calibration_frange = None

    def get_stims(self):
        """Gets the stimuli available for setting as the current calibration stimulus
        
        :returns: list<:class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`>
        """
        return self.stim_components

    def set_stim_by_index(self, index):
        """Sets the stimulus to be generated to the one referenced by index

        :param index: index number of stimulus to set from this class's internal list of stimuli
        :type index: int
        """
        # remove any current components
        self.stimulus.clearComponents()
        # add one to index because of tone curve
        self.stimulus.insertComponent(self.stim_components[index])

    def set_duration(self, dur):
        """See :meth:`AbstractCalibrationRunner<sparkle.run.calibration_runner.AbstractCalibrationRunner.set_duration>`"""
        # this may be set at any time, and is not checked before run, so set
        # all stim components
        for comp in self.stim_components:
            comp.setDuration(dur)
        self.reftone.setDuration(dur)

    def _initialize_run(self):
       
        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        if self.apply_cal:
            self.protocol_model.setCalibration(self.calibration_vector, self.calibration_freqs, self.calibration_frange)
            # calibration testing doesn't save anything
            self.save_data = False
        else:
            data_items = self.datafile.keys()
            self.current_dataset_name = next_str_num(self.group_name, data_items)
            
            self.datafile.init_group(self.current_dataset_name, mode='calibration')
            
            logger = logging.getLogger('main')
            logger.debug('Calibrating with fs %s' %  self.stimulus.samplerate())

            self.datafile.init_data(self.current_dataset_name, mode='calibration', 
                                    dims=(self.stimulus.repCount(), self.stimulus.duration()*self.stimulus.samplerate()))

            info = {'samplerate_ad': self.player.aifs}
            self.datafile.set_metadata(self.current_dataset_name, info)
            # point is to output the signal at the specificed voltage, to we set
            # the intensity of the components to match whatever the caldb is now
            self.save_data = True
            self.stimulus.component(0,0).setIntensity(self.caldb)
            print 'USING {} V, {} Hz, {} dBSPL'.format(self.calv, self.calf, self.caldb)
            self.reftone.setIntensity(self.caldb)
            self.reftone.setFrequency(self.calf)
            self.protocol_model.insert(self.refstim,0)
            self.calname = None
            self.protocol_model.setCalibration(None, None, None)

            self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                    nested_name='reference_tone',
                                    dims=(self.stimulus.repCount(), self.stimulus.duration()*self.stimulus.samplerate()))

    def _initialize_test(self, test):
        assert test.samplerate() == self.player.aifs

    def _process_response(self, response, trace_info, irep):
        if self.save_data:
            if trace_info['components'][0]['stim_type'] == 'Pure Tone':
                self.datafile.append(self.current_dataset_name, response, nested_name='reference_tone')
            elif trace_info['components'][0]['stim_type'] == 'FM Sweep' or trace_info['components'][0]['stim_type'] == 'White Noise':
                self.datafile.append(self.current_dataset_name, response)
            else:
                raise Exception("Improper calibration stimulus : {}".format(trace_info['components'][0]['stim_type']))

    def process_calibration(self, save=True):
        """processes calibration control signal. Determines transfer function
        of speaker to get frequency vs. attenuation curve.

        :param save: Whether to save this calibration data to file
        :type save: bool
        :returns: numpy.ndarray, str, int, float -- frequency response (in dB), dataset name, calibration reference frequency, reference intensity
        """
        if not self.save_data:
            raise Exception("Cannot process an unsaved calibration")
            
        avg_signal = np.mean(self.datafile.get_data(self.current_dataset_name + '/signal'), axis=0)

        diffdB = attenuation_curve(self.stimulus.signal()[0], avg_signal,
                                        self.stimulus.samplerate(), self.calf)
        logger = logging.getLogger('main')
        logger.debug('The maximum dB attenuation is {}, caldB {}'.format(max(diffdB), self.caldb))

        # save a vector of only the calibration intensity results
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

        mean_reftone = np.mean(self.datafile.get_data(self.current_dataset_name + '/reference_tone'), axis=0)
        tone_amp = signal_amplitude(mean_reftone, self.player.get_aifs())
        db = calc_db(tone_amp, self.mphonesens, self.mphonedb)
        # remove the reference tone from protocol
        self.protocol_model.remove(0)
        
        return diffdB, self.current_dataset_name, self.calf, db

    def set_reps(self, reps):
        """set the number of repetitions for the stimuli (reference tone and cal stim)

        :param reps: number of times to present the same stimulus
        :type reps: int
        """
        self.stimulus.setRepCount(reps)
        self.refstim.setRepCount(reps)

    def count(self):
        return self.stimulus.repCount()


# whether to use relative peak level (from FFT), or calculate from
# microphone sensitivity level
USE_FFT = False

class CalibrationCurveRunner(AbstractCalibrationRunner):
    """Handles the presentaion of a 'traditional' style calibration
    curve. Loops over a set of tones of different frequencies and 
    intensities. Currently just used for testing"""
    def __init__(self, *args):
        super(CalibrationCurveRunner, self).__init__(*args)

        self.group_name = 'calibration_test_'

        self.player = FinitePlayer()

        self.stimulus = CCFactory.create()

        self.protocol_model.insert(self.stimulus, 0)

        # add in a tone at the calibration frequency and intensity
        control_stim = StimulusModel()
        self.control_tone = PureTone()
        control_stim.insertComponent(self.control_tone)
        self.protocol_model.insert(control_stim, 0)

        self.save_data = False

    # def set_save_params(self, folder=None, name=None):
    #     """Folder and filename where raw experiment data will be saved to

    #     :param savefolder: folder for experiment data
    #     :type savefolder: str
    #     :param samename: filename template, without extention for individal experiment files
    #     :type savename: str
    #     """
    #     if folder is not None:
    #         self.savefolder = folder
    #     if name is not None:
    #         self.savename = name

    def set_duration(self, dur):
        """See :meth:`AbstractCalibrationRunner<sparkle.run.calibration_runner.AbstractCalibrationRunner.set_duration>`"""
        self.stimulus.component(0,0).setDuration(dur)
        # self.stimulus.data(self.stimulus.index(0,0)).setDuration(dur)

    def _initialize_run(self):
        self.calibration_frequencies = []
        self.calibration_indexes = []

        if self.save_data:
            data_items = self.datafile.keys()
            self.current_dataset_name = next_str_num(self.group_name, data_items)

            self.datafile.init_group(self.current_dataset_name, mode='calibration')
            self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                    dims=(self.stimulus.traceCount(), self.stimulus.repCount(), self.aitimes.shape[0]))
            self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                    dims=(self.stimulus.traceCount(), self.stimulus.repCount()),
                                    nested_name='fft_peaks')
            self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                    dims=(self.stimulus.traceCount(), self.stimulus.repCount()),
                                    nested_name='vamp')

            info = {'samplerate_ad': self.player.aifs}
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
        f = trace_info['components'][0]['frequency'] #only the one component (PureTone)
        db = trace_info['components'][0]['intensity']
        # print 'f', f, 'db', db
        
        response = np.squeeze(response)
        assert len(response.shape) == 1, 'calibration only supported for single output channel'
        # target frequency amplitude
        freq, spectrum = calc_spectrum(response, self.player.get_aifs())
        peak_fft = spectrum[(np.abs(freq-f)).argmin()]

        # signal amplitude
        vamp = signal_amplitude(response, self.player.get_aifs())

        if self.trace_counter >= 0:
            if irep == 0:
                if db == self.caldb:
                    self.calibration_frequencies.append(f)
                    self.calibration_indexes.append(self.trace_counter)
                self.trace_counter +=1
                self.peak_avg = []

            if self.save_data:

                self.datafile.append(self.current_dataset_name, response)
                self.datafile.append(self.current_dataset_name, peak_fft, 
                                     nested_name='fft_peaks')
                self.datafile.append(self.current_dataset_name, np.array([vamp]), 
                                     nested_name='vamp')
                self.datafile.append_trace_info(self.current_dataset_name, trace_info)

            self.putnotify('calibration_response_collected', (spectrum, freq, vamp))

        # calculate resultant dB and emit
        if USE_FFT:
            self.peak_avg.append(peak_fft)
        else:
            self.peak_avg.append(vamp)
        if irep == self.nreps-1:
            mean_peak = np.mean(self.peak_avg)
            # print 'peak fft', mean_peak
            if self.trace_counter == -1:
                # this always is the first trace
                self.calpeak = mean_peak
                self.trace_counter +=1
            else:
                # use relative dB
                # resultdb = calc_db(mean_peak, self.calpeak) + self.caldb
                # dB according to microphone sensitivity
                resultdb = calc_db(mean_peak, self.mphonesens, self.mphonedb)
                self.putnotify('average_response', (f, db, resultdb))

    def process_calibration(self, save=False):
        """processes the data gathered in a calibration run (does not work if multiple
            calibrations), returns resultant dB"""
        
        if not self.save_data:
            raise Exception("Runner must be set to save when run, to be able to process")

        vfunc = np.vectorize(calc_db, self.mphonesens, self.mphonedb)

        if USE_FFT:
            peaks = np.mean(abs(self.datafile.get_data(self.current_dataset_name + '/fft_peaks')), axis=1)
        else:
            peaks = np.mean(abs(self.datafile.get_data(self.current_dataset_name + '/vamp')), axis=1)

        # print 'calibration frequencies', self.calibration_frequencies
        # cal_index = self.calibration_indexes[self.calibration_frequencies.index(self.calf)]
        # cal_peak = peaks[cal_index]
        # cal_vmax = vmaxes[cal_index]

        # print 'vfunc inputs', vmaxes, self.caldb, cal_vmax

        resultant_dB = vfunc(peaks, self.calpeak) * -1 #db attenuation

        print 'calibration frequences', self.calibration_frequencies, 'indexes', self.calibration_indexes
        print 'attenuations', resultant_dB

        calibration_vector = resultant_dB[self.calibration_indexes].squeeze()
        # Not currenly saving resultant intensity

        return resultant_dB, '', self.calf

    def set_reps(self, reps):
        """set the number of repetitions for the stimul(us/i)

        :param reps: number of times to present the same stimulus
        :type reps: int
        """
        self.stimulus.setRepCount(reps)

    def count(self):
        """Total number of all tests/traces/reps currently in this protocol

        :returns: int -- the total
        """
        total = 0
        for test in self.protocol_model.allTests():
            total += test.traceCount()*test.loopCount()*test.repCount()
        return total
