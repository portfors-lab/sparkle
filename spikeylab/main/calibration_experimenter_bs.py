import logging
import numpy as np

from spikeylab.main.protocol_acquisition import Experimenter
from spikeylab.stim.types.stimuli_classes import WhiteNoise, FMSweep
from spikeylab.tools.audiotools import attenuation_curve
from spikeylab.acq.players import FinitePlayer
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.tools.util import next_str_num

class CalibrationExperimenterBS(Experimenter):
    def __init__(self, signals):
        Experimenter.__init__(self, signals)

        self.player = FinitePlayer()

        self.stimulus = StimulusModel()
        # # insert stim component... either noise or chirp
        self.stim_components = [WhiteNoise(), FMSweep()]
        self.stimulus.insertComponent(self.stim_components[0])
        self.protocol_model.insertNewTest(self.stimulus, 0)

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
        
        print 'initialize data signal size', self.stimulus.duration(), self.stimulus.samplerate(), (self.stimulus.repCount(), self.stimulus.duration()*self.stimulus.samplerate())
        self.datafile.init_data(self.current_dataset_name, mode='calibration', 
                                dims=(self.stimulus.repCount(), self.stimulus.duration()*self.stimulus.samplerate()),
                                nested_name='signal')

        info = {'samplerate_ad': self.player.aisr}
        self.datafile.set_metadata(self.current_dataset_name, info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        if self.apply_cal:
            self.protocol_model.setCalibration(self.calibration_vector, self.calibration_freqs, self.calibration_frange)
        else:
            self.stimulus.data(self.stimulus.index(0,0)).setIntensity(self.caldb)
            self.calname = None
            self.protocol_model.setCalibration(None, None, None)

    def _initialize_test(self, test):
        return

    def _process_response(self, response, trace_info, irep):
        print 'size of response:', response.shape
        self.datafile.append(self.current_dataset_name, response, 
                             nested_name='signal')

        self.signals.response_collected.emit(self.aitimes, response)
        
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
