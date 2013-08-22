#from __future__ import division

import h5py
import os
import time
import numpy as np
import threading, Queue

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4.QtGui import QApplication
from PyQt4 import QtCore

from PyDAQmx.DAQmxConstants import DAQmx_Val_GroupByScanNumber
from PyDAQmx.DAQmxTypes import *

from audiolab.plotting.chacoplots import LiveWindow
from audiolab.io.daq_tasks import AITaskFinite, AOTaskFinite, AITask, AOTask
from audiolab.io.structures import BigStore
from audiolab.plotting.plotz import AnimatedWindow, ScrollingPlot
from audiolab.tools.qthreading import TestSignals, GenericThread

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

class TestFileAcquire():
    """
    Test continuous acquisition into a HDF5 file
    """
    def setUp(self):
        fname = os.path.join(tempfolder,'savetemp.hdf5')
        self.testdata = BigStore(fname, chunksize=2**24)

        npts = 10000
        frequency = 5
        amp = 2
        x = np.linspace(0, np.pi, npts)
        self.stim = amp * np.sin(frequency*x*2*np.pi)

        self.t = x        

        self.sr = 200000
        self.npts = npts

        #keep the generation and acq same duration
        sr_out = 200000
        npts_out = npts*(sr_out/self.sr) 
        #print(npts_out)
        #print "durations", float(npts)/self.sr, float(npts_out)/sr_out

        self.aot = AOTask(b"PCI-6259/ao0", sr_out, npts_out, 
                            trigsrc=b"ai/StartTrigger")
        self.ait = AITask(b"PCI-6259/ai0", self.sr, self.npts)
        #print "stim max", max(abs(self.stim))
        self.aot.write(self.stim)

        self.app = QApplication(['sometext'])

        self.signals = TestSignals()
        self.signals.done.connect(self.app.quit)

    def tearDown(self):
        # delete generated file
        fname = self.testdata.hdf5.filename
        self.testdata.close()
        os.remove(fname)

    def test_synchronous(self):
        """
        Test acquitision, storing data, without plot display
        """

        self.ait.register_callback(self.stashacq,self.npts)
        self.fig = None

        self.administert()

    def test_synch_with_mpl(self):
        """
        Test acquisition, storing data, with matplotlib display
        """

        self.fig = AnimatedWindow(([],[]), ([],[]))
        self.fig.show()
        self.fig.draw_line(0, 0, self.t, self.stim)
        #self.fig.axs[1].set_xlim(0,1)

        self.ait.register_callback(self.stashacq_plot, self.npts)

        self.signals.update_data.connect(self.update_display)

        self.administert()

    def xtest_synch_with_scrollplot(self):
        self.fig = ScrollingPlot(1, 1/self.sr)
        self.fig.show()

        self.ait.register_callback(self.stashacq_plotscroll,self.npts)
        
        self.administert()

    def test_synch_with_chaco(self):

        self.fig = LiveWindow(2)
        self.fig.show()
        self.fig.draw_line(0, 0, self.t, self.stim)
        QApplication.processEvents()

        self.ait.register_callback(self.stashacq_plot,self.npts)

        self.signals.update_data.connect(self.update_display)
        
        self.administert()

    def administert(self):
        q = Queue.Queue()
        task = threading.Thread(target=self.doacquitision, args=(q,))
        # self.task = GenericThread(self.doacquitision, (q,))
        # self.app.connect(self.task, QtCore.SIGNAL("update_data"), self.update_display)
        task.start()

        # non-blocking wait for acq to finish, and signal quit
        self.app.exec_()

        result = q.get()

        if self.fig is not None:
            self.fig.close()

        self.testdata.consolidate()

        print 'no. data points acquired: ', self.testdata.shape(), ' desired ', result
        assert self.testdata.shape() == result

    def doacquitision(self,q=None):
        self.aot.start()
        self.ait.start()
        
        acqtime = 3 #seconds 
        time.sleep(acqtime)
        
        self.aot.stop()
        self.ait.stop()

        # print('no. data points acquired: ', self.testdata.shape(), ' desired ', self.sr*acqtime)

        q.put((acqtime*self.sr,))
        
        self.signals .done.emit()


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
            self.signals.update_data.emit(self.t, inbuffer)

        except:
            self.aot.stop()
            self.ait.stop()
            raise

    def stashacq_plotscroll(self,task):
        try:
            r = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                               task.n,byref(r),None)
            self.testdata.append(inbuffer.tolist())
            self.fig.append(inbuffer)
            QApplication.processEvents()

        except:
            self.aot.stop()
            self.ait.stop()
            raise


    def update_display(self, xdata=[0], ydata=[0]):
        # print "update display!"
        self.testdata.append(ydata.tolist())
        self.fig.draw_line(1, 0, xdata, ydata)
        QApplication.processEvents()