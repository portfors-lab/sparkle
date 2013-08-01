import h5py
import os
import time
import numpy as np
from PyQt4 import QtCore, QtGui

from PyDAQmx.DAQmxConstants import DAQmx_Val_GroupByScanNumber
from PyDAQmx.DAQmxTypes import *

from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask, AOTask
from audiolab.io.structures import BigStore
from audiolab.plotting.plotz import AnimatedWindow

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

class TestFileAcquire():
    """
    Test continuous acquisition into a HDF5 file
    """

    def setUp(self):
        print('setup')
        fname = os.path.join(tempfolder,'savetemp.hdf5')
        self.testdata = BigStore(fname, chunksize=2**24)

        npts = 1000
        frequency = 50000
        amp = 2
        x = np.linspace(0,np.pi, npts)
        self.stim = amp * np.sin(frequency*x*2*np.pi)
        self.t = x        

        self.sr = 1000000
        self.npts = npts

        self.aot = AOTask(b"PCI-6259/ao0", self.sr, self.npts, trigsrc=b"ai/StartTrigger")
        self.ait = AITask(b"PCI-6259/ai0", self.sr, self.npts)
        
        self.aot.write(self.stim)

    def tearDown(self):
        # delete generated file
        fname = self.testdata.hdf5.filename
        self.testdata.close()
        os.remove(fname)

    def test_synchronous(self):

        self.ait.register_callback(self.stashacq,self.npts)

        self.aot.start()
        self.ait.start()
        
        acqtime = 6 #seconds 
        time.sleep(acqtime)
        
        self.aot.stop()
        self.ait.stop()
        self.testdata.consolidate()
        print('no. data points acquired: ', self.testdata.shape(), ' desired ', self.sr*acqtime)

        assert self.testdata.shape() == (acqtime*self.sr,)

    def test_synch_with_plot(self):

        app = QtGui.QApplication(['sometext'])
        self.fig = AnimatedWindow(([],[]), ([],[]))
        self.fig.show()
        self.fig.draw_line(0, 0, self.t, self.stim)
        #self.fig.axs[1].set_xlim(0,1)

        self.ait.register_callback(self.stashacq_plot,self.npts)
        
        self.aot.start()
        self.ait.start()
        
        acqtime = 6 #seconds 
        time.sleep(acqtime)
        
        self.aot.stop()
        self.ait.stop()
        self.testdata.consolidate()
        print('no. data points acquired: ', self.testdata.shape(), ' desired ', self.sr*acqtime)

        assert self.testdata.shape() == (acqtime*self.sr,)
        
        self.fig.close()

    def stashacq(self,task):
        try:
            r = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                               task.n,byref(r),None)
            self.testdata.append(inbuffer.tolist())
        except:
            self.aot.stop()
            self.ait.stop()
            raise

    def stashacq_plot(self,task):
        try:
            r = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                               task.n,byref(r),None)
            self.testdata.append(inbuffer.tolist())
            self.fig.draw_line(1,0, self.t, inbuffer)

        except:
            self.aot.stop()
            self.ait.stop()
            raise
