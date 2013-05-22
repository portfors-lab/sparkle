import sys, os
import time
import pickle

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np

from daq_tasks import *
from plotz import *
from calform import Ui_CalibrationWindow
from disp_dlg import DisplayDialog

AIPOINTS = 100 #only used if default not saved
XLEN = 5 #seconds, also not used?
SAVE_DATA_CHART = False
SAVE_DATA_TRACES = False
USE_FINITE = True

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
            try:
                self.ui.freq_spnbx.setValue(inlist[0])
                self.ui.sr_spnbx.setValue(inlist[1])
                self.ui.dur_spnbx.setValue(inlist[2])
                self.ui.db_spnbx.setValue(inlist[3])
                self.ui.risefall_spnbx.setValue(inlist[4])
                self.ui.aochan_box.setCurrentIndex(inlist[5])
                self.ui.aichan_box.setCurrentIndex(inlist[6])
                self.ainpts = inlist[7]
                self.ui.aisr_spnbx.setValue(inlist[8])
                self.ui.interval_spnbx.setValue(inlist[9])
            except:
                print("failed to find all defaults")
                self.ainpts = AIPOINTS

        self.daq_lock = QtCore.QMutex()
        self.stim_lock = QtCore.QMutex()
        self.daq_timer = None
        self.thread_pool = []

        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(5)

        self.signal = WorkerSignal()
        self.signal.done.connect(self.ai_display)

    def on_start(self):
        self.on_stop()

        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        # depending on currently displayed tab, present
        # tuning curve, or on-the-fly modifyable tone
        
        if self.ui.tabs.currentIndex() == 0 :

            self.cnt = 0
            self.update_stim()

            sr = self.sr
            npts = self.tone.size
            interval = self.ui.interval_spnbx.value()

            if SAVE_DATA_CHART or SAVE_DATA_TRACES:
                self.a = []
            
            self.ndata = 0
            self.current_line_data = []
            #self.sp.start_update(100)

            # cannot change interval on the fly
            self.ui.interval_spnbx.setEnabled(False)
            try:
                if USE_FINITE:
                    # set a timer to repeatedly start ao and ai tasks
                    # set up first go before timer, so that the task starts as soon as timer fires
                    response_npts = int(self.aitime*self.aisr)
                    self.aitask = AITaskFinite(aichan, self.aisr, response_npts)
                    self.aotask = AOTaskFinite(aochan, sr, npts, trigsrc=b"ai/StartTrigger")
                    self.aotask.write(self.tone)
                    self.daq_timer = self.startTimer(interval)
                else:
                    self.aitask = AITask(aichan, self.aisr, self.ainpts)
                    self.aotask = AOTask(aochan, sr, npts, 
                                         trigsrc=b"ai/StartTrigger")
                    self.aitask.register_callback(self.every_n_callback,
                                                  self.ainpts)
                    self.aotask.write(self.tone)
                    
                    self.aotask.StartTask()
                    self.aitask.StartTask()
            except:
                print('ERROR! TERMINATE!')
                self.on_stop
                raise
        else:
            pass

    def on_stop(self):
        self.ui.interval_spnbx.setEnabled(True)
        if USE_FINITE:
            if self.daq_timer is not None:
                self.killTimer(self.daq_timer)
        else:
            try:
                self.aitask.stop()
                self.aotask.stop()
                self.sp.killTimer(self.sp.timer)
            except DAQError:
                print("No task running")
            except:
                raise

    def update_stim(self):
        scale_factor = 1000
        time_scale = 1000
        f = self.ui.freq_spnbx.value()*scale_factor
        sr = self.ui.sr_spnbx.value()*scale_factor
        dur = self.ui.dur_spnbx.value()/scale_factor
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()/scale_factor
        aisr =  self.ui.aisr_spnbx.value()*scale_factor
        #dur = 1

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
        self.stim_lock.lock()
        self.tone = tone
        self.sr = sr
        self.aitime = dur
        self.aisr = aisr
        self.stim_lock.unlock()

        self.statusBar().showMessage('npts: {}'.format(npts))

        # now update the display of the stim
        if self.sp == None or not(self.sp.active):
            self.spawn_display(timevals, tone)
            self.sp.draw_line(2,0,freq,sp)
        else:
            self.stim_display(timevals, tone, freq, sp)

    def spawn_display(self,timevals,tone):
        self.sp = AnimatedWindow((timevals,tone), ([],[]), 
                                 ([[],[]],[[],[]]))

        #unset animation on first axes for stim
        #self.sp.figure.axes[0].lines[0].set_animated(False)
        self.sp.show()

        # draw stim
        self.sp.axs[0].draw_artist(self.sp.axs[0].lines[0])
        self.sp.canvas.blit(self.sp.axs[0].bbox)

    def stim_display(self, xdata, ydata, xfft, yfft):
        # hard coded for stim in axes 0 and FFT in 2
        print('x0: {}, xend: {}'.format(xdata[0], xdata[-1]))
        self.sp.draw_line(0,0,xdata,ydata)
        self.sp.draw_line(2,0,xfft,yfft)
        
    def ai_display(self):
        try:
            lims = self.sp.axs[1].axis()
            # copy data to variable as data structures not synchronized :(
            data = self.current_line_data[:]
        
            t = len(data)/self.aisr
            #xdata = np.arange(lims[0], lims[0]+len(self.current_line_data))
            xdata = np.linspace(lims[0], lims[0]+t, len(data))

            print("response x range {}".format(xdata[0], xdata[-1]))
        
            self.sp.draw_line(1,0,xdata,data)
        except:
            print("Error drawing line data")
            self.sp.killTimer(self.sp.timer)
            raise

    def timerEvent(self, evt):
        print("tick")

        #self.thread_pool.append( GenericThread(self.finite_worker) )
        t  = GenericThread(self.finite_worker)
        #t.start()
        #self.thread_pool[len(self.thread_pool)-1].start()
        #print("threadpool size {}".format(len(self.thread_pool)))
        self.pool.start(t)

    def finite_worker(self):
        # acquire data and reset task to be read for next timer event
        self.daq_lock.lock()
        self.aotask.StartTask()
        self.aitask.StartTask()
        
        # blocking read
        data = self.aitask.read()
        self.current_line_data = data

        print("data max {}, min {}".format(np.amax(data), np.amin(data)))

        self.aitask.stop()
        self.aotask.stop()

        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        self.stim_lock.lock()

        npts =  self.tone.size
        response_npts = int(self.aitime*self.aisr)

        self.aitask = AITaskFinite(aichan, self.aisr, response_npts)
        self.aotask = AOTaskFinite(aochan, self.sr, npts, trigsrc=b"ai/StartTrigger")
        self.aotask.write(self.tone)

        self.daq_lock.unlock()
        self.stim_lock.unlock()

        #self.emit(QtCore.SIGNAL('ai_display()'))
        self.signal.done.emit()
        
    def every_n_callback(self,task):
        
        # read in the data as it is acquired and append to data structure
        try:
            read = c_int32()
            inbuffer = np.zeros(task.n)
            task.ReadAnalogF64(task.n,10.0,DAQmx_Val_GroupByScanNumber,
                               inbuffer,task.n,byref(read),None)
            if SAVE_DATA_CHART:
                self.a.extend(inbuffer.tolist())
                # for now use stimulus data size also for acquisition
                #ainpts = len(self.tone)

            #print(self.data[0])
            self.ndata += read.value
            #print(self.ndata)
            
            n = read.value
            lims = self.sp.axs[1].axis()
            #print("lims {}".format(lims))
            #print("ndata {}".format(self.ndata))
            
            # for display purposes only
            ndata = len(self.current_line_data)
            aisr = self.aisr

            #print(self.aisr, self.aitime, ndata/aisr)
            if ndata/aisr >= self.aitime:
            #if ndata/aisr > lims[1]:
                #print("change x lim, {} to {}".format((ndata-n)/aisr,((ndata-n)/aisr)+XLEN))
                #self.sp.figure.axes[1].set_xlim((ndata-n)/aisr,((ndata-n)/aisr)+XLEN)
                # must use regular draw to update axes tick labels
                #self.sp.draw()
                # update saved background so scale stays accurate
                #self.sp.axs_background = self.sp.copy_from_bbox(self.sp.figure.axes[1].bbox)
                if len(self.current_line_data) != self.aitime*self.aisr:
                    print("incorrect number of data points saved")
                if SAVE_DATA_TRACES:
                    self.a.append(self.current_line_data)
                self.current_line_data = []
            
            self.current_line_data.extend(inbuffer.tolist())
        except MemoryError:
            print("data size: {}, elements: {}".format(sys.getsizeof(self.a)/(1024*1024), len(self.a)))
            self.aitask.stop()
            self.aotask.stop()
            raise
        except: 
            print('ERROR! TERMINATE!')
            #print("data size: {}, elements: {}".format(sys.getsizeof(self.a)/(1024*1024), len(self.a)))
            self.aitask.stop()
            self.aotask.stop()
            raise

    def set_interval_min(self):
        dur = self.ui.dur_spnbx.value()
        interval = self.ui.interval_spnbx.value()
        if interval < dur:
            print("interval less than duration, increasing interval")
            self.ui.interval_spnbx.setValue(dur)
        if interval == dur:
            print("Warning: No interval down-time, consider using continuous acquisition to avoid failure.")

    def set_dur_max(self):
        print("also need to set dur_max")

    def launch_display_dlg(self):
        field_vals = {'chunksz' : self.ainpts}
        dlg = DisplayDialog(default_vals=field_vals)
        if dlg.exec_():
            ainpts = dlg.get_values()
            self.ainpts = ainpts
        print(self.ainpts)

    def keyPressEvent(self,event):
        #print("keypress")
        #print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            if USE_FINITE:
                self.update_stim()
            else:
                self.on_stop()
                self.on_start()
            self.setFocus()
        elif event.key () == QtCore.Qt.Key_Escape:
            self.setFocus()

    def closeEvent(self,event):
        # halt acquisition loop
        self.on_stop()

        #save inputs into file to load up next time - order is important
        f = self.ui.freq_spnbx.value()
        sr = self.ui.sr_spnbx.value()
        dur = self.ui.dur_spnbx.value()
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()
        aochan_index = self.ui.aochan_box.currentIndex()
        aichan_index = self.ui.aichan_box.currentIndex()
        ainpts = self.ainpts
        aisr = self.ui.aisr_spnbx.value()
        interval = self.ui.interval_spnbx.value()

        save_inputs(f,sr,dur,db,rft,aochan_index,aichan_index, ainpts, aisr, interval)

        QtGui.QMainWindow.closeEvent(self,event)

class GenericThread(QtCore.QRunnable):
    def __init__(self, function, *args, **kwargs):
        QtCore.QRunnable.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
    """
    def __del__(self):
        self.wait()
    """
    def run(self):
        self.function(*self.args,**self.kwargs)
        return

class WorkerSignal(QtCore.QObject):
    done = QtCore.pyqtSignal()

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
