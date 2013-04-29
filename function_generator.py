import sys, os

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np
from scipy import signal
import scipy.io.wavfile as wv

from fg_form import Ui_fgform
from daq_tasks import *
from plotz import ResultsPlot

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
        self.ui.sr_edit.textChanged.connect(self.update_time)
        self.ui.npts_edit.textChanged.connect(self.update_time)
        self.ui.aisr_edit.textChanged.connect(self.update_time)
        self.ui.ainpts_edit.textChanged.connect(self.update_time)        
        self.update_time()
        self.ui.wav_radio.toggled.connect(self.update_npts)
        self.ui.browse_button.clicked.connect(self.getdir)
        
        axis_action = QtGui.QAction('adjust axis', self)
        axis_action.triggered.connect(self.adjust_axis)
        self.popMenu = QtGui.QMenu( self )
        self.popMenu.addAction( axis_action )

        #self.ui.inplot.setContextMenuPolicy(QtCore.Qt.CustomContextMenu);
        #self.ui.inplot.customContextMenuRequested.connect(self.on_context_menu)
        self.ui.inplot.figure.canvas.mpl_connect('button_press_event', 
                                                 self.on_figure_press)

        #mainbox = QtGui.QHBoxLayout()
        #mainbox.addLayout(self.ui.main_layout)

    def on_figure_press(self,event):
        if event.inaxes != self.ui.inplot.axes:
            return
        if event.button == 3:
            #print('xdata: {}, ydata: {}, x: {}, y: {}'.format(event.xdata,event.ydata, event.x, event.y))
            #print(self.ui.inplot.height())
            figheight = self.ui.inplot.height()
            point = QtCore.QPoint(event.x, figheight-event.y)
            self.popMenu.exec_(self.ui.inplot.mapToGlobal(point))

    def on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.ui.inplot.mapToGlobal(point))

    def adjust_axis(self):
        print("no one expects the spanish inquisition")

    def update_time(self):
        #update the time display if one of the parameters changes
        sr = int(self.ui.sr_edit.text())
        npts = int(self.ui.npts_edit.text())
        airate = int(self.ui.aisr_edit.text())
        readnpts = int(self.ui.ainpts_edit.text())

        aot = npts/sr
        ait = readnpts/airate
        self.aot = aot

        self.ui.aotime.setText("AO time: " + str(aot))
        self.ui.aitime.setText("AI time: " + str(ait))        

    def update_npts(self):
        if self.ui.wav_radio.isChecked():
            self.ui.reset_box.setEnabled(False)
            self.ui.ainpts_edit.setEnabled(False)
            self.ui.folder_edit.setEnabled(True)
        else:
            self.ui.folder_edit.setEnabled(False)
            self.ui.reset_box.setEnabled(True)
            self.ui.ainpts_edit.setEnabled(True)

    def getdir(self):
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open folder', 
                                                  'C:\\Users')
        self.ui.folder_edit.setText(fname)

    def start_gen(self):
        sr = int(self.ui.sr_edit.text())
        npts = int(self.ui.npts_edit.text())
        
        aochan = self.ui.aochan_box.currentText().encode()
        aichan = self.ui.aichan_box.currentText().encode()
        self.readnpts = int(self.ui.ainpts_edit.text())
        airate = int(self.ui.aisr_edit.text())
        self.scroll_plot = False

        self.airate = airate
        self.indata = []
        self.npts = npts
        self.ncollected = 0

        #plot data we intend to generate
        self.ui.inplot.axes.cla()
        self.ui.inplot.axes.plot([],[])

        aot = npts/sr
        ait = self.readnpts/airate 
        self.in_time_vals = np.linspace(0,ait,self.readnpts)       
        self.out_time_vals = np.linspace(0,aot,npts)
        self.display_line_data = []

        self.ui.outplot.axes.set_xlim(0,aot)
        
        if aot > ait:
            self.ui.inplot.axes.set_xlim(0,aot)   
        else:
            self.ui.inplot.axes.set_xlim(0,ait)   

        if self.ui.sin_radio.isChecked() or self.ui.square_radio.isChecked() or self.ui.saw_radio.isChecked():
            self.continuous_gen(aichan,aochan,sr,npts,airate,self.readnpts)
        else:
            self.readnpts=30000
            self.finite_gen(aichan,aochan,sr,airate,self.readnpts)

    def continuous_gen(self,aichan,aochan,sr,npts,aisr,ainpts):
        #in/out data
        amp = int(self.ui.amp_edit.text())
        freq = int(self.ui.freq_edit.text())
        self.ui.outplot.axes.set_ylim(-amp,amp)
        #self.ui.inplot.axes.set_ylim(-amp,amp) 
        self.ui.inplot.axes.set_ylim(-10,10)       
        if self.ui.sin_radio.isChecked():
            outdata = amp * np.sin(freq * np.linspace(0, 2*np.pi, npts))
        elif self.ui.square_radio.isChecked():
            outdata = amp * np.sign(np.sin(freq * np.linspace(0, 2*np.pi, npts
                                            )))
        elif self.ui.saw_radio.isChecked():
            outdata = amp * signal.sawtooth(freq * np.linspace(0, 2*np.pi, 
                                            npts))

        self.ui.outplot.axes.plot(self.out_time_vals,outdata)
        self.ui.inplot.axes.hold(True)

        self.ui.outplot.draw()
        self.ui.inplot.draw()
        QtGui.QApplication.processEvents()


        try:
            self.ai = AITask(aichan,aisr,npts)

            # two ways to sync -- give the AOTask the ai sample clock 
            # for its source, or have it trigger off the ai

            #first way
            #self.ao = AOTask(aochan,sr,npts,b"ai/SampleClock")

            #second way
            self.ao = AOTask(aochan,sr,npts,trigsrc=b"ai/StartTrigger")
            
            #print("amax of outdata: " + str(np.amax(outdata)))
            
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
        
        self.ncollected += r.value
        #print(self.ncollected)
        #store data in a numpy array where columns are trace sweeps
        #print(inbuffer.shape)
        self.indata.append(inbuffer.tolist())
        if self.scroll_plot:
            # Todo: make scrolling plot
            pass
        else:
            xl = self.ui.inplot.axes.axis() #axis limits
            if self.ncollected/self.airate > xl[1]:
                self.ui.inplot.axes.set_xlim((self.ncollected-r.value)/self.airate,
                                             ((self.ncollected-r.value)/self.airate)+self.aot)
                self.display_line_data = []
            self.display_line_data.extend(inbuffer.tolist())
            xl = self.ui.inplot.axes.axis()
            tdata = np.linspace(xl[0], xl[0]+(len(self.display_line_data)/self.airate), 
                                len(self.display_line_data))
            self.ui.inplot.axes.lines[0].set_data(tdata,self.display_line_data)
        
        self.ui.inplot.draw()
        QtGui.QApplication.processEvents()
    
    def finite_gen(self,aichan,aochan,sr,aisr,npts):
        #import audio files to output
        stimFolder = "C:\\Users\\Leeloo\\Dropbox\\daqstuff\\M1_FD024"
        #stimFolder = "C:\\Users\\amy.boyle\\sampledata\\M1_FD024"
        #print(stimFolder)
        #stimFolder = self.ui.folder_edit.text()        
        print(stimFolder)
        stimFileList = os.listdir(stimFolder)
        print('Found '+str(len(stimFileList))+' stim files')
                
        self.ui.inplot.axes.hold(False)
        self.ui.inplot.draw()
        QtGui.QApplication.processEvents()

        for istim in stimFileList[:6]:
                
            try:
                sr,outdata = wv.read(stimFolder+"\\"+istim)
            except:
                print("Problem reading wav file")
                raise
            outdata = outdata.astype(float)
            mx = np.amax(outdata)
            outdata = outdata/mx
                
            #overwrite npts and aisr with the output data length --FIXME!!!!!!!!
            #npts = len(outdata)
            aisr = sr

            self.ui.outplot.axes.set_xlim(0,len(outdata))
            self.ui.outplot.axes.plot(range(len(outdata)),outdata)
            
            #also set ai to same - FIXME!!!!!
            self.ui.inplot.axes.set_xlim(0,len(outdata))
            self.ui.inplot.axes.plot(range(len(outdata)),outdata)

            self.ui.outplot.draw()

            try:
                self.ai = AITaskFinite(aichan,aisr,npts)

                # two ways to sync -- give the AOTask the ai sample clock 
                # for its source, or have it trigger off the ai

                self.ao = AOTaskFinite(aochan,sr,len(outdata),b"",b"ai/StartTrigger")

                self.ao.write(outdata)
                self.ao.start()
                self.ai.StartTask()
                
                #blocking read
                data = self.ai.read()

                self.ncollected += npts
        
                #store data in a numpy array where columns are trace sweeps
                self.indata.append(data.tolist())
                #there is only one line of data, reset it to current acquisition
                self.ui.inplot.axes.lines[0].set_data(range(len(data)),data)
                self.ui.inplot.draw()
                QtGui.QApplication.processEvents()

                self.ai.stop()
                self.ao.stop()
            except:
                print('ERROR! TERMINATE!')
                self.ai.stop()
                self.ao.stop()
                raise
        print('done')
        print("indata len: " + str(len(self.indata[0])))
        aggdata = np.array(self.indata).transpose()
        print(aggdata.shape)
        rp = ResultsPlot(aggdata,self)
        rp.show()

    def stop_gen(self):
        try:
            self.ao.stop()
            self.ai.stop()
        except:
            print("Task already stopped, or does not exist")

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
