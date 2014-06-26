import numpy as np

from spikeylab.acq.players import FinitePlayer, ContinuousPlayer, MAXV
class TestDAQPlayers():
    def test_finite_acquisition_equal_dims(self):
        fs = 500000
        dur = 0.01
        stim, response0 = self.run_finite(fs, dur, fs, dur)

        # pyplot.plot(tone)
        # pyplot.plot(response0)
        # pyplot.show()

        amp = np.max(stim)
        tolerance = max(amp*0.1, 0.005) #noise floor
        assert np.allclose(stim, response0,rtol=0,atol=tolerance)

    def test_finite_acquisition_slower_out_fs(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs/4, dur)

        assert len(stim) == len(response0)/4
        assert np.round(np.amax(response0), 2) == np.amax(stim)

    def test_finite_acquisition_slower_in_fs(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs/4, dur, fs, dur)

        assert len(stim)/4 == len(response0)
        assert np.round(np.amax(response0), 2) == np.amax(stim)

    def test_finite_acquisition_short_out_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs, dur/4)

        assert len(stim) == len(response0)/4
        assert np.round(np.amax(response0), 2) == np.amax(stim)

    def test_finite_acquisition_out_slow_fs_and_short_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs/4, dur/2)

        assert len(stim) == len(response0)/4/2
        assert np.round(np.amax(response0), 2) == np.round(np.amax(stim), 2)

    def test_finite_acquisition_short_in_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur/2, fs, dur)

        assert len(stim)/2 == len(response0)
        assert np.round(np.amax(response0), 2) == np.amax(stim)

    def test_finite_acquisition_in_slow_fs_and_short_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs/4, dur/2, fs, dur)

        assert len(stim)/4/2 == len(response0)
        assert np.round(np.amax(response0), 2) == np.amax(stim)

    def test_stim_over_max_voltage(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs, dur, 11.0)

        assert len(stim) == len(response0)
        assert np.round(np.amax(response0), 2) == MAXV

    def test_continuous(self):
        player = ContinuousPlayer()
        fs = 500000
        dur = 0.2
        tone = data_func((fs*dur)/2, 5, 2.0)
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

    def run_finite(self, infs, indur, outfs, outdur, amp=2.0):
        player = FinitePlayer()

        tone = data_func(outfs*outdur, 5, amp)
        player.set_stim(tone, outfs)
        player.set_aidur(indur)
        player.set_aisr(infs)
        player.set_aichan(u"PCI-6259/ai0")
        player.set_aochan(u"PCI-6259/ao0")
        player.start()

        response0 = player.run()
        player.reset()
        response1 = player.run()
        player.stop()

        return tone, response0

    def stash_acq(self, databuffer):
        print 'stashing'
        self.single = databuffer
        self.data.extend(databuffer)

def data_func(nx, f, amp):
    x = np.arange(nx)
    return amp*np.sin(2*np.pi*f*x/len(x))

