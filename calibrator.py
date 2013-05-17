import sys, os
import time

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np

from daq_tasks import *
from plotz import *
from calform import Ui_CalibrationWindow

AIPOINTS = 1000
XLEN = 5 #seconds

class Calibrator(QtGui.QMainWindow):
    def __init__(self, dev_name, parent=None):
        #auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_CalibrationWindow()
        self.ui.setupUi(self)

        cnames = get_ao_chans(dev_name.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(dev_name.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.start_button.clicked.connect(self.on_start)
        self.ui.stop_button.clicked.connect(self.on_stop)

        self.tone = []
        self.sp = None

        inlist = load_inputs()
        if len(inlist) > 0:
            self.ui.freq_spnbx.setValue(inlist[0])
            self.ui.sr_spnbx.setValue(inlist[1])
            self.ui.dur_spnbx.setValue(inlist[2])
            self.ui.db_spnbx.setValue(inlist[3])
            self.ui.risefall_spnbx.setValue(inlist[4])
            self.ui.aochan_box.setCurrentIndex(inlist[5])
            self.ui.aichan_box.setCurrentIndex(inlist[6])

    def on_start(self):

        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        # depending on currently displayed tab, present
        # tuning curve, or on-the-fly modifyabe tone
        
        if self.ui.tabs.currentIndex() == 0 :
            print("vroom")
            self.cnt = 0
            self.update_stim()

            sr = self.sr
            npts = self.tone.size

            #self.data = np.zeros(npts)
            self.a = []
            self.ndata = 0
            self.current_line_data = []

            try:
                self.aitask = AITask(aichan,sr, AIPOINTS)
                self.aotask = AOTask(aochan,sr, npts, 
                                     trigsrc=b"ai/StartTrigger")
                self.aitask.register_callback(self.every_n_callback,AIPOINTS)

                self.aotask.StartTask()
                self.aitask.StartTask()
            except:
                print('ERROR! TERMINATE!')
                self.aitask.stop()
                self.aotask.stop()
                raise
        else:
            pass

    def on_stop(self):
        self.aitask.stop()
        self.aotask.stop()

    def update_stim(self):
        scale_factor = 1000
        f = self.ui.freq_spnbx.value()*scale_factor
        sr = self.ui.sr_spnbx.value()*scale_factor
        dur = self.ui.dur_spnbx.value()/scale_factor
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()/scale_factor

        #print('freq: {}, rft: {}'.format(f,rft))
        tone = make_tone(f,db,dur,rft,sr)
        
        npts = tone.size
        timevals = np.arange(npts)/sr

        #also plot stim FFT
        sp = np.fft.fft(tone)/npts
        freq = np.arange(npts)/(npts/sr)
        sp = sp[:(npts/2)]
        freq = freq[:(npts/2)] #single sided

        # I think I need to put in some sort of lock here?
        self.tone = tone
        self.sr = sr
        self.aitime = dur

        self.statusBar().showMessage('npts: {}'.format(npts))

        # now update the display of the stim
        if self.sp == None or not(self.sp.active):
            self.spawn_display(timevals, tone, f)
        else:
            self.stim_display(timevals, tone, freq, sp)

    def spawn_display(self,timevals,tone,f):
        self.sp = AnimatedDisplay(timevals,tone,[],[],[[],[]],[[],[]],
                                  interval=10, callback=self.ai_display)
        #unset animation on first axes for stim
        self.sp.figure.axes[0].lines[0].set_animated(False)
        self.sp.show()

    def stim_display(self, xdata, ydata, xfft, yfft):
        # hard coded for stim in axes 0 and FFT in 2
        print("update stim display")
        print('x0: {}, xend: {}'.format(xdata[0], xdata[-1]))
        self.sp.figure.axes[0].lines[0].set_data(xdata,ydata)
        self.sp.figure.axes[2].lines[0].set_data(xfft,yfft)
        self.sp.draw()
        QtGui.QApplication.processEvents()

    def ai_display(self,task):
            
        current_size = self.sp.figure.axes[1].bbox.width, self.sp.figure.axes[1].bbox.height
        if self.sp.old_size != current_size:
            self.sp.old_size = current_size
            xlims = self.sp.figure.axes[1].axis()
            self.sp.figure.axes[1].clear()
            self.sp.figure.axes[1].plot([],[])
            self.sp.figure.axes[1].set_ylim(-10,10)
            self.sp.figure.axes[1].set_xlim(xlims[0], xlims[1])
            self.sp.draw()
            self.sp.ax_background = self.sp.copy_from_bbox(self.sp.figure.axes[1].bbox)
        
        self.sp.restore_region(self.sp.ax_background)
        lims = self.sp.figure.axes[1].axis()

        data = self.current_line_data[:]
        
        t = len(data)/self.sr
        #xdata = np.arange(lims[0], lims[0]+len(self.current_line_data))
        xdata = np.linspace(lims[0], lims[0]+t, len(data))
        self.sp.figure.axes[1].lines[0].set_data(xdata,data)
        
        self.sp.figure.axes[1].draw_artist(self.sp.figure.axes[1].lines[0])
        self.sp.blit(self.sp.figure.axes[1].bbox)

        if self.cnt == 0:
            # TODO: this shouldn't be necessary, but if it is excluded the
            # canvas outside the axes is not initially painted.
            self.sp.draw()
        self.cnt += 1

    def every_n_callback(self,task):
        # read in the data as it is acquired and append to data structure
        try:
            read = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,
                               inbuffer,task.n,byref(read),None)
            self.a.extend(inbuffer.tolist())
            #print(self.data[0])
            self.ndata += read.value
            #print(self.ndata)
            
            n = read.value
            lims = self.sp.figure.axes[1].axis()
            #print("lims {}".format(lims))
            #print("ndata {}".format(self.ndata))
            
            ndata = len(self.current_line_data)
            aisr = self.sr
            if ndata/aisr > self.aitime:
            #if ndata/aisr > lims[1]:
                #print("change x lim, {} to {}".format((ndata-n)/aisr,((ndata-n)/aisr)+XLEN))
                #self.sp.figure.axes[1].set_xlim((ndata-n)/aisr,((ndata-n)/aisr)+XLEN)
                # must use regular draw to update axes tick labels
                #self.sp.draw()
                # update saved background so scale stays accurate
                #self.sp.ax_background = self.sp.copy_from_bbox(self.sp.figure.axes[1].bbox)
                self.current_line_data = []
            
            self.current_line_data.extend(inbuffer.tolist())
        except: 
            print('ERROR! TERMINATE!')
            self.aitask.stop()
            self.aotask.stop()
            raise

    def set_interval_min(self):
        print("to do: interval min")

    def set_dur_max(self):
        print("also need to set dur_max")

    def keyPressEvent(self,event):
        #print("keypress")
        #print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.update_stim()
            self.setFocus()
        elif event.key () == QtCore.Qt.Key_Escape:
            self.setFocus()

def make_tone(freq,db,dur,risefall,samplerate):
    # create portable tone generator class that allows the 
    # ability to generate tones that modifyable on-the-fly
    npts = dur * samplerate
    #print("duration (s) :{}".format(dur))
    # equation for db from voltage is db = 20 * log10(V2/V1))
    # 10^(db/20)
    v_at_caldB = 0.175
    caldB = 100
    amp = (10 ** ((db-caldB)/20)*v_at_caldB)
    print('*'*40)
    print("AO Amp: {}, current dB: {}, cal dB: {}, V at cal dB: {}"
          .format(amp, db, caldB, v_at_caldB))
    rf_npts = risefall * samplerate
    #print('amp {}, freq {}, npts {}, rf_npts {}'
    # .format(amp,freq,npts,rf_npts))
    
    tone = amp * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
    #add rise fall
    if risefall > 0:
        tone[:rf_npts] = tone[:rf_npts] * np.linspace(0,1,rf_npts)
        tone[-rf_npts:] = tone[-rf_npts:] * np.linspace(1,0,rf_npts)
        
        return tone

def load_inputs():
    cfgfile = "inputs.cfg"
    input_list = []
    try:
        with open(cfgfile, 'r') as cfo:
            for line in cfo:
                input_list.append(int(line.strip()))
        cfo.close()
    except:
        print("error loading user inputs file")
    return input_list

def save_inputs(*args):
    #should really do this with a dict
    cfgfile = "inputs.cfg"
    cf = open(cfgfile, 'w')
    for arg in args:
        cf.write("{}\n".format(arg))
    cf.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = Calibrator(devName)
    myapp.show()
    sys.exit(app.exec_())
