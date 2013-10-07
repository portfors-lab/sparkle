import sys, os
import json
import scipy.io.wavfile as wv

from audiolab.plotting.chacoplots import Plotter, LiveWindow, ScrollingPlotter, ImagePlotter
from PyQt4 import QtCore, QtGui

from audiolab.io.daq_tasks import *

from audiolab.config.info import caldata_filename, calfreq_filename
from audiolab.dialogs.saving_dlg import SavingDialog 
from audiolab.dialogs.scale_dlg import ScaleDialog
from audiolab.tools.qthreading import ProtocolSignals
from audiolab.main.acqmodel import AcquisitionModel
import audiolab.tools.systools as systools
from audiolab.tools.audiotools import spectrogram, calc_spectrum

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

        self.apply_calibration = False
        self.display = None

        self.live_lock = QtCore.QMutex()

        self.signals = ProtocolSignals()
        self.signals.response_collected.connect(self.display_response)
        self.signals.stim_generated.connect(self.display_stim)
        self.signals.ncollected.connect(self.update_chart)
        self.signals.spikes_found.connect(self.display_raster)
        self.signals.trace_finished.connect(self.trace_done)
        self.ui.display.spiketrace_plot.traits.signals.threshold_updated.connect(self.update_thresh)

        self.acqmodel = AcquisitionModel()
        self.acqmodel.register_signal(self.signals.response_collected, 'response_collected')
        self.acqmodel.register_signal(self.signals.spikes_found, 'spikes_found')
        self.acqmodel.register_signal(self.signals.trace_finished, 'trace_finished')

        self.ui.thresh_lnedt.returnPressed.connect(self.set_plot_thresh)        
        
        self.current_operation = None

        # set default values
        homefolder = os.path.join(os.path.expanduser("~"), "audiolab_data")
        
        # load saved user inputs
        inputsfname = os.path.join(systools.get_appdir(), INPUTSFNAME)
        try:
            with open(inputsfname, 'r') as jf:
                inputsdict = json.load(jf)
        except:
            print "problem loading app data"
            inputsdict = {}

        self.wavrootdir = inputsdict.get('wavrootdir', os.path.expanduser('~'))
        self.ui.thresh_lnedt.setText(inputsdict.get('threshold', '0.5'))
        self.ui.aisr_spnbx.setValue(inputsdict.get('aisr', 100))
        self.ui.binsz_lnedt.setText(inputsdict.get('binsz', '5'))        
        self.tscale = inputsdict.get('tscale', 0.001)
        self.fscale = inputsdict.get('fscale', 1000)
        self.savefolder = inputsdict.get('savefolder', homefolder)
        self.savename = inputsdict.get('savename', "untitled")
        self.saveformat = inputsdict.get('saveformat', 'hdf5')

        # update GUI to reflect loaded values
        self.update_unit_labels()
        self.set_plot_thresh()

        # set up wav file directory finder paths
        self.dirmodel = QtGui.QFileSystemModel(self)
        self.dirmodel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.ui.filetree_view.setModel(self.dirmodel)
        self.ui.filetree_view.setRootIndex(self.dirmodel.setRootPath(self.wavrootdir))

        self.filemodel = QtGui.QFileSystemModel(self)
        self.filemodel.setFilter(QtCore.QDir.Files)
        self.ui.filelist_view.setModel(self.filemodel)
        self.ui.filelist_view.setRootIndex(self.filemodel.setRootPath(self.wavrootdir))

    def on_start(self):
        # set plot axis to appropriate limits

        acq_rate = self.ui.aisr_spnbx.value()*self.fscale
        aichan = str(self.ui.aichan_box.currentText())
        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            self.run_explore()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_tc':
            self.tuning_curve()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            # change plot to scrolling plot
            winsz = float(self.ui.windowsz_spnbx.value())
            self.ui.display.set_xlimits((0,winsz/1000))
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
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            self.acqmodel.halt_explore()

        self.current_operation = None
        self.ui.start_btn.setEnabled(True)
        self.live_lock.unlock()
        self.ui.running_label.setText(u"OFF")
        self.ui.running_label.setPalette(RED)
        self.ui.start_btn.setText('Start')


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

    def run_explore(self):
        self.ui.start_btn.setText('Update')
        # make this an enum!!!!
        self.current_operation = 'explore'
        aochan = self.ui.aochan_box.currentText()
        aichan = self.ui.aichan_box.currentText()
        acq_rate = self.ui.aisr_spnbx.value()*self.fscale
        winsz = float(self.ui.windowsz_spnbx.value())*self.tscale
        binsz = float(self.ui.binsz_lnedt.text())*self.tscale
        nreps = self.ui.nreps_spnbx.value()
        reprate = self.ui.reprate_spnbx.value()
        interval = (1/reprate)*1000

        print 'interval', interval
        # set up first stimulus, lets start with vocalizations for now
        if self.ui.explore_stim_type_cmbbx.currentText() == 'Vocalization':
            # assume user has already clicked on wav file
            
            self.acqmodel.set_explore_params(wavfile=self.current_wav_file, aochan=aochan, aichan=aichan,
                                             acqtime=winsz, aisr=acq_rate, nreps=nreps)
            self.acqmodel.run_explore(interval)


    def tuning_curve(self):
        print "run curve"
        if self.live_lock.tryLock():
            pass
        else:
            print u"Operation already in progress"
            return

        # will need to replace this with user defined filepath
        if self.apply_calibration:
            self.acqmodel.set_calibration(self.calfname)
        else:
            self.acqmodel.set_calibration(None)

        self.ui.start_btn.setEnabled(False)

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

    def display_stim(self, stimdeets, times, signal, xfft, yfft):
        print "display stim"
        self.ui.display.update_signal(times, signal)
        self.ui.display.update_fft(xfft, yfft)

    def display_response(self, times, response):
        print "display reponse"
        self.ui.display.update_spiketrace(times, response)

    def display_raster(self, bins, spike_counts):
        self.ui.display.add_raster_points(bins, spike_counts)

    def trace_done(self):
        self.ui.display.clear_raster()


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

    def launch_scale_dlg(self):
        field_vals = {u'fscale' : self.fscale, u'tscale' : self.tscale}
        dlg = ScaleDialog(default_vals=field_vals)
        if dlg.exec_():
            fscale, tscale = dlg.get_values()
            self.fscale = fscale
            self.tscale = tscale
        self.update_unit_labels()

    def update_unit_labels(self):
        nf_lbls = 7
        nt_lbls = 8
        if self.fscale == 1000:
            # better way to do this than eval?
            for i in range(nf_lbls):
                lbl_str = "self.ui.funit_lbl" + str(i) + ".setText(u'kHz')"
                try:
                    eval(lbl_str)
                except:
                    print "trouble with command: ", lbl_str
        elif self.fscale == 1:
            for i in range(nf_lbls):
                lbl_str = "self.ui.funit_lbl" + str(i) + ".setText(u'Hz')"
                try:
                    eval(lbl_str)
                except:
                    print "trouble with command: ", lbl_str
        else:
            print self.fscale
            raise Exception(u"Invalid frequency scale")
            
        if self.tscale == 0.001:
            for i in range(nt_lbls):
                lbl_str = "self.ui.tunit_lbl" + str(i) + ".setText(u'ms')"
                try:
                    eval(lbl_str)
                except:
                    print "trouble with command: ", lbl_str
        elif self.tscale == 1:
            for i in range(nt_lbls):
                lbl_str = "self.ui.tunit_lbl" + str(i) + ".setText(u's')"
                try:
                    eval(lbl_str)
                except:
                    print "trouble with command: ", lbl_str
        else:
            print self.tscale
            raise Exception(u"Invalid time scale")
    
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
        """ On double click of wav file, load into display """
        # display spectrogram of file
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        spec, f, bins, fs = spectrogram(spath)
        self.ui.display.update_spec(spec, xaxis=bins, yaxis=f)

        sr, wavdata = wv.read(spath)
        freq, spectrum = calc_spectrum(wavdata,sr)

        self.ui.display.update_fft(freq, spectrum)
        t = np.linspace(0,(float(len(wavdata))/sr), len(wavdata))
        print 'stim time lims', t[0], t[-1]
        self.ui.display.update_signal(t, wavdata)

        self.current_wav_file = spath

        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            aochan = self.ui.aochan_box.currentText()
            aichan = self.ui.aichan_box.currentText()
            acq_rate = self.ui.aisr_spnbx.value()*self.fscale
            winsz = float(self.ui.windowsz_spnbx.value())*0.001
            self.acqmodel.set_explore_params(wavfile=self.current_wav_file, aochan=aochan, aichan=aichan,
                                             acqtime=winsz, aisr=acq_rate)
            print 'win size', winsz
            self.ui.display.set_xlimits((0,winsz))
        # self.current_gen_rate = sr
        # self.current_wav_signal = wavdata

    def wavfile_clicked(self, model_index):
        # display spectrogram of file
        spath = self.dirmodel.fileInfo(model_index).absoluteFilePath()
        spec, f, bins, fs = spectrogram(spath)
        # self.ui.display.update_spec(spec, xaxis=bins, yaxis=f)
        self.ui.spec_preview.update_data(spec,xaxis=bins,yaxis=f)

    def update_thresh(self, thresh):
        self.ui.thresh_lnedt.setText(str(thresh))
        self.acqmodel.set_threshold(thresh)

    def set_plot_thresh(self):
        thresh = float(self.ui.thresh_lnedt.text())
        self.ui.display.spiketrace_plot.set_threshold(thresh)
        self.acqmodel.set_threshold(thresh)

    def closeEvent(self,event):
        # save current inputs to file for loading next time
        appdir = systools.get_appdir()
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        fname = os.path.join(appdir, INPUTSFNAME)

        savedict = {}
        savedict['wavrootdir'] = self.wavrootdir
        savedict['threshold'] = self.ui.thresh_lnedt.text()
        savedict['binsz'] = self.ui.binsz_lnedt.text()
        savedict['aisr'] = self.ui.aisr_spnbx.value()
        savedict['tscale'] = self.tscale
        savedict['fscale'] = self.fscale
        savedict['savefolder'] = self.savefolder
        savedict['savename'] = self.savename
        savedict['saveformat'] = self.saveformat
        with open(fname, 'w') as jf:
            json.dump(savedict, jf)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = ControlWindow(devName)
    myapp.show()
    sys.exit(app.exec_())