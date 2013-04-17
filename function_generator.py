import sys, os

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np
from scipy import signal

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
        cnames = get_ai_chans(b"Dev1")
        self.ui.aichan_box.addItems(cnames)
        self.ui.start_button.clicked.connect(self.start_gen)
        self.ui.stop_button.clicked.connect(self.stop_gen)

    def start_gen(self):
        sr = int(self.ui.sr_edit.text())
        npts = int(self.ui.npts_edit.text())
        amp = int(self.ui.amp_edit.text())
        freq = int(self.ui.freq_edit.text())
        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()
        self.readnpts = 10
        self.readnpts = npts

        #in/out data
        if self.ui.sin_radio.isChecked():
            outdata = amp * np.sin(freq * np.linspace(0, 2*np.pi, npts))
        elif self.ui.square_radio.isChecked():
            outdata = amp * np.sign(np.sin(freq * np.linspace(0, 2*np.pi, npts)))
        else:
            outdata = amp * signal.sawtooth(freq * np.linspace(0, 2*np.pi, npts))
        self.indata = []
        self.npts = npts
        self.ncollected = 0

        #plot data we intend to generate
        self.ui.outplot.axes.plot(range(len(outdata)),outdata)
        self.aiplot, = self.ui.inplot.axes.plot([],[])
        
        self.ui.outplot.axes.set_xlim(0,npts)
        self.ui.outplot.axes.set_ylim(-amp,amp)
        self.ui.inplot.axes.set_xlim(0,npts)
        self.ui.inplot.axes.set_ylim(-amp,amp)
        self.ui.inplot.axes.hold(True)

        self.ui.outplot.draw()
        self.ui.inplot.draw()
        QtGui.QApplication.processEvents()

        try:
            self.ai = AITask(aichan,sr,npts)
            self.ao = AOTask(aochan,sr,npts)
            self.ao.write(outdata)
            #register callback to plot after npts samples acquired into buffer
            self.ai.register_callback(self.every_n_callback,self.readnpts)
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
        inbuffer = np.zeros(self.readnpts)
        task.ReadAnalogF64(self.readnpts,10.0,DAQmx_Val_GroupByScanNumber,inbuffer,
                           self.readnpts,byref(r),None)
        #print("****************************dddd")
        self.ncollected += r.value
        print(self.ncollected)
        #store data in a numpy array where columns are trace sweeps
        #print(inbuffer.shape)
        self.indata.append(inbuffer.tolist())
        self.aiplot.set_data(range(len(inbuffer)),inbuffer)
        #self.ui.inplot.axes.plot(range(self.ncollected-self.readnpts,self.ncollected),inbuffer)
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

def get_ai_chans(dev):
    buf = create_string_buffer(512)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAIPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode('utf-8').split(",")
    #print(chans)
    return chans

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = FGenerator()
    myapp.show()
    sys.exit(app.exec_())
