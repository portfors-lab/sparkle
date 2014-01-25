import sys, os
import scipy.io.wavfile as wv

from spikeylab.plotting.custom_plots import ChartWidget
from PyQt4 import QtCore, QtGui

from spikeylab.io.daq_tasks import *

from spikeylab.config.info import caldata_filename, calfreq_filename
from spikeylab.dialogs.saving_dlg import SavingDialog 
from spikeylab.dialogs.scale_dlg import ScaleDialog
from spikeylab.dialogs.specgram_dlg import SpecDialog
from spikeylab.main.acqmodel import AcquisitionModel
from spikeylab.tools.audiotools import spectrogram, calc_spectrum
from spikeylab.plotting.custom_plots import SpecWidget

from controlwindow import ControlWindow

RED = QtGui.QPalette()
RED.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
GREEN = QtGui.QPalette()
GREEN.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)

DEVNAME = "PCI-6259"

class MainWindow(ControlWindow):
    def __init__(self, inputs_filename):
        # set up model and stimlui first, 
        # as saved configuration relies on this
        self.acqmodel = AcquisitionModel()
        
        # get stimuli editor widgets
        self.explore_stimuli = self.acqmodel.stimuli_list()
        
        # auto generated code intialization
        ControlWindow.__init__(self, inputs_filename)
        
        self.ui.start_btn.clicked.connect(self.on_start)
        self.ui.stop_btn.clicked.connect(self.on_stop)

        cnames = get_ao_chans(DEVNAME.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(DEVNAME.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.running_label.setPalette(RED)

        self.scrollplot = ChartWidget()

        self.apply_calibration = False
        self.display = None

        self.live_lock = QtCore.QMutex()

        self.ui.display.spiketrace_plot.traits.signals.threshold_updated.connect(self.update_thresh)
        
        self.ui.protocolView.setModel(self.acqmodel.protocol_model)

        self.acqmodel.signals.response_collected.connect(self.display_response)
        self.acqmodel.signals.spikes_found.connect(self.display_raster)
        self.acqmodel.signals.trace_finished.connect(self.trace_done)
        self.acqmodel.signals.stim_generated.connect(self.display_stim)
        self.acqmodel.signals.warning.connect(self.set_status_msg)
        self.acqmodel.signals.ncollected.connect(self.update_chart)
        self.acqmodel.signals.group_finished.connect(self.on_stop)
        self.acqmodel.signals.samplerateChanged.connect(self.update_generation_rate)
        
        for stim in self.explore_stimuli:
            self.ui.parameter_stack.addWidget(stim.showEditor())
            self.ui.explore_stim_type_cmbbx.addItem(stim.name)

        self.ui.thresh_lnedt.returnPressed.connect(self.set_plot_thresh)        
        
        self.current_operation = None

        # update GUI to reflect loaded values
        self.set_plot_thresh()

        # set up wav file directory finder paths
        self.exvocal = self.ui.parameter_stack.widget_for_name("Vocalization")
        self.exvocal.setRootDirs(self.wavrootdir, self.filelistdir)
        self.exvocal.filelist_view.doubleClicked.connect(self.wavfile_selected)

        # always show plots on load
        self.ui.plot_dock.setVisible(True)
        self.ui.psth_dock.setVisible(True)

    def on_start(self):
        # set plot axis to appropriate limits
        # first time set up data file
        if self.acqmodel.datafile is None:
            self.acqmodel.set_save_params(self.savefolder, self.savename)
            self.acqmodel.create_data_file()
        self.ui.plot_dock.setWidget(self.ui.display)
        if not self.verify_inputs():
            return
        self.ui.running_label.setText(u"RUNNING")
        self.ui.running_label.setPalette(GREEN)
        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            self.run_explore()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            self.run_chart()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_protocol':
            self.run_protocol()
        else: 
            raise Exception("unrecognized tab selection")

    def on_update(self):
        aochan = self.ui.aochan_box.currentText()
        aichan = self.ui.aichan_box.currentText()
        acq_rate = self.ui.aisr_spnbx.value()*self.fscale

        winsz = float(self.ui.windowsz_spnbx.value())*self.tscale
        binsz = float(self.ui.binsz_spnbx.value())*self.tscale

        nbins = np.ceil(winsz/binsz)
        bin_centers = (np.arange(nbins)*binsz)+(binsz/2)
        self.ui.psth.set_bins(bin_centers)
        self.acqmodel.set_params(aochan=aochan, aichan=aichan,
                                 acqtime=winsz, aisr=acq_rate,
                                 binsz=binsz)

        self.ui.display.set_xlimits((0,winsz))
        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            self.acqmodel.clear_explore_stimulus()
            nreps = self.ui.ex_nreps_spnbx.value()
            gen_rate = self.ui.aosr_spnbx.value()*self.fscale
            self.acqmodel.set_explore_samplerate(gen_rate)
            self.acqmodel.set_params(nreps=nreps)
            # each widget should be in charge of putting its own stimulus together
            stim_index = self.ui.explore_stim_type_cmbbx.currentIndex()
            stim_widget = self.ui.parameter_stack.widget(stim_index)
            stim_widget.saveToObject()
            # have model sort all signals stuff out?
            signal = self.acqmodel.set_stim_by_index(stim_index)
            freq, spectrum = calc_spectrum(signal, gen_rate)
            timevals = np.arange(len(signal)).astype(float)/gen_rate
            self.ui.display.set_nreps(nreps)
            self.ui.display.update_fft(freq, spectrum)
            self.ui.display.update_signal(timevals, signal)
        if self.ui.tab_group.currentWidget().objectName() == 'tab_chart':
            return winsz, acq_rate
            
    def on_stop(self):
        if self.current_operation == 'chart':
            self.acqmodel.stop_chart()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            self.acqmodel.halt()

        self.current_operation = None
        self.live_lock.unlock()
        self.ui.running_label.setText(u"OFF")
        self.ui.running_label.setPalette(RED)
        self.ui.start_btn.setEnabled(True)
        self.ui.start_btn.setText('Start')
        self.ui.start_btn.clicked.disconnect()
        self.ui.start_btn.clicked.connect(self.on_start)


    def run_chart(self):
        winsz, acq_rate = self.on_update()
        # change plot to scrolling plot
        self.scrollplot.set_windowsize(winsz)
        self.scrollplot.set_sr(acq_rate)
        self.ui.plot_dock.setWidget(self.scrollplot)

        self.current_operation = 'chart'
        self.acqmodel.start_chart()

    def update_chart(self, data):
        self.scrollplot.append_data(data)

    def update_generation_rate(self, fs):
        self.ui.aosr_spnbx.setValue(fs*self.tscale)

    def run_explore(self):
        self.ui.start_btn.setText('Update')
        self.ui.start_btn.clicked.disconnect()
        self.ui.start_btn.clicked.connect(self.on_update)
        # make this an enum!!!!
        self.current_operation = 'explore'
        reprate = self.ui.reprate_spnbx.value()
        interval = (1/reprate)*1000

        self.on_update()            
        self.acqmodel.run_explore(interval)

    def run_protocol(self):

        self.ui.start_btn.setEnabled(False)
        self.current_operation = 'protocol'

        reprate = self.ui.reprate_spnbx.value()
        interval = (1/reprate)*1000
        
        self.on_update()

        self.acqmodel.run_protocol(interval)

    def display_stim(self, stimdeets, times, signal, xfft, yfft):
        print "display stim"
        self.ui.display.update_signal(times, signal)
        self.ui.display.update_fft(xfft, yfft)

    def display_response(self, times, response):
        # print "display reponse"
        self.ui.display.update_spiketrace(times, response)

    def display_raster(self, bins, repnum):
        # convert to times for raster
        binsz = float(self.ui.binsz_spnbx.value())*self.tscale
        bin_times = (np.array(bins)*binsz)+(binsz/2)
        self.ui.display.add_raster_points(bin_times, repnum)
        self.ui.psth.append_data(bins, repnum)

    def trace_done(self, total_spikes, avg_count, avg_latency, avg_rate):
        self.ui.display.clear_raster()
        self.ui.psth.clear_data()
        self.ui.spike_total_lbl.setText(str(total_spikes))
        self.ui.spike_avg_lbl.setText(str(avg_count))
        self.ui.spike_latency_lbl.setText(str(avg_latency*1000))
        self.ui.spike_rate_lbl.setText(str(avg_rate))

    def launch_save_dlg(self):
        field_vals = {u'savefolder' : self.savefolder, u'savename' : self.savename, u'saveformat' : self.saveformat}
        dlg = SavingDialog(default_vals = field_vals)
        if dlg.exec_():
            savefolder, savename, saveformat = dlg.values()
            self.savefolder = savefolder
            self.savename = savename
            self.saveformat = saveformat

    def launch_calibration_dlg(self):
        pass

    def launch_scale_dlg(self):
        field_vals = {u'fscale' : self.fscale, u'tscale' : self.tscale}
        dlg = ScaleDialog(default_vals=field_vals)
        if dlg.exec_():
            fscale, tscale = dlg.values()
            self.update_unit_labels(tscale, fscale)

    def launch_specgram_dlg(self):
        dlg = SpecDialog(default_vals=self.spec_args)
        if dlg.exec_():
            argdict = dlg.values()
            SpecWidget().set_spec_args(**argdict)
            self.spec_args = argdict

    def wavfile_selected(self, model_index):
        """ On double click of wav file, load into display """
        # display spectrogram of file
        spath = self.exvocal.current_wav_file

        self.ui.display.update_spec(spath)
        sr, wavdata = wv.read(spath)

        freq, spectrum = calc_spectrum(wavdata,sr)

        self.ui.display.update_fft(freq, spectrum)
        t = np.linspace(0,(float(len(wavdata))/sr), len(wavdata))
        print 'stim time lims', t[0], t[-1]
        self.ui.display.update_signal(t, wavdata)

        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            winsz = float(self.ui.windowsz_spnbx.value())*self.tscale

            self.ui.display.set_xlimits((0,winsz))

    def update_thresh(self, thresh):
        self.ui.thresh_lnedt.setText(str(thresh))
        self.acqmodel.set_threshold(thresh)

    def set_plot_thresh(self):
        thresh = float(self.ui.thresh_lnedt.text())
        self.ui.display.spiketrace_plot.set_threshold(thresh)
        self.acqmodel.set_threshold(thresh)

    def show_display(self):
        self.ui.plot_dock.setVisible(True)

    def show_psth(self):
        self.ui.psth_dock.setVisible(True)

    def set_status_msg(self, status):
        self.statusBar().showMessage(status)

    def closeEvent(self,event):
        # stop any tasks that may be running
        self.on_stop()
        self.acqmodel.close_data()
        super(MainWindow, self).closeEvent(event)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow("controlinputs.json")
    myapp.show()
    sys.exit(app.exec_())