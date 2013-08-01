import numpy as np
from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask, AOTask
from PyDAQmx.DAQmxConstants import DAQmx_Val_GroupByScanNumber
from PyDAQmx.DAQmxTypes import *
import time

glblist = []
DEBUG = False

def test_syncfinite():
    """
    Test basic operation of DAQ and drivers
    """

    #amps = [0.00002, 0.0001, 0.001, 0.01, 0.1, 1]
    amps = [0.01, 0.1, 1]
    frequency = 50000
    npts = 10000
    for amp in amps:
        aot = AOTaskFinite(b"PCI-6259/ao0", 1000000, npts, trigsrc=b"ai/StartTrigger")
        ait = AITaskFinite(b"PCI-6259/ai0", 1000000, npts)

        x = np.linspace(0,np.pi, npts)
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

        print(amp)       
        assert np.allclose(stim,response,rtol=0,atol=tolerance)

def test_sync_continuous():

    npts = 10000
    frequency = 50000
    amp = 2
    x = np.linspace(0,np.pi, npts)
    stim = amp * np.sin(frequency*x*2*np.pi)

    sr = 1000000
    aot = AOTask(b"PCI-6259/ao0", sr, npts, trigsrc=b"ai/StartTrigger")
    ait = AITask(b"PCI-6259/ai0", sr, npts)

    ait.register_callback(stashacq,npts)

    aot.write(stim)
    aot.start()
    ait.start()

    acqtime = 6 #seconds 
    time.sleep(acqtime)

    aot.stop()
    ait.stop()
    print('no. data points acquired: ', len(glblist))


    assert len(glblist) == acqtime*sr

def stashacq(task):
    r = c_int32()
    inbuffer = np.zeros(task.n)
    task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                       task.n,byref(r),None)
    glblist.extend(inbuffer.tolist())



