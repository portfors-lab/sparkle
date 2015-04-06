import numpy as np

from sparkle.acq.players import FinitePlayer
from sparkle.run.list_runner import ListAcquisitionRunner
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import Silence
from sparkle.tools.audiotools import signal_amplitude


class MphoneCalibrationRunner(ListAcquisitionRunner):
    """
    No stimulus out, simply reads in the microphone and returns
    the average RMS, which will be used as the microphone sensitivity
    variable in dB SPL calculations elsewhere
    """
    _reps = 5
    def __init__(self, *args):
        super(MphoneCalibrationRunner, self).__init__(*args)

        self.save_data = False
        self.silence_window = False
        self.player = FinitePlayer()

        # acquistiion without a stimulus is not allowed, so use silence
        stim = StimulusModel()
        stim.setRepCount(self._reps)
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

    def process_calibration(self):
        amps = []
        for itest in range(self.response_buffer.shape[0]):
            amps.append(signal_amplitude(self.response_buffer[itest,:], self.player.aifs))
        amp = np.mean(amps)
        return amp

    def reps(self):
        return self._reps
