import time
import unittest

import numpy as np

from sparkle.acq.daq_tasks import AITask, AITaskFinite, AOTask, AOTaskFinite, \
    DigitalOutTask, get_ai_chans, get_ao_chans, get_devices

try:
    from PyDAQmx import *
except:
    from sparkle.acq.daqmx_stub import *


DEBUG = False
DEVNAME = get_devices()[0]

class TestDAQTasks():
    def setup(self):
        self.data = []
        self.fs = 1000000 # 1000000 is max for PCI-6259

        answer = bool32()
        err = DAQmxGetDevIsSimulated(DEVNAME, answer)
        self.devmode = answer.value

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
            aot = AOTaskFinite(DEVNAME+"/ao2", self.fs, npts, trigsrc=u"ai/StartTrigger")
            ait = AITaskFinite(DEVNAME+"/ai16", self.fs, npts)

            stim = amp * np.sin(frequency*x*2*np.pi)

            aot.write(stim)

            aot.StartTask()
            ait.StartTask()

            response = ait.read()

            aot.stop()
            ait.stop()

            # squeeze single channel into single dimension
            response = np.squeeze(response)
            assert stim.shape == response.shape

            response = np.roll(response, -1)
            response[-1] = stim[-1] # free pass on last point

            if DEBUG:
                import matplotlib.pyplot as plt
                plt.plot(x, stim, x, response)
                plt.show()


            if not self.devmode:
                tolerance = max(amp*0.1, 0.005) #noise floor
                assert np.allclose(stim[10:],response[10:],rtol=0,atol=tolerance)
            
    def test_sync_continuous(self):

        npts = 10000
        frequency = 50000
        amp = 2
        x = np.linspace(0, np.pi, npts)
        stim = amp * np.sin(frequency*x*2*np.pi)

        aot = AOTask(DEVNAME+"/ao2", self.fs, npts, trigsrc=b"ai/StartTrigger")
        ait = AITask(DEVNAME+"/ai16", self.fs, npts)

        ait.register_callback(self.stashacq,npts)

        aot.write(stim)
        aot.start()
        ait.start()

        acqtime = 2 #seconds 
        time.sleep(acqtime)

        aot.stop()
        ait.stop()
        # print('no. data points acquired: ', len(self.data), 'expected', acqtime*self.fs)
        # print type(self.data[0])

        expected = acqtime*self.fs
        assert expected*0.85 <= len(self.data) <= expected*1.1

    def test_asynch_continuous_finite(self):
        ainpts = 1000

        ait = AITask(DEVNAME+"/ai16", self.fs, ainpts)
        ait.register_callback(self.stashacq, ainpts)
        ait.start()
        
        amps = [0.01, 0.1, 1]
        frequency = 50000
        aonpts = 10000
        x = np.linspace(0, np.pi, aonpts)
        for amp in amps:
            aot = AOTaskFinite(DEVNAME+"/ao2", self.fs, aonpts, trigsrc=u"")

            stim = amp * np.sin(frequency*x*2*np.pi)

            aot.write(stim)
            aot.StartTask()
            aot.wait()
            aot.stop()

        ait.stop()

        assert len(self.data) > aonpts*len(amps)

    def test_digital_output(self):
        dur = 1
        rate = 2
        dout = DigitalOutTask(DEVNAME+'/port0/line1', rate)
        dout.start()
        time.sleep(dur)
        # print 'samples generated', dout.generated()
        # this reading is haywire?
        # assert  dout.generated() == dur*rate
        dout.stop()
    
    @unittest.skip("Hardware needs to be connected")
    def test_triggered_AI(self):
        npts = 10000
        rate = 2.
        trigger = DigitalOutTask(DEVNAME+'/port0/line1', rate)
        ait = AITaskFinite(DEVNAME+"/ai16", self.fs, npts, trigsrc='/'+DEVNAME+'/PFI0')
        starttime = time.time()
        trigger.start()
        ait.StartTask()
        response0 = ait.read()
        ait.StopTask()
        ait.start()
        # ait = AITaskFinite(DEVNAME+"/ai16", self.fs, npts, trigsrc='/'+DEVNAME+'/PFI0')
        response1 = ait.read()
        duration = time.time() - starttime
        trigger.stop()
        ait.stop()

        # print "response shape", response1.shape
        # print "duration", duration
        assert len(response1) == npts

    @unittest.skip("Hardware needs to be connected")
    def test_triggered_and_sync_AI_AO(self):
        npts = 10000
        rate = 2.
        trigger = DigitalOutTask(DEVNAME+'/port0/line1', rate)
        ait = AITaskFinite(DEVNAME+"/ai16", self.fs, npts, trigsrc='/'+DEVNAME+'/PFI0')
        aot = AOTaskFinite(DEVNAME+"/ao2", self.fs, npts, trigsrc=u"ai/StartTrigger")
        
        frequency = 5
        x = np.linspace(0,np.pi, npts)
        stim = np.sin(frequency*x*2*np.pi)
        aot.write(stim)

        starttime = time.time()
        trigger.start()
        # aot.StartTask()
        ait.StartTask()
        response0 = ait.read()

        aot.StopTask()
        ait.StopTask()
        aot.StartTask()
        ait.start()
        # ait = AITaskFinite(DEVNAME+"/ai16", self.fs, npts, trigsrc='/'+DEVNAME+'/PFI0')
        response1 = ait.read()
        duration = time.time() - starttime

        trigger.stop()
        ait.stop()
        aot.stop() 

        # print "response shape", response1.shape
        # print "duration", duration
        assert len(response1) == npts

    def test_multichannel_acq(self):
        npts = 10000
        fs = 10000
        ait = AITaskFinite([DEVNAME+"/ai16", DEVNAME+"/ai17"], fs, npts)
        ait.StartTask()
        response = ait.read()
        ait.stop()

        assert response.shape == (2, npts)

    def stashacq(self, data):
        self.data.extend(data.tolist())

def test_get_ao_chans():
    chans = get_ao_chans(DEVNAME)
    assert len(chans) == 4

def test_get_ai_chans():
    chans = get_ai_chans(DEVNAME)
    assert len(chans) == 32
