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


class TestFileAcquire():
    """
    Test continuous acquisition into a HDF5 file
    """

    def setUp(self):
        print('setup')
        fname = os.path.join(tempfolder,'savetemp.hdf5')
        #self.testdata = BigStore(fname, chunksize=2**24)

        npts = 10000
        frequency = 5000
        amp = 2
        x = np.linspace(0,np.pi, npts)
        self.stim = amp * np.sin(frequency*x*2*np.pi)
        self.t = x        

        self.sr = 400000
        self.npts = npts

        self.aot = AOTask(b"PCI-6259/ao0", self.sr, self.npts, trigsrc=b"ai/StartTrigger")
        self.ait = AITask(b"PCI-6259/ai0", self.sr, self.npts)
        
        self.aot.write(self.stim)

        
    def tearDown(self):
        # delete generated file
        fname = self.testdata.hdf5.filename
        #self.testdata.close()
        #os.remove(fname)

    def test_synch_with_chaco_plot(self):

        app = QApplication(['sometext'])
        self.fig = LiveWindow(2)
        self.fig.show()
        self.fig.draw_line(0, 0, self.t, self.stim)
        QApplication.processEvents()

        self.signals = TestSignals()
        self.signals.update_data.connect(self.update_display)

        self.ait.register_callback(self.stashacq_plot,self.npts)
        
        self.aot.start()
        self.ait.start()
        
        acqtime = 6 #seconds 
        #time.sleep(acqtime)
        raw_input("Press enter to stop")

        self.aot.stop()
        self.ait.stop()
        self.testdata.consolidate()
        print('no. data points acquired: ', self.testdata.shape(), ' desired ', self.sr*acqtime)

        assert self.testdata.shape() == (acqtime*self.sr,)
        
        #self.fig.close()

    def stashacq_plot(self,task):
        try:
            r = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                               task.n,byref(r),None)
            #self.testdata.append(inbuffer.tolist())
            
            self.signals.update_data.emit(self.t, inbuffer)
            return

        except:
            self.aot.stop()
            self.ait.stop()
            raise

    def update_display(self, xdata, ydata):
        self.fig.draw_line(1, 0, xdata, ydata)
        QApplication.processEvents()

def xtest_sync_finite_chaco():

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