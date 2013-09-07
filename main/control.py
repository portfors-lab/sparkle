import sys, os
import json
import scipy.io.wavfile as wv

from audiolab.plotting.chacoplots import Plotter, LiveWindow, ScrollingPlotter, ImagePlotter
from PyQt4 import QtCore, QtGui

from audiolab.io.daq_tasks import *

from audiolab.config.info import caldata_filename, calfreq_filename
from audiolab.dialogs.saving_dlg import SavingDialog
from audiolab.tools.qthreading import ProtocolSignals
from audiolab.main.acqmodel import AcquisitionModel
import audiolab.tools.systools as systools
from audiolab.tools.audiotools import spectrogram

from maincontrol_form import Ui_ControlWindow

RED = QtGui.QPalette()
RED.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
GREEN = QtGui.QPalette()
GREEN.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)

INPUTSFNAME = "controlinputs.json"

class ControlWindow(QtGui.QMainWindow):
    def __init__(self, dev_name, parent=None):
        # auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_ControlWindow()
        self.ui.setupUi(self)

        self.ui.start_btn.clicked.connect(self.on_start)
        self.ui.stop_btn.clicked.connect(self.on_stop)

        cnames = get_ao_chans(dev_name.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(dev_name.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.running_label.setPalette(RED)

        # load saved user inputs
        inputsfname = os.path.join(systools.get_appdir(), INPUTSFNAME)
        try:
            with open(inputsfname, 'r') as jf:
                inputsdict = json.load(jf)
        except:
            print "problem loading app data"
            inputsdict = {}

        self.wavrootdir = inputsdict.get('wavrootdir', os.path.expanduser('~'))

        # set up wav file directory finder paths
        self.dirmodel = QtGui.QFileSystemModel(self)
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.ui.filetree_view.setModel(self.dirmodel)
        self.ui.filetree_view.setRootIndex(self.dirmodel.setRootPath(self.wavrootdir))

        self.filemodel = QtGui.QFileSystemModel(self)
        self.filemodel.setFilter(QtCore.QDir.Files)
        self.ui.filelist_view.setModel(self.filemodel)
        self.ui.filelist_view.setRootIndex(self.filemodel.setRootPath(self.wavrootdir))

        self.apply_calibration = False
        self.display = None
        self.fscale = 1000

        # set default values
        homefolder = os.path.join(os.path.expanduser("~"), "audiolab_data")
        self.savefolder = homefolder
        self.savename = u"untitled"
        self.saveformat = u'hdf5'

        self.live_lock = QtCore.QMutex()

        self.signals = ProtocolSignals()
        self.signals.response_collected.connect(self.display_response)
        self.signals.stim_generated.connect(self.display_stim)
        self.signals.ncollected.connect(self.update_chart)

        self.acqmodel = AcquisitionModel()

    def on_start(self):
        # set plot axis to appropriate limits
        winsz = float(self.ui.windowsz_spnbx.value())
        self.ui.display.set_xlimits((0,winsz/1000))

        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            pass
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_tc':
            self.tuning_curve()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            # change plot to scrolling plot
            acq_rate = self.ui.aisr_spnbx.value()*self.fscale
            aichan = str(self.ui.aichan_box.currentText())
            self.scrollplot = ScrollingPlotter(self, 1, 1/float(acq_rate))
            self.ui.stim_dock.setWidget(self.scrollplot.widget)
            self.start_chart(aichan, acq_rate)
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_experiment':
            pass
        else: 
            error("unrecognized tab selection")

    def on_stop(self):
        if self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            self.ait.stop()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_tc':
            self.acqmodel.halt_curve()
            if isinstance(self.sender(), QtGui.QPushButton):
                self.acqmodel.closedata()

        self.ui.start_btn.setEnabled(True)
        self.live_lock.unlock()
        self.ui.running_label.setText(u"OFF")
        self.ui.running_label.setPalette(RED)

    def start_chart(self, aichan, samplerate):
        npts = samplerate/10 #update display at 10Hz rate
        self.ait = AITask(aichan, samplerate, npts*5)
        self.ait.register_callback(self.read_continuous, npts)
        self.ait.start()

    def read_continuous(self,task):
        inbuffer = task.read()
        self.signals.ncollected.emit(inbuffer)

    def update_chart(self, data):
        self.scrollplot.update_data(data)

    def tuning_curve(self):
        print "run curve"

        if self.live_lock.tryLock():
            # will need to replace this with user defined filepath
            if self.apply_calibration:
                self.acqmodel.set_calibration(self.calfname)
            else:
                self.acqmodel.set_calibration(None)

            self.ui.start_btn.setEnabled(False)

            # will get from GUI in future
            self.fscale = 1000 
            self.tscale = 0.001
            
            try:
                #scale_factor = 1000
                aochan = self.ui.aochan_box.currentText()
                aichan = self.ui.aichan_box.currentText()
                f_start = self.ui.freq_start_spnbx.value()*self.fscale
                f_stop = self.ui.freq_stop_spnbx.value()*self.fscale
                f_step = self.ui.freq_step_spnbx.value()*self.fscale
                db_start = self.ui.db_start_spnbx.value()
                db_stop = self.ui.db_stop_spnbx.value()
                db_step = self.ui.db_step_spnbx.value()
                dur = self.ui.dur_spnbx_2.value()*self.tscale
                rft = self.ui.risefall_spnbx_2.value()*self.tscale
                reprate = self.ui.reprate_spnbx.value()
                sr = self.ui.aosr_spnbx.value()*self.fscale
                aisr = self.ui.aisr_spnbx.value()*self.fscale
                nreps = self.ui.nreps_spnbx.value()

                if f_start < f_stop:
                    freqs = range(f_start, f_stop+1, f_step)
                else:
                    freqs = range(f_start, f_stop-1, -f_step)
                if db_start < db_stop:
                    intensities = range(db_start, db_stop+1, db_step)
                else:
                    intensities = range(db_start, db_stop-1, -db_step)

                # calculate ms interval from reprate
                interval = (1/reprate)*1000
                self.sr = sr
                self.interval = interval

                # set up display
                if self.display == None or not(self.display.active):
                    pass
                    # self.spawn_display()
                    #self.display.show()

                if not os.path.isdir(self.savefolder):
                    os.makedirs(self.savefolder)

                self.acqmodel.set_save_params(self.savefolder, self.savename)
                self.acqmodel.setup_curve(dur=dur, sr=sr, rft=rft, 
                                          nreps=nreps, freqs=freqs,
                                          intensities=intensities,
                                          aisr=aisr, aochan=aochan, 
                                          aichan=aichan, interval=interval)

                self.acqmodel.register_signal(self.signals.response_collected, 'response_collected')
                self.acqmodel.register_signal(self.signals.stim_generated, 'stim_generated')
                
                self.ui.running_label.setText(u"RUNNING")
                self.ui.running_label.setPalette(GREEN)

                # save these lists for easier plotting later
                self.freqs = freqs
                self.intensities = intensities

                self.acqmodel.run_curve()

            except:
                self.live_lock.unlock()
                print u"handle curve set-up exception"
                self.ui.start_btn.setEnabled(True)
                raise
        else:
            print u"Operation already in progress"

    def display_stim(self, stimdeets, times, signal, xfft, yfft):
        print "display stim"
        self.ui.display.update_signal(times, signal)
        self.ui.display.update_fft(xfft, yfft)

    def display_response(self, times, response):
        print "display reponse"
        self.ui.display.update_spiketrace(times, response)

    def launch_save_dlg(self):
        field_vals = {u'savefolder' : self.savefolder, u'savename' : self.savename, u'saveformat' : self.saveformat}
        dlg = SavingDialog(default_vals = field_vals)
        if dlg.exec_():
            savefolder, savename, saveformat = dlg.get_values()
            self.savefolder = savefolder
            self.savename = savename
            self.saveformat = saveformat

    def launch_calibration_dlg(self):
        pass

    def browse_wavdirs(self):
        wavdir = QtGui.QFileDialog.getExistingDirectory(self, 'select root folder', self.wavrootdir)
        self.ui.filetree_view.setRootIndex(self.dirmodel.setRootPath(wavdir))
        self.ui.filelist_view.setRootIndex(self.filemodel.setRootPath(wavdir))
        self.ui.wavrootdir_lnedt.setText(wavdir)
        self.wavrootdir = wavdir

    def wavdir_selected(self, model_index):
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        self.ui.filelist_view.setRootIndex(self.filemodel.setRootPath(spath))

    def wavfile_selected(self, model_index):
        # display spectrogram of file
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        spec, f, bins, fs = spectrogram(spath)
        self.ui.display.update_spec(spec, xaxis=bins, yaxis=f)

        sr, wavdata = wv.read(spath)
        freq, spectrum = calc_spectrum(wavdata,sr)

        self.ui.display.update_fft(freq, spectrum)
        t = np.linspace(0,(float(len(wavdata))/sr), len(wavdata))
        self.ui.display.update_signal(t, wavdata)

    def wavfile_clicked(self, model_index):
        # display spectrogram of file
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        spec, f, bins, fs = spectrogram(spath)
        self.ui.display.update_spec(spec, xaxis=bins, yaxis=f)


    def closeEvent(self,event):
        # save current inputs to file for loading next time
        appdir = systools.get_appdir()
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        fname = os.path.join(appdir, INPUTSFNAME)

        savedict = {}
        savedict['wavrootdir'] = self.wavrootdir
        with open(fname, 'w') as jf:
            json.dump(savedict, jf)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = ControlWindow(devName)
    myapp.show()
    sys.exit(app.exec_())