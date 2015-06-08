import unittest

import matplotlib.pyplot as plt
import numpy as np

from sparkle.acq.players import ContinuousPlayer, FinitePlayer

DEVNAME = "PCI-6259"

try:
    from PyDAQmx import *
except:
    from sparkle.acq.daqmx_stub import *

class TestDAQPlayers():
    def setUp(self):
        answer = bool32()
        err = DAQmxGetDevIsSimulated(DEVNAME, answer)
        self.devmode = answer.value

    def test_finite_acquisition_equal_dims(self):
        fs = 500000
        dur = 0.01
        stim, response0 = self.run_finite(fs, dur, fs, dur)

        # pyplot.plot(tone)
        # pyplot.plot(response0)
        # pyplot.show()

        amp = np.max(stim)
        tolerance = max(amp*0.1, 0.005) #noise floor
        assert stim.shape[-1] == response0.shape[-1]
        if not self.devmode:
            assert np.allclose(stim, response0, rtol=0, atol=tolerance)

    def test_finite_acquisition_slower_out_fs(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs/4, dur)

        assert stim.shape[-1] == response0.shape[-1]/4
        if not self.devmode:
            # assert np.round(np.amax(response0), 2) == np.amax(stim)
            pass

    def test_finite_acquisition_slower_in_fs(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs/4, dur, fs, dur)

        assert stim.shape[-1]/4 == response0.shape[-1]
        if not self.devmode:
            assert np.round(np.amax(response0), 1) == np.amax(stim)

    def test_finite_acquisition_short_out_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs, dur/4)

        assert stim.shape[-1] == response0.shape[-1]/4
        if not self.devmode:
            assert np.round(np.amax(response0), 1) == np.amax(stim)

    def test_finite_acquisition_out_slow_fs_and_short_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs/4, dur/2)

        assert stim.shape[-1] == response0.shape[-1]/4/2
        if not self.devmode:
            pass
            # assert np.round(np.amax(response0), 2) == np.round(np.amax(stim), 2)
        
    def test_finite_acquisition_short_in_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur/2, fs, dur)

        assert stim.shape[-1]/2 == response0.shape[-1]
        if not self.devmode:
            assert np.round(np.amax(response0), 1) == np.amax(stim)

    def test_finite_acquisition_in_slow_fs_and_short_duration(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs/4, dur/2, fs, dur)

        assert stim.shape[-1]/4/2 == response0.shape[-1]
        if not self.devmode:
            assert np.round(np.amax(response0), 2) == np.amax(stim)

    def test_finite_multichannel(self):
        fs = 500000
        dur = 0.01
        stim, response0 = self.run_finite(fs, dur, fs, dur, nchans=2)

        assert len(response0.shape) == 2
        assert stim.shape[-1] == response0.shape[-1]
        assert response0.shape[0] == 2

    @unittest.skip("No longer having acq module check out voltage")
    def test_stim_over_max_voltage(self):
        fs = 500000
        dur = 0.02
        stim, response0 = self.run_finite(fs, dur, fs, dur, 11.0)

        assert stim.shape[-1] == response0.shape[-1]
        if not self.devmode:
            assert np.round(np.amax(response0), 1) == MAXV

    def test_continuous(self):
        player = ContinuousPlayer()
        fs = 500000
        dur = 0.2
        tone = data_func((fs*dur)/2, 5, 2.0)
        player.set_stim(tone, fs)
        player.set_aidur(0.02)
        player.set_aifs(fs/4) 
        player.set_aochan(u"PCI-6259/ao2")   
        #start the acquisition
        self.data = []
        self.single = []
        player.set_read_function(self.stash_acq)
        player.start_continuous([u"PCI-6259/ai16",u"PCI-6259/ai1"])

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

    def run_finite(self, infs, indur, outfs, outdur, amp=2.0, nchans=1):
        player = FinitePlayer()

        tone = data_func(outfs*outdur, 5, amp)
        player.set_stim(tone, outfs)
        player.set_aidur(indur)
        player.set_aifs(infs)
        if nchans == 1:
            player.set_aichan(DEVNAME+"/ai16")
        else:
            chans = [DEVNAME+"/ai"+str(i) for i in range(nchans)]
            player.set_aichan(chans)
        player.set_aochan(DEVNAME+"/ao2")
        # player.start_timer(10)
        player.start()

        response0 = player.run()
        player.reset()
        response1 = player.run()
        player.stop()
        # player.stop_timer()

        return tone, response0

    def stash_acq(self, databuffer):
        print 'stashing'
        self.single = databuffer
        self.data.extend(databuffer)

def data_func(nx, f, amp):
    x = np.arange(nx)
    return amp*np.sin(2*np.pi*f*x/len(x))
