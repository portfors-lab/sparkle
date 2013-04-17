import sys, os

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np

from fg_form import Ui_fgform
from daq_tasks import AOTask,AITask

class FGenerator(QtGui.QMainWindow):
    def __init__(self, parent=None):
        #auto generated code intialization
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_fgform()
        self.ui.setupUi(self)

        #manual costumization
        cnames = get_ao_chans(b"Dev1")
        self.ui.aochan_box.addItems(cnames)
        self.ui.start_button.clicked.connect(self.start_gen)
        self.ui.stop_button.clicked.connect(self.stop_gen)

    def start_gen(self):
        sr = int(self.ui.sr_edit.text())
        npts = int(self.ui.npts_edit.text())
        amp = int(self.ui.amp_edit.text())
        freq = int(self.ui.freq_edit.text())
        aochan = self.ui.aochan_box.currentText().encode()
        
        self.ui.outplot.axes.set_xlim(0,npts)
        self.ui.outplot.axes.set_ylim(-amp,amp)
        self.ui.inplot.axes.set_xlim(0,npts)
        self.ui.inplot.axes.set_ylim(-amp,amp)

        #in/out data
        outdata = amp * np.sin(freq * np.linspace(0, 2*np.pi, npts))
        self.indata = []
        self.npts = npts

        #plot data we intend to generate
        self.ui.outplot.axes.plot(range(len(outdata)),outdata)
        self.inplot, = self.ui.inplot.axes.plot([],[])

        self.ui.outplot.draw()
        self.ui.inplot.draw()
        QtGui.QApplication.processEvents()

        try:
            self.ai = AITask(b"Dev1/ai0",sr,npts)
            self.ao = AOTask(aochan,sr,npts)
            self.ao.write(outdata)
            #tight coupling --FIXME
            #self.ai.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,100,0,name='every_n_callback')
            self.ai.register_callback(self.every_n_callback,self.npts)
            self.ao.start()
            self.ai.StartTask()
        except:
            print('ERROR! TERMINATE!')
            self.ai.stop()
            self.ao.stop()
            raise

    def every_n_callback(self,task):
        #print("booya you watery tart")
        r = c_int32()
        inbuffer = np.zeros(self.npts)
        task.ReadAnalogF64(self.npts,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                           self.npts,byref(r),None)
        #store data in a numpy array where columns are trace sweeps
        self.indata.append(inbuffer.tolist())
        print(str(len(self.indata)-self.npts) + ' : ' + str(len(self.indata)))

        #self.inplot.set_data(range(len(self.indata)-self.npts,len(self.indata)),inbuffer)
        self.inplot.set_data(range(len(self.indata)),self.indata)
        self.ui.inplot.draw()
        QtGui.QApplication.processEvents()

    def stop_gen(self):
        self.ao.stop()
        self.ai.stop()



def get_ao_chans(dev):
    buf = create_string_buffer(256)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAOPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode('utf-8').split(",")
    #print(chans)
    return chans  

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = FGenerator()
    myapp.show()
    sys.exit(app.exec_())
