import numpy as np
from spikeylab.acq.daq_tasks import AITaskFinite, AOTaskFinite, AITask, AOTask, \
                                    get_ao_chans, get_ai_chans
try:
    from PyDAQmx import *
    skip = False
except:
    skip = True

import time
import unittest

DEBUG = False

class TestDAQTasks():
    def setup(self):
        self.data = []
        self.sr = 1000000 # 1000000 is max for PCI-6259

    @unittest.skipIf(skip, 'No IO tests for dev mode')
    def test_sync_finite(self):
        u"""
        Test basic operation of DAQ and drivers
        """

        #amps = [0.00002, 0.0001, 0.001, 0.01, 0.1, 1]
        amps = [0.01, 0.1, 1]
        frequency = 5#0000
        npts = 10000
        x = np.linspace(0,np.pi, npts)
        for amp in amps:
            aot = AOTaskFinite(u"PCI-6259/ao0", self.sr, npts, trigsrc=u"ai/StartTrigger")
            ait = AITaskFinite(u"PCI-6259/ai0", self.sr, npts)

            stim = amp * np.sin(frequency*x*2*np.pi)

            aot.write(stim)

            aot.StartTask()
            ait.StartTask()

            response = ait.read()

            aot.stop()
            ait.stop()

            response = np.roll(response, -1)
            response[-1] = stim[-1] # free pass on first point
            if DEBUG:
                import matplotlib.pyplot as plt
                plt.plot(x, stim, x, response)
                plt.show()

            tolerance = max(amp*0.1, 0.005) #noise floor

            assert np.allclose(stim[10:],response[10:],rtol=0,atol=tolerance)
            
    @unittest.skipIf(skip, 'No IO tests for dev mode')
    def test_sync_continuous(self):

        npts = 10000
        frequency = 50000
        amp = 2
        x = np.linspace(0, np.pi, npts)
        stim = amp * np.sin(frequency*x*2*np.pi)

        aot = AOTask(b"PCI-6259/ao0", self.sr, npts, trigsrc=b"ai/StartTrigger")
        ait = AITask(b"PCI-6259/ai0", self.sr, npts)

        ait.register_callback(self.stashacq,npts)

        aot.write(stim)
        aot.start()
        ait.start()

        acqtime = 2 #seconds 
        time.sleep(acqtime)

        aot.stop()
        ait.stop()
        print('no. data points acquired: ', len(self.data), 'expected', acqtime*self.sr)
        print type(self.data[0])

        expected = acqtime*self.sr
        assert expected*0.9 <= len(self.data) <= expected*1.1

    @unittest.skipIf(skip, 'No IO tests for dev mode')
    def test_asynch_continuous_finite(self):
        ainpts = 1000

        ait = AITask(u"PCI-6259/ai0", self.sr, ainpts)
        ait.register_callback(self.stashacq, ainpts)
        ait.start()
        
        amps = [0.01, 0.1, 1]
        frequency = 50000
        aonpts = 10000
        x = np.linspace(0, np.pi, aonpts)
        for amp in amps:
            aot = AOTaskFinite(u"PCI-6259/ao0", self.sr, aonpts, trigsrc=u"")

            stim = amp * np.sin(frequency*x*2*np.pi)

            aot.write(stim)
            aot.StartTask()
            aot.wait()
            aot.stop()

        ait.stop()

        assert len(self.data) > aonpts*len(amps)

    def stashacq(self, data):
        self.data.extend(data.tolist())

@unittest.skipIf(skip, 'No IO tests for dev mode')
def test_get_ao_chans():
    chans = get_ao_chans("PCI-6259")
    assert len(chans) == 4

@unittest.skipIf(skip, 'No IO tests for dev mode')
def test_get_ai_chans():
    chans = get_ai_chans("PCI-6259")
    assert len(chans) == 32