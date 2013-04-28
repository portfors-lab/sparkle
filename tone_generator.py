import sys, os

from PyQt4 import QtCore, QtGui
from PyDAQmx import *
import numpy as np

from tgform import Ui_tgform
from daq_tasks import *
from plotz import *

class ToneGenerator(QtGui.QMainWindow):
    def __init__(self, parent=None):
        #auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_tgform()
        self.ui.setupUi(self)

        self.ui.start_button.clicked.connect(self.update_stim)
        self.sp = None

    def update_stim(self):
        f = self.ui.freq_spnbx.value()
        sr = self.ui.sr_spnbx.value()
        dur = self.ui.dur_spnbx.value()
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()
        f = f*1000 # convert to Hz

        tone = self.make_tone(f,db,dur,rft,sr)
        
        timevals = (np.arange(tone.shape[0]))/sr
        if self.sp == None:
            print('create new')
            self.sp = SimplePlot(timevals,tone,parent=self)
            #set axes limits?
            self.sp.fig.axes[0].set_ylim(-10,10)
            self.sp.fig.axes[0].set_xlim(0,5000)
            self.sp.fig.canvas.draw()
        else:
            #always only single axes and line
            print('update')
            self.sp.fig.axes[0].lines[0].set_data(timevals,tone)
            self.sp.fig.canvas.draw()

    def stop(self):
        pass

    def make_tone(self,freq,db,dur,risefall,samplerate):
        #create portable tone generator class that allows the ability to generate tones that modifyable on-the-fly
        npts = dur * samplerate

        # equation for db from voltage is db = 20 * log10(V2/V1))
        # 10^(db/20)
        amp = 10 ** (db/20)
        rf_npts = risefall * samplerate
        tone = amp * np.sin(freq * np.linspace(0, 2*np.pi, npts))
        #add rise fall
        if risefall > 0:
            tone[:rf_npts] = tone[:rf_npts] * np.linspace(0,1,rf_npts)
            tone[-rf_npts:] = tone[-rf_npts:] * np.linspace(1,0,rf_npts)

        return tone

    def keyPressEvent(self,event):
        print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
           self.update_stim()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = ToneGenerator()
    myapp.show()
    sys.exit(app.exec_())
