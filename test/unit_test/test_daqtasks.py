import numpy as np
from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite

def test_syncfinite():
    u"""
    Test basic operation of DAQ and drivers
    """

    amps = [0.00002, 0.0001, 0.001, 0.01, 0.1, 1]
    #amps = [0.01, 0.1, 1]
    frequency = 50000
    npts = 10000
    for amp in amps:
        aot = AOTaskFinite(u"PCI-6259/ao0", 1000000, npts, trigsrc=u"ai/StartTrigger")
        ait = AITaskFinite(u"PCI-6259/ai0", 1000000, npts)

        x = np.linspace(0,np.pi, npts)
        stim = amp * np.sin(frequency*x*2*np.pi)

        aot.write(stim)

        aot.StartTask()
        ait.StartTask()

        response = ait.read()

        aot.stop()
        ait.stop()

        tolerance = 0.005 #noise floor

        assert np.allclose(stim,response,rtol=0,atol=tolerance)

