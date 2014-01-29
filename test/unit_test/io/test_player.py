import numpy as np
# import matplotlib.pyplot as plt

from spikeylab.io.players import FinitePlayer, ContinuousPlayer
class TestDAQPlayers():
    def test_finite_acquisition_equal_dims(self):
        player = FinitePlayer()
        fs = 500000
        dur = 0.01
        tone = data_func(fs*dur, 5)
        player.set_stim(tone, fs)
        player.set_aidur(0.01)
        player.set_aisr(fs)
        player.set_aichan(u"PCI-6259/ai0")
        player.set_aochan(u"PCI-6259/ao0")
        player.start()

        response0 = player.run()
        player.reset()
        response1 = player.run()
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
        tone = data_func((fs*dur)/2, 5)
        player.set_stim(tone, fs)
        player.set_aidur(0.02)
        player.set_aisr(fs/4)
        player.set_aichan(u"PCI-6259/ai0")
        player.set_aochan(u"PCI-6259/ao0")
        player.start()

        response0 = player.run()
        player.reset()
        response1 = player.run()
        player.stop()

        # Just make sure doesn't throw error then?

    def test_continuous(self):
        player = ContinuousPlayer()
        fs = 500000
        dur = 0.2
        tone = data_func((fs*dur)/2, 5)
        player.set_stim(tone, fs)
        player.set_aidur(0.02)
        player.set_aisr(fs/4) 
        player.set_aochan(u"PCI-6259/ao0")   
        #start the acquisition
        self.data = []
        self.single = []
        player.set_read_function(self.stash_acq)
        player.start_continuous([u"PCI-6259/ai0",u"PCI-6259/ai1"])

        # now start a generation
        player.reset()
        player.run()

        player.stop_all()
        nstims = player.generation_count()

        # print 'data shape', self.single.shape
        # plt.plot(self.single.T)
        # plt.show()

        assert nstims == 1
        assert len(self.data) > 1

    def stash_acq(self, databuffer):
        print 'stashing'
        self.single = databuffer
        self.data.extend(databuffer)

def data_func(nx, f):
    x = np.arange(nx)
    return 2*np.sin(2*np.pi*f*x/len(x))

