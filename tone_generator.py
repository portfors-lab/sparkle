import sys, os

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import threading

from tgform import Ui_tgform
from daq_tasks import *
from plotz import *

class ToneGenerator(QtGui.QMainWindow):
    def __init__(self, parent=None):
        #auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_tgform()
        self.ui.setupUi(self)

        cnames = get_ao_chans(b"Dev1")
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(b"Dev1")
        self.ui.aichan_box.addItems(cnames)

        self.ui.start_button.clicked.connect(self.on_start)
        self.ui.stop_button.clicked.connect(self.on_stop)

        self.sp = None
        self.keep_playing = True
        self.tone = []
        self.ai_lock = threading.Lock()

    def on_start(self):
        #repeatedly present tone stimulus until user presses stop
        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()
        self.update_stim()

        sr = self.ui.sr_spnbx.value()*1000
        npts = self.tone.size
        self.statusBar().showMessage('npts: {}'.format(npts))

        t = threading.Thread(target=self.acq_loop, args =(aichan,aochan,sr,npts))
        t.daemon = True
        t.start()

    def acq_loop(self,aichan,aochan,sr,npts):
        #self.keep_playing = False
        while self.keep_playing:
            self.ai_lock.acquire()
            try:
                self.ai = AITaskFinite(aichan,sr,npts)
                
                self.ao = AOTaskFinite(aochan,sr,npts,b"",b"ai/StartTrigger")

                self.ao.write(self.tone)

                self.ao.start()
                self.ai.StartTask()
                
                #blocking read
                data = self.ai.read()

                #spin off update thread
                #update_thread = GenericThread(self.update_plot, 1, range(len(data)), data)
                #update_thread.start()
                
                self.ai.stop()
                self.ao.stop()
        
                #self.update_plot(1,range(len(data)),data)

            except:
                print('ERROR! TERMINATE!')
                self.ai.stop()
                self.ao.stop()
                raise

            self.ai_lock.release()
            t = threading.Thread(target=self.update_plot, args = (1,range(len(data)),data))
            t.daemon = True
            t.start()

        print("Stopped")

    def update_plot(self,axnum,xdata,ydata):
        #Do something with AI data
        #print("update plot")
        self.sp.fig.axes[axnum].lines[0].set_data(xdata,ydata)
        self.sp.fig.canvas.draw()
        QtGui.QApplication.processEvents()

    def on_stop(self):
        self.keep_playing = False

    def spawn_fig(self,timevals,tone):
        #acquire lock first because the ai counts on there being a figure existing to plot to
        self.ai_lock.acquire()

        self.sp = SubPlots(timevals,tone,[],[],parent=None)
        #set axes limits?
        self.sp.fig.axes[0].set_ylim(-10,10)
        self.sp.fig.axes[0].set_xlim(0,5)
        self.sp.fig.canvas.draw()
        QtGui.QApplication.processEvents()

        self.ai_lock.release()
        self.sp.show()

    def update_stim(self):
        f = self.ui.freq_spnbx.value()*1000
        sr = self.ui.sr_spnbx.value()*1000
        dur = self.ui.dur_spnbx.value()/1000
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()/1000

        #print('freq: {}, rft: {}'.format(f,rft))
        tone = make_tone(f,db,dur,rft,sr)
        
        timevals = (np.arange(tone.shape[0]))/sr
        
        if self.sp == None or not(self.sp.active):
            #print('create new')
            #t = threading.Thread(target= self.spawn_fig, args=(timevals,tone))
            #t.daemon=True
            #t = GenericThread(self.spawn_fig, timevals, tone)
            #t.start()
            self.spawn_fig(timevals,tone)
        else:
            #always only single axes and line
            #print('update')
            t = threading.Thread(target= self.update_plot, args=(0,timevals,tone))
            t.daemon=True
            t.start()
            #self.sp.fig.axes[0].lines[0].set_data(timevals,tone)
        
        self.tone = tone

    def keyPressEvent(self,event):
        print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
           self.update_stim()

    def closeEvent(self,event):
        # halt acquisition loop
        self.on_stop()
        QtGui.QMainWindow.closeEvent(self,event)

def make_tone(freq,db,dur,risefall,samplerate):
        #create portable tone generator class that allows the ability to generate tones that modifyable on-the-fly
        npts = dur * samplerate

        # equation for db from voltage is db = 20 * log10(V2/V1))
        # 10^(db/20)
        amp = 10 ** (db/20)
        rf_npts = risefall * samplerate
        #print('amp {}, freq {}, npts {}, rf_npts {}'.format(amp,freq,npts,rf_npts))
        tone = amp * np.sin(freq * np.linspace(0, 2*np.pi, npts))
        #add rise fall
        if risefall > 0:
            tone[:rf_npts] = tone[:rf_npts] * np.linspace(0,1,rf_npts)
            tone[-rf_npts:] = tone[-rf_npts:] * np.linspace(1,0,rf_npts)

        return tone

class GenericThread(threading.Thread):
    def __init__(self, function, *args, **kwargs):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    #def __del__(self):
        #self.wait()

    def run(self):
        self.function(*self.args, **self.kwargs)
        return

def get_ao_chans(dev):
    buf = create_string_buffer(256)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAOPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode('utf-8').split(",")
    return chans  

def get_ai_chans(dev):
    buf = create_string_buffer(512)
    buflen = c_uint32(sizeof(buf))
    DAQmxGetDevAIPhysicalChans(dev, buf, buflen)
    pybuf = buf.value
    chans = pybuf.decode('utf-8').split(",")
    return chans

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = ToneGenerator()
    myapp.show()
    sys.exit(app.exec_())
