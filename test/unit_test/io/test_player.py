import numpy as np

from spikeylab.io.players import FinitePlayer, ContinuousPlayer
class TestDAQPlayers():
    def test_finite_acquisition_equal_dims(self):
        player = FinitePlayer()
        fs = 500000
        dur = 0.01
        x = np.arange(fs*dur)
        tone = data_func(x, 5)
        player.set_stim(tone, fs)
        player.set_aidur(0.01)
        player.set_aisr(fs)
        player.start(u"PCI-6259/ao0",u"PCI-6259/ai0")

        response0 = player.read()
        player.reset()
        response1 = player.read()
        player.stop()

        # pyplot.plot(tone)
        # pyplot.plot(response0)
        # pyplot.show()

        amp = np.max(tone)
        tolerance = max(amp*0.1, 0.005) #noise floor
        assert np.allclose(tone, response0,rtol=0,atol=tolerance)

    def test_finite_acquisition_unequal_dims(self):
        player = FinitePlayer()
        fs = 500000
        dur = 0.02
        x = np.arange((fs*dur)/2)
        tone = data_func(x, 5)
        player.set_stim(tone, fs)
        player.set_aidur(0.02)
        player.set_aisr(fs/4)
        player.start(u"PCI-6259/ao0",u"PCI-6259/ai0")

        response0 = player.read()
        player.reset()
        response1 = player.read()
        player.stop()

        # Just make sure doesn't throw error then?

    def test_continuous(self):
        player = ContinuousPlayer()
        fs = 500000
        dur = 0.2
        x = np.arange((fs*dur)/2)
        tone = data_func(x, 5)
        player.set_stim(tone, fs)
        player.set_aidur(0.02)
        player.set_aisr(fs/4) 
        player.set_aochan(u"PCI-6259/ao0")   
        #start the acquisition
        self.data = []
        player.set_read_function(self.stash_acq)
        player.start(u"PCI-6259/ai0")

        # now start a generation
        player.reset()
        player.generate()

        player.stop()
        nstims = player.generation_count()

        assert nstims == 1
        assert len(self.data) > 1

    def stash_acq(self, databuffer):
        self.data.extend(databuffer)

def data_func(x, f):
    return 2*np.sin(2*np.pi*f*x/len(x))

