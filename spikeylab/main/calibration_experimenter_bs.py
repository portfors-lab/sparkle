import os
import logging
import numpy as np

from spikeylab.tools.util import create_unique_path
from spikeylab.main.protocol_acquisition import Experimenter
from spikeylab.stim.types.stimuli_classes import WhiteNoise, FMSweep
from spikeylab.tools.audiotools import smooth
from spikeylab.io.players import FinitePlayer
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.data.dataobjects import AcquisitionData

import matplotlib.pyplot as plt

class CalibrationExperimenterBS(Experimenter):
    def __init__(self, signals):
        Experimenter.__init__(self, signals)

        self.savefolder = None
        self.savename = 'calibration'

        self.player = FinitePlayer()

        self.stimulus = StimulusModel()
        # # insert stim component... either noise or chirp
        self.stim_components = [WhiteNoise(), FMSweep()]
        self.stimulus.insertComponent(self.stim_components[0])
        self.protocol_model.insertNewTest(self.stimulus, 0)

        save_data = True
        self.group_name = 'group_0'

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

    def stash_calibration(self, attenuations, freqs, frange):
        self.calibration_vector = attenuations
        self.calibration_freqs = freqs
        self.calibration_frange = frange

    def apply_calibration(self, apply_cal):
        self.apply_cal = apply_cal

    def set_duration(self, dur):
        # self.stimulus.data(self.stimulus.index(0,0)).setDuration(dur)
        # this may be set at any time, and is not checked before run, so set
        # all stim components
        print 'setting duration', dur
        for comp in self.stim_components:
            comp.setDuration(dur)

    def set_reps(self, reps):
        self.stimulus.setRepCount(reps)

    def _initialize_run(self):
        self.current_dataset_name = 'calibration'
       
        self.stimulus.data(self.stimulus.index(0,0)).setIntensity(self.caldb)

        print 'using stimulus', self.stimulus.data(self.stimulus.index(0,0)).name

        if self.savefolder is None or self.savename is None:
            print "You must first set a save folder and filename"
        fname = create_unique_path(self.savefolder, self.savename)
        logger = logging.getLogger('main')
        logger.info('calibration file name %s' % fname)

        self.datafile = AcquisitionData(fname)
        self.datafile.init_group(self.current_dataset_name)
        self.datafile.init_data(self.current_dataset_name, mode='calibration',
                                dims=(self.stimulus.repCount(), self.stimulus.duration()*self.stimulus.samplerate()),
                                nested_name='signal')

        info = {'samplerate_ad': self.player.aisr}
        self.datafile.set_metadata('', info)

        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

        if self.apply_cal:
            self.protocol_model.setCalibration(self.calibration_vector, self.calibration_freqs, self.calibration_frange)
        else:
            self.protocol_model.setCalibration(None, None, None)

    def _initialize_test(self, test):
        return

    def _process_response(self, response, trace_info, irep):
        self.datafile.append(self.current_dataset_name, response, 
                             nested_name='signal')

        self.signals.response_collected.emit(self.aitimes, response)
        
    def process_calibration(self, save=True):
        """processes calibration control signal. Determines transfer function
        of speaker to get frequency vs. attenuation curve."""
        print 'process the calibration'
        dataset_name = 'calibration'
        avg_signal = np.mean(self.datafile.get('signal'), axis=0)
        # remove dc offset
        avg_signal = avg_signal - np.mean(avg_signal)

        y = avg_signal
        x = self.stimulus.signal()[0]

        Y = np.fft.rfft(y)
        X = np.fft.rfft(x)

        Ymag = np.sqrt(Y.real**2 + Y.imag**2)
        Xmag = np.sqrt(X.real**2 + X.imag**2)

        # convert to decibel scale
        YmagdB = 20 * np.log10(Ymag)
        XmagdB = 20 * np.log10(Xmag)

        # now we can substract to get attenuation curve
        diffdB = XmagdB - YmagdB

        # may want to smooth results here?
        # diffdB = smooth(diffdB)

        # frequencies present in calibration spectrum
        npts = len(y)
        fq = np.arange(npts/2+1)/(float(npts)/self.stimulus.samplerate())

        # shift by the given calibration frequency to align attenutation
        # with reference point set by user
        diffdB -= diffdB[fq == self.calf]

        # save a vector of only the calibration intensity results
        fname = self.datafile.filename
        if save:
            self.datafile.init_data(dataset_name, mode='calibration',
                                    dims=diffdB.shape,
                                    nested_name='calibration_intensities')
            self.datafile.append(dataset_name, diffdB,
                                 nested_name='calibration_intensities')

            relevant_info = {'frequencies': 'all', 'calibration_dB':self.caldb,
                             'calibration_voltage': self.calv, 'calibration_frequency': self.calf,
                             }
            self.datafile.set_metadata('calibration_intensities',
                                       relevant_info)
            self.datafile.close()
            self.signals.calibration_file_changed.emit(fname)
            print 'finished calibration :)'
        else:
            # delete the data saved to file thus far.
            self.datafile.close()
            os.remove(fname)
            print 'calibration not saved'
        return diffdB, fname, self.calf
