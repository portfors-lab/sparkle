import h5py
import os
import time
import numpy as np

from PyDAQmx.DAQmxConstants import DAQmx_Val_GroupByScanNumber
from PyDAQmx.DAQmxTypes import *

from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask, AOTask
from audiolab.io.structures import BigStore

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

class TestFileAcquire():
    """
    Test continuous acquisition into a HDF5 file
    """

    def setUp(self):

        fname = os.path.join(tempfolder,'savetemp.hdf5')
        self.testdata = BigStore(fname)

        npts = 1000
        frequency = 50000
        amp = 2
        x = np.linspace(0,np.pi, npts)
        self.stim = amp * np.sin(frequency*x*2*np.pi)
        
        self.sr = 1000000
        self.npts = npts

    def tearDown(self):
        # delete generated file
        fname = self.testdata.hdf5.filename
        self.testdata.close()
        os.remove(fname)

    def test_synchronous(self):
        
        self.aot = AOTask(b"PCI-6259/ao0", self.sr, self.npts, trigsrc=b"ai/StartTrigger")
        self.ait = AITask(b"PCI-6259/ai0", self.sr, self.npts)
        
        self.ait.register_callback(self.stashacq,self.npts)
        
        self.aot.write(self.stim)
        self.aot.start()
        self.ait.start()
        
        acqtime = 6 #seconds 
        time.sleep(acqtime)
        
        self.aot.stop()
        self.ait.stop()
        self.testdata.consolidate()
        print('no. data points acquired: ', self.testdata.shape(), ' desired ', self.sr*acqtime)

        assert self.testdata.shape() == (acqtime*self.sr,)

        
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


