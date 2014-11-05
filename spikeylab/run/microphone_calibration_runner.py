import numpy as np

from spikeylab.run.list_runner import ListAcquisitionRunner
from spikeylab.tools.audiotools import rms
from spikeylab.stim.stimulus_model import StimulusModel
from spikeylab.stim.types.stimuli_classes import Silence
from spikeylab.acq.players import FinitePlayer

class MphoneCalibrationRunner(ListAcquisitionRunner):
    """
    No stimulus out, simply reads in the microphone and returns
    the average RMS, which will be used as the microphone sensitivity
    variable in dB SPL calculations elsewhere
    """
    def __init__(self, *args):
        ListAcquisitionRunner.__init__(self, *args)

        self.save_data = False
        self.silence_window = False
        self.player = FinitePlayer()

        # acquistiion without a stimulus is not allowed, so use silence
        stim = StimulusModel()
        stim.setRepCount(5)
        stim.insertComponent(Silence())
        self.protocol_model.insert(stim,0)

    def _initialize_run(self):
        self.player.set_aochan(self.aochan)
        self.player.set_aichan(self.aichan)

    def _initialize_test(self, test):        
        recording_length = self.aitimes.shape[0]
        self.response_buffer = np.zeros((test.repCount(), recording_length))

    def _process_response(self, response, trace_info, irep):
        self.response_buffer[irep,:] = response
        self.putnotify('response_collected', (self.aitimes, response))

    def process_calibration(self):
        mean_response = np.mean(self.response_buffer,0)
        amp = rms(mean_response, self.player.aisr)

        return amp