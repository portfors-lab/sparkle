from nose.tools import assert_equal

import test.sample as sample
from sparkle.stim.types import get_stimuli_models


class TestStimuliTypes():

    def setUp(self):
        stimuli_classes = get_stimuli_models()
        self.stimuli = []
        for stimclass in stimuli_classes:
            if stimclass.protocol:
                stimulus = stimclass()
                if stimulus.name == "Vocalization":
                    stimulus.setFile(sample.samplewav())
                self.stimuli.append(stimulus)

    def test_signal(self):
        fs = 375000
        atten = 20
        caldb = 100
        calv = 0.1
        for stimulus in self.stimuli:
            signal = stimulus.signal(fs=fs, atten=atten, caldb=caldb, calv=calv)
            print stimulus.name, signal[:20]
            assert signal is not None
            assert len(signal.shape) == 1

    def test_verify_stimulus(self):
        fs = 375000
        for stimulus in self.stimuli:
            msg = stimulus.verify(samplerate=fs)
            assert msg == 0

    def test_state_change(self):
        # test that the minimum states update
        mandatory_attrs = ['duration', 'intensity', 'risefall']
        for stimulus in self.stimuli:
            state = stimulus.stateDict()
            for attr in mandatory_attrs:
                assert attr in state
                state[attr] = 666
            stimulus.loadState(state)
            assert_equal(state, stimulus.stateDict())

    def test_serializable(self):
        for stimulus in self.stimuli:
            stream = stimulus.serialize()
            obj = stimulus.deserialize(stream)
            assert stream is not None
            assert obj is not None
