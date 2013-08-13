from audiolab.plotting.chacoplots import LiveWindow

import h5py
import os
import time
import numpy as np

from PyDAQmx.DAQmxConstants import DAQmx_Val_GroupByScanNumber
from PyDAQmx.DAQmxTypes import *

from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask, AOTask
from audiolab.io.structures import BigStore
from audiolab.calibration.qthreading import TestSignals

from PyQt4.QtGui import QApplication

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")



def test_sync_finite_chaco():

    fname = os.path.join(tempfolder,'savetemp.hdf5')
    testdata = BigStore(fname, chunksize=2**24)

    app = QApplication(['sometext'])
    fig = LiveWindow(2)
    fig.show()

    amp = 2
    frequencies = [1, 3, 10, 50000]
    npts = 100000
    sr = 1000000
    for frequency in frequencies:
        aot = AOTaskFinite(u"PCI-6259/ao0", sr, npts, trigsrc=u"ai/StartTrigger")
        ait = AITaskFinite(u"PCI-6259/ai0", sr, npts)

        x = np.linspace(0,np.pi, npts)
        stim = amp * np.sin(frequency*x*2*np.pi)

        aot.write(stim)

        aot.StartTask()
        ait.StartTask()

        response = ait.read()

        fig.draw_line(1, 0, x, response)

        aot.stop()
        ait.stop()

        QApplication.processEvents()

        testdata.append(response)
        #time.sleep(1)

    fig.close()
    testdata.close()
    os.remove(fname)