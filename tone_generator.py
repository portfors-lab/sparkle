import sys, os
import threading
import time

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from IPython import embed
from IPython.config.loader import Config
from IPython.frontend.terminal.embed import InteractiveShellEmbed

from tgform import Ui_tgform
from daq_tasks import *
from plotz import *

class ToneGenerator(QtGui.QMainWindow):
    def __init__(self, dev_name, parent=None):
        #auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_tgform()
        self.ui.setupUi(self)

        cnames = get_ao_chans(dev_name.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(dev_name.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.start_button.clicked.connect(self.on_start)
        self.ui.stop_button.clicked.connect(self.on_stop)

        #self.setFocusPolicy()

        self.sp = None
       
        self.tone = []
        self.ai_lock = threading.Lock()

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
        #repeatedly present tone stimulus until user presses stop
        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()

        #update the stimulus, this will also set some of the class IO parameters
        self.update_stim()
        self.keep_playing = True

        t = threading.Thread(target=self.acq_loop, args =(aichan,aochan))
        t.daemon = True
        t.start()

    def acq_loop(self,aichan,aochan):
        #self.keep_playing = False
        while self.keep_playing:
            self.ai_lock.acquire()
            sr = self.sr
            npts = self.tone.size
            try:
                self.ai = AITaskFinite(aichan,sr,npts)
                self.ao = AOTaskFinite(aochan,sr,npts,b"",b"ai/StartTrigger")

                self.ao.write(self.tone)
                print("%.8f AO V" % np.amax(self.tone))

                self.ao.start()
                self.ai.StartTask()
                
                #blocking read
                data = self.ai.read()

                #spin off update thread
                #update_thread = GenericThread(self.update_plot, 1, range(len(data)), data)
                #update_thread.start()
                
                self.ai.stop()
                self.ao.stop()
                time.sleep(1)
                #self.update_plot(1,range(len(data)),data)

            except:
                print('ERROR! TERMINATE!')
                self.ai.stop()
                self.ao.stop()
                raise

            self.ai_lock.release()
            #print("data size {} or {}".format(data.shape[0],data.size))
            timevals = (np.arange(data.shape[0]))/sr
            #t = threading.Thread(target=self.update_plot, args = (1,timevals,data))
            #t.start()
            #also plot FFT
            print("%.5f AI V" % (np.amax(data)))
            sp = np.real(np.fft.fft(data)/npts)
            freq = np.arange(npts)/(npts/sr)
            sp = sp[:(npts/2)]
            freq = freq[:(npts/2)] #single sided
            maxidx = sp.argmax(axis=0)
            #print(maxidx)
            print("%.6f FFT, at %d Hz\n" % (np.amax(abs(sp)), freq[maxidx]))
            #print('fft max: {}, min: {}, freq max: {}, min: {}'.format(np.amax(sp), np.amin(sp), 
            #                                                           np.amax(freq), np.amin(freq)))
            #t = threading.Thread(target=self.update_plot, args = (2,freq,abs(sp)))
            #t.start()
            t = threading.Thread(target=self.update_plots, args = ([1,2],[0,1],[timevals, freq],[data,abs(sp)]))
            t.start()

        print("Stopped")

    def update_plot(self,axnum,xdata,ydata):
        #Do something with AI data
        #print("update plot")
        self.sp.fig.axes[axnum].lines[0].set_data(xdata,ydata)
        self.sp.fig.canvas.draw()
        QtGui.QApplication.processEvents()

    def update_plots(self,axnums,linenums,xdata,ydata):
        #Do something with AI data
        #print("update plot")
        for iax in range(len(axnums)):
            #print(iax)
            #print("ax {}, line {}, axlen {}, linelen {}, datalen {},{}".format(axnums[iax], linenums[iax], len(self.sp.fig.axes),len(self.sp.fig.axes[iax].lines) ,len(xdata[iax]),len(ydata[iax])))
            #print("line obj {}".format(self.sp.fig.axes[iax].lines))
            self.sp.fig.axes[axnums[iax]].lines[linenums[iax]].set_data(xdata[iax],ydata[iax])
        self.sp.fig.canvas.draw()
        QtGui.QApplication.processEvents()

    def on_stop(self):
        self.keep_playing = False
        #ips = setup_ipshell()
        #ips()

    def spawn_fig(self,timevals,tone,fft_xrange):
        #acquire lock first because the ai counts on there being a figure existing to plot to
        self.ai_lock.acquire()

        self.sp = SubPlots(timevals,tone,[],[],[[],[]],[[],[]],parent=None)
        #set axes limits?
        self.sp.fig.axes[0].set_ylim(-10,10)
        # set input y scale to match stimulus (since we are trying to measure it back right?)
        self.sp.fig.axes[1].set_ylim(-10,10)
        self.sp.fig.axes[0].set_xlim(0,5)
        self.sp.fig.axes[1].set_xlim(0,5)
        #Set fft bounds by range expected
        self.sp.fig.axes[2].set_ylim(0,2)
        self.sp.fig.axes[2].set_xlim(0,fft_xrange*2)
        self.sp.fig.canvas.draw()
        QtGui.QApplication.processEvents()

        self.ai_lock.release()
        self.sp.show()

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

        #acquire lock and update IO parameters
        self.ai_lock.acquire()
        self.tone = tone
        self.sr = sr
        self.npts = npts
        self.ai_lock.release()

        self.statusBar().showMessage('npts: {}'.format(npts))

        if self.sp == None or not(self.sp.active):
            #print('create new')
            #t = threading.Thread(target= self.spawn_fig, args=(timevals,tone))
            #t.daemon=True
            #t = GenericThread(self.spawn_fig, timevals, tone)
            #t.start()
            self.spawn_fig(timevals,tone,f)
        else:
            #always only single axes and line
            #adjust the FFT x axis
            self.sp.fig.axes[2].set_xlim(0,f*2)
            t = threading.Thread(target=self.update_plots, args=([0,2],[0,0],[timevals, freq],[tone, sp]))
            t.daemon=True
            t.start()

    def keyPressEvent(self,event):
        #print("keypress")
        #print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.update_stim()
            self.setFocus()
        elif event.key () == QtCore.Qt.Key_Escape:
            self.setFocus()
        elif event.text() == 'a':
            self.ui.sr_spnbx.stepDown()
        elif event.text() == 's':
            self.ui.sr_spnbx.stepUp()
        elif event.text() == 'q':
            self.ui.freq_spnbx.stepDown()
        elif event.text() == 'w':
            self.ui.freq_spnbx.stepUp()
        elif event.text() == 'z':
            self.ui.dur_spnbx.stepDown()
        elif event.text() == 'x':
            self.ui.dur_spnbx.stepUp()
        elif event.text() == 'e':
            self.ui.db_spnbx.stepDown()
        elif event.text() == 'r':
            self.ui.db_spnbx.stepUp()
        elif event.text() == 'd':
            self.ui.risefall_spnbx.stepDown()
        elif event.text() == 'f':
            self.ui.risefall_spnbx.stepUp()
        elif event.text() == 'u':
            self.print_caldata()

    def mousePressEvent(self,event):
        self.setFocus()

    def closeEvent(self,event):
        # halt acquisition loop
        self.on_stop()

        #save inputs into file to load up next time
        f = self.ui.freq_spnbx.value()
        sr = self.ui.sr_spnbx.value()
        dur = self.ui.dur_spnbx.value()
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()
        aochan_index = self.ui.aochan_box.currentIndex()
        aichan_index = self.ui.aichan_box.currentIndex()

        save_inputs(f,sr,dur,db,rft,aochan_index,aichan_index)

        QtGui.QMainWindow.closeEvent(self,event)

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

def make_tone(freq,db,dur,risefall,samplerate):
        #create portable tone generator class that allows the ability to generate tones that modifyable on-the-fly
        npts = dur * samplerate
        #print("duration (s) :{}".format(dur))
        # equation for db from voltage is db = 20 * log10(V2/V1))
        # 10^(db/20)
        v_at_caldB = 0.175
        caldB = 100
        amp = (10 ** ((db-caldB)/20)*v_at_caldB)
        print('*'*40)
        print("AO Amp: {}, current dB: {}, cal dB: {}, V at cal dB: {}".format(amp, db, caldB, v_at_caldB))
        rf_npts = risefall * samplerate
        #print('amp {}, freq {}, npts {}, rf_npts {}'.format(amp,freq,npts,rf_npts))
        tone = amp * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
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


def setup_ipshell():
    try:
        get_ipython
    except NameError:
        nested = 0
        cfg = Config()
        prompt_config = cfg.PromptManager
        prompt_config.in_template = 'In <\\#>: '
        prompt_config.in2_template = '   .\\D.: '
        prompt_config.out_template = 'Out<\\#>: '
    else:
        print("Running nested copies of IPython.")
        print("The prompts for the nested copy have been modified")
        cfg = Config()
        nested = 1

    # First import the embeddable shell class


    # Now create an instance of the embeddable shell. The first argument is a
    # string with options exactly as you would type them if you were starting
    # IPython at the system command line. Any parameters you want to define for
    # configuration can thus be specified here.
    ipshell = InteractiveShellEmbed(config=cfg,
                                    banner1 = 'Dropping into IPython',
                                    exit_msg = 'Leaving Interpreter, back to program.')
    return ipshell

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = ToneGenerator(devName)
    myapp.show()
    sys.exit(app.exec_())
