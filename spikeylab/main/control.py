import spikeylab

import sys, os
import scipy.io.wavfile as wv
import numpy as np
import threading
import logging
import time

from PyQt4 import QtCore, QtGui

from spikeylab.io.daq_tasks import get_ao_chans, get_ai_chans

from spikeylab.dialogs import SavingDialog, ScaleDialog, SpecDialog, CalibrationDialog
from spikeylab.main.acquisition_manager import AcquisitionManager
from spikeylab.tools.audiotools import calc_spectrum, get_fft_peak
from spikeylab.plotting.pyqtgraph_widgets import ProgressWidget
from spikeylab.tools.qthreading import GenericThread, GenericObject, SimpleObject, Thread
from spikeylab.plotting.pyqtgraph_widgets import FFTWidget
from spikeylab.data.dataobjects import load_calibration_file
from spikeylab.plotting.pyqtgraph_widgets import SimplePlotWidget

from controlwindow import ControlWindow

RED = QtGui.QPalette()
RED.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
GREEN = QtGui.QPalette()
GREEN.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
BLACK = QtGui.QPalette()
BLACK.setColor(QtGui.QPalette.Foreground,QtCore.Qt.black)

DEVNAME = "PCI-6259"

class MainWindow(ControlWindow):
    def __init__(self, inputs_filename=''):
        # set up model and stimlui first, 
        # as saved configuration relies on this
        self.acqmodel = AcquisitionManager()
        
        # get stimuli editor widgets
        self.explore_stimuli = self.acqmodel.stimuli_list()
        
        # auto generated code intialization
        ControlWindow.__init__(self, inputs_filename)
        
        self.ui.start_btn.clicked.connect(self.on_start)
        self.ui.stop_btn.clicked.connect(self.on_stop)
        self.ui.start_chart_btn.clicked.connect(self.on_start_chart)
        self.ui.stop_chart_btn.clicked.connect(self.on_stop_chart)

        cnames = get_ao_chans(DEVNAME.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(DEVNAME.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.running_label.setPalette(RED)

        self.apply_calibration = False
        self.calpeak = None

        self.live_lock = QtCore.QMutex()

        # self.display.spiketrace_plot.traits.signals.threshold_updated.connect(self.update_thresh)
        self.display.threshold_updated.connect(self.update_thresh)
        self.display.colormap_changed.connect(self.relay_cmap_change)

        self.ui.protocolView.setModel(self.acqmodel.protocol_model())
        self.ui.calibration_widget.setCurveModel(self.acqmodel.calibration_stimulus('tone'))

        self.acqmodel.signals.response_collected.connect(self.display_response)
        self.acqmodel.signals.calibration_response_collected.connect(self.display_calibration_response)
        self.acqmodel.signals.average_response.connect(self.display_db_result)
        self.acqmodel.signals.spikes_found.connect(self.display_raster)
        self.acqmodel.signals.trace_finished.connect(self.trace_done)
        self.acqmodel.signals.stim_generated.connect(self.display_stim)
        self.acqmodel.signals.warning.connect(self.set_status_msg)
        self.acqmodel.signals.ncollected.connect(self.update_chart)
        self.acqmodel.signals.current_trace.connect(self.report_progress)
        self.acqmodel.signals.current_rep.connect(self.report_rep)
        self.acqmodel.signals.group_finished.connect(self.on_group_done)
        self.acqmodel.signals.samplerateChanged.connect(self.update_generation_rate)
        self.acqmodel.signals.calibration_file_changed.connect(self.update_calfile)
        self.acqmodel.signals.tuning_curve_started.connect(self.spawn_tuning_curve)
        self.acqmodel.signals.tuning_curve_response.connect(self.display_tuning_curve)

        self.ui.thresh_spnbx.valueChanged.connect(self.set_plot_thresh)        
        self.ui.windowsz_spnbx.valueChanged.connect(self.set_calibration_duration)
        self.ui.binsz_spnbx.setKeyboardTracking(False)
        self.ui.windowsz_spnbx.setKeyboardTracking(False)
        self.ui.ex_nreps_spnbx.setKeyboardTracking(False)
        self.ui.thresh_spnbx.setKeyboardTracking(False)

        self.active_operation = None

        # update GUI to reflect loaded values
        self.set_plot_thresh()
        self.set_calibration_duration()

        # set up wav file directory finder paths
        self.exvocal = self.ui.parameter_stack.widget_for_name("Vocalization")
        self.exvocal.filelist_view.doubleClicked.connect(self.wavfile_selected)
        self.selected_wav_file = self.exvocal.current_wav_file

        # always start in windowed mode
        self.mode_toggled('Windowed')
        self.prev_tab = self.ui.tab_group.tabText(self.ui.tab_group.currentIndex()).lower()
        # always show plots on load
        self.ui.plot_dock.setVisible(True)
        self.ui.psth_dock.setVisible(True)

        self.ui.stop_btn.setEnabled(False)
        self.ui.stop_chart_btn.setEnabled(False)

        logger = logging.getLogger('main')
        handlers = logger.handlers
        # dig out the UI handler to assign text edit ... a better way?
        for h in handlers:
            if h.get_name() == 'ui':
                h.set_widget(self.ui.log_txedt)
                break
        logger.info("**** Program started "+time.strftime("%d-%m-%Y")+ ' ****')

        self.calpeak = None

    def connect_updatable(self, connect):
        if connect:
            self.ui.start_btn.clicked.disconnect()
            self.ui.start_btn.clicked.connect(self.on_update)
            self.ui.binsz_spnbx.valueChanged.connect(self.on_update)
            self.ui.windowsz_spnbx.valueChanged.connect(self.on_update)
            self.ui.ex_nreps_spnbx.valueChanged.connect(self.on_update)
            for editor in self.ui.parameter_stack.widgets():
                editor.valueChanged.connect(self.on_update)
        else:
            try:
                self.ui.ex_nreps_spnbx.valueChanged.disconnect()
                self.ui.binsz_spnbx.valueChanged.disconnect()
                self.ui.windowsz_spnbx.valueChanged.disconnect()
                # this should always remain connected 
                self.ui.windowsz_spnbx.valueChanged.connect(self.set_calibration_duration)
                self.ui.start_btn.clicked.disconnect()
                self.ui.start_btn.clicked.connect(self.on_start)
                for editor in self.ui.parameter_stack.widgets():
                    editor.valueChanged.disconnect()
            except TypeError:
                # disconnecting already disconnected signals throws TypeError
                pass

    def on_start(self):
        # set plot axis to appropriate limits
        # first time set up data file
        if not self.verify_inputs('windowed'):
            return

        # disable the components we don't want changed amid generation
        self.ui.aochan_box.setEnabled(False)
        self.ui.aisr_spnbx.setEnabled(False)
        reprate = self.ui.reprate_spnbx.setEnabled(False)
        self.ui.stop_btn.setEnabled(True)
        self.plot_progress = False

        if self.current_mode == 'windowed':
            if self.acqmodel.datafile is None:
                self.acqmodel.set_save_params(self.savefolder, self.savename)
                self.acqmodel.create_data_file()
            self.ui.aichan_box.setEnabled(False)
            # FIX ME:
            if self.ui.plot_dock.current() == 'calibration':
                self.ui.plot_dock.switch_display('standard')
            self.ui.running_label.setText(u"RECORDING")
            self.ui.running_label.setPalette(GREEN)

        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            self.run_explore()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_protocol':
            self.run_protocol()
        elif self.ui.tab_group.currentWidget().objectName() == 'tab_calibrate':
            self.acqmodel.set_calibration_reps(self.ui.calibration_widget.ui.nreps_spnbx.value())
            self.run_calibration()
        else: 
            raise Exception("unrecognized tab selection")

    def on_start_chart(self):
        if not self.verify_inputs('chart'):
            return

        if self.acqmodel.datafile is None:
            self.acqmodel.set_save_params(self.savefolder, self.savename)
            self.acqmodel.create_data_file()

        self.run_chart()
        self.ui.running_label.setText(u"RECORDING")
        self.ui.running_label.setPalette(GREEN)
        self.ui.start_chart_btn.setEnabled(False)
        self.ui.aichan_box.setEnabled(False)
        self.ui.aisr_spnbx.setEnabled(False)
        self.ui.stop_chart_btn.setEnabled(True)
        self.ui.windowsz_spnbx.valueChanged.connect(self.update_scolling_windowsize)

    def on_update(self):
        if not self.verify_inputs(self.active_operation):
            return
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
        self.binsz = binsz

        self.display.set_xlimits((0,winsz))
        # update or clear spec
        if str(self.ui.explore_stim_type_cmbbx.currentText().lower()) == 'vocalization':
            # don't update file - revert to last double clicked
            stim_index = self.ui.explore_stim_type_cmbbx.currentIndex()
            stim_widget = self.ui.parameter_stack.widget(stim_index)
            if stim_widget.current_wav_file != self.selected_wav_file:
                stim_widget.component().setFile(self.selected_wav_file)
            self.display.show_spec(self.selected_wav_file)
        else:
            self.display.update_spec(None)
        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            nreps = self.ui.ex_nreps_spnbx.value()

            self.acqmodel.set_params(nreps=nreps)
            
            # have model sort all signals stuff out?
            stim_index = self.ui.explore_stim_type_cmbbx.currentIndex()
            signal, ovld = self.acqmodel.set_stim_by_index(stim_index)
            # print 'stim signal', len(signal)
            self.ui.over_atten_lbl.setNum(ovld)
            if ovld > 0:
                self.ui.over_atten_lbl.setPalette(RED)
            else:
                self.ui.over_atten_lbl.setPalette(BLACK)

            gen_rate = self.acqmodel.explore_genrate()
            self.ui.aosr_spnbx.setValue(gen_rate/self.fscale)
            self.display_stim(signal, gen_rate)
            self.display.set_nreps(nreps)
        if self.current_mode == 'chart':
            return winsz, acq_rate
            
    def on_stop(self):
        self.acqmodel.halt() # stops generation, and acquistion if linked
        if self.current_mode == 'windowed':
            self.active_operation = None
            self.live_lock.unlock()
            self.ui.running_label.setText(u"OFF")
            self.ui.running_label.setPalette(RED)
            self.ui.aichan_box.setEnabled(True)
            self.connect_updatable(False)
        self.ui.start_btn.setEnabled(True)
        self.ui.start_btn.setText('Start')
        self.ui.stop_btn.clicked.disconnect()
        self.ui.stop_btn.clicked.connect(self.on_stop)


        self.ui.aisr_spnbx.setEnabled(True)
        self.ui.aochan_box.setEnabled(True)
        reprate = self.ui.reprate_spnbx.setEnabled(True)
        self.ui.stop_btn.setEnabled(False)

    def on_stop_chart(self):
        self.acqmodel.stop_chart()
        self.ui.start_chart_btn.setEnabled(True)
        self.active_operation = None
        self.live_lock.unlock()
        self.ui.running_label.setText(u"OFF")
        self.ui.running_label.setPalette(RED)
        self.ui.aichan_box.setEnabled(True)
        self.ui.aisr_spnbx.setEnabled(True)
        self.ui.stop_chart_btn.setEnabled(False)
        self.ui.windowsz_spnbx.valueChanged.disconnect()
        self.ui.windowsz_spnbx.valueChanged.connect(self.set_calibration_duration)

    def on_group_done(self, halted):
        if self.active_operation == 'calibration':
            #maybe don't call this at all if save is false?
            save = self.ui.calibration_widget.ui.savecal_ckbx.isChecked() and not halted
            calname = self.acqmodel.process_calibration(save)
            if not self.ui.calibration_widget.is_tone_cal() and save:
                attenuations, freqs = load_calibration_file(calname, self.calvals['calf'])
                self.pw = SimplePlotWidget(freqs, attenuations, parent=self)
                self.pw.setWindowFlags(QtCore.Qt.Window)
                self.pw.set_labels('Frequency', 'Attenuation', 'Calibration Curve')
                self.pw.show()
        self.on_stop()

    def run_chart(self):
        winsz, acq_rate = self.on_update()
        # change plot to scrolling plot
        self.scrollplot.set_windowsize(winsz)
        self.scrollplot.set_sr(acq_rate)
        self.ui.plot_dock.switch_display('chart')

        # self.active_operation = 'chart'
        self.acqmodel.start_chart()

    def update_scolling_windowsize(self):
        winsz = float(self.ui.windowsz_spnbx.value())*self.tscale
        self.scrollplot.set_windowsize(winsz)

    def update_chart(self, stim_data, response_data):
        self.scrollplot.append_data(stim_data, response_data)

    def update_generation_rate(self, fs):
        self.ui.aosr_spnbx.setValue(fs/self.fscale)

    def run_explore(self):
        self.ui.start_btn.setText('Update')
        
        self.connect_updatable(True)

        self.active_operation = 'explore'
        reprate = self.ui.reprate_spnbx.value()
        interval = (1/reprate)*1000

        self.on_update()            
        self.acqmodel.run_explore(interval)

    def run_protocol(self):
        self.display.update_spec(None)

        self.ui.start_btn.setEnabled(False)
        self.active_operation = 'protocol'

        reprate = self.ui.reprate_spnbx.value()
        interval = (1/reprate)*1000
        
        self.on_update()
        if self.current_mode == 'windowed':
            overload = self.acqmodel.setup_protocol(interval)
            if np.any(np.array(overload) > 0):
                answer = QtGui.QMessageBox.question(self, 'Oh Dear!', 
                                'Stimuli in test list are over the maximum allowable voltage output. They will be rescaled with a maximum undesired attenuation of {:.2f}dB.\n \
                                Do you want to continue?'.format(np.amax(overload)),
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if answer == QtGui.QMessageBox.No:
                    self.on_stop()
                    return

            self.acqmodel.run_protocol()
        else:
            self.acqmodel.run_chart_protocol(interval)

    def run_calibration(self):
        self.ui.start_btn.setEnabled(False)
        self.active_operation = 'calibration'

        self.ui.stop_btn.clicked.disconnect()
        self.ui.stop_btn.clicked.connect(self.acqmodel.halt)

        stim_index = self.ui.calibration_widget.current_index()
        self.acqmodel.set_calibration_by_index(stim_index)

        if self.ui.calibration_widget.is_tone_cal():
            frequencies, intensities = self.acqmodel.calibration_range()
            self.livecurve = ProgressWidget(list(frequencies), list(intensities))
            self.livecurve.set_labels('calibration')
            self.ui.progress_dock.setWidget(self.livecurve)
            self.ui.plot_dock.switch_display('calibration')
        else:
            self.ui.plot_dock.switch_display('calexp')
            
        reprate = self.ui.reprate_spnbx.value()
        interval = (1/reprate)*1000

        self.on_update()
        self.acqmodel.run_calibration(interval, self.ui.calibration_widget.ui.applycal_ckbx.isChecked())

    def display_response(self, times, response):
        # print 'response signal', len(response)
        if len(times) != len(response):
            print "WARNING: times and response not equal"
        if self.ui.plot_dock.current() == 'standard':
            self.display.update_spiketrace(times, response)
        elif self.ui.plot_dock.current() == 'calexp':
                
            rms = np.sqrt(np.mean(pow(response,2)))
            # vmax = np.amax(response) - np.mean(response) 
            vmax = rms*1.414
            # print 'abs max', vmax, 'rms', rms, 'cheat', vmax*0.707
            masterdb = 94 + (20.*np.log10(rms/(0.004)))
            masterdb2 = 94 + (20.*np.log10(vmax/(0.004)))
            self.ui.dblevel_lbl.setNum(masterdb)
            self.ui.dblevel_lbl2.setNum(masterdb2)
            sr = self.ui.aisr_spnbx.value()*self.fscale
            freq, signal_fft = calc_spectrum(response, sr)
            if False:
                spectrum = self.calvals['caldb'] + (20.*np.log10(signal_fft/peak))
            else:
                spectrum = signal_fft
            self.ui.dblevel_lbl3.setNum(np.amax(spectrum))
            spectrum[0] = 0
            self.extended_display.update_signal(times, response, plot='response')
            self.extended_display.update_fft(freq, spectrum, plot='response')
            self.extended_display.update_spec(response, sr, plot='response')

    def display_calibration_response(self, fdb, spectrum, freqs, spec_peak, vmax):
        # display fft here
        f, db = fdb
        # print 'response f', f, 'db', db
        spectrum[0] = 0
        spec_max, max_freq = get_fft_peak(spectrum, freqs)
        if spec_max != spec_peak:
            print 'max freq', max_freq, 'current', f
            self.ui.calibration_widget.ui.fftf_lbl.setPalette(RED)
        else:
            self.ui.calibration_widget.ui.fftf_lbl.setPalette(BLACK)

        self.ui.calibration_widget.ui.aiv_lbl.setNum(vmax)
        self.ui.calibration_widget.ui.fftpeak_lbl.setNum(spec_max)
        self.ui.calibration_widget.ui.fftf_lbl.setNum(spec_peak)
        self.ui.calibration_widget.ui.flabel.setNum(f)
        self.ui.calibration_widget.ui.dblabel.setNum(db)
        self.calibration_display.update_in_fft(freqs, spectrum)


    def display_db_result(self, f, db, resultdb):
        try:
            self.ui.calibration_widget.ui.db_lbl.setNum(resultdb)
            self.livecurve.set_point(f,db,resultdb)
        except:
            print u"WARNING : Problem drawing to calibration plot"
            raise

    def spawn_tuning_curve(self, frequencies, intensities, plot_type):
        self.livecurve = ProgressWidget(frequencies, intensities)
        self.livecurve.set_labels(plot_type)

        # self.livecurve.show()
        self.ui.progress_dock.setWidget(self.livecurve)
        self.plot_progress = True

    def display_tuning_curve(self, f, db, spike_count):
        if self.plot_progress:
            self.livecurve.set_point(f, db, spike_count)

    def display_raster(self, bins, repnum):
        # convert to times for raster
        if repnum == 0:
            self.ui.psth.clear_data()
            self.display.clear_raster()
        if len(bins) > 0:
            binsz = self.binsz
            bin_times = (np.array(bins)*binsz)+(binsz/2)
            self.display.add_raster_points(bin_times, repnum)
            self.ui.psth.append_data(bins, repnum)
            
    def display_stim(self, signal, fs):
        freq, spectrum = calc_spectrum(signal, fs)
        timevals = np.arange(len(signal)).astype(float)/fs
        if self.active_operation == 'calibration':
            if self.ui.plot_dock.current() == 'calexp':
                self.extended_display.update_signal(timevals, signal, plot='stim')
                self.extended_display.update_fft(freq, spectrum, plot='stim')
                self.extended_display.update_spec(signal, fs, plot='stim')
            else:
                self.calibration_display.update_out_fft(freq, spectrum)
                self.ui.calibration_widget.ui.avo_lbl.setText(str(np.amax(signal)))
        else:
            if self.ui.plot_dock.current() == 'standard':
                self.display.update_signal(timevals, signal)
                self.display.update_fft(freq, spectrum)
            elif self.ui.plot_dock.current() == 'calexp':
                self.extended_display.update_signal(timevals, signal, plot='stim')
                self.extended_display.update_fft(freq, spectrum, plot='stim')
                self.extended_display.update_spec(signal, fs, plot='stim')

    def report_progress(self, itest, itrace, stim_info):
        self.ui.test_num.setText(str(itest))
        self.ui.trace_num.setText(str(itrace))
        stim_types = [comp['stim_type'] for comp in stim_info['components']]
        # print 'stim_types', stim_types
        if len(set(stim_types)) == 1:
            self.ui.trace_type.setText(stim_types[0])
        else:
            self.ui.trace_type.setText('who knows?')
        self.ui.trace_info.setText(" A 500g jar of honey represents about ten million trips from the hive to flowers and back again.")

    def report_rep(self, irep):
        self.ui.rep_num.setText(str(irep))

    def trace_done(self, total_spikes, avg_count, avg_latency, avg_rate):
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
        dlg = CalibrationDialog(default_vals = self.calvals, fscale=self.fscale)
        if dlg.exec_():
            values = dlg.values()
            self.acqmodel.set_params(**values)
            if values['use_calfile']:
                self.acqmodel.set_calibration(values['calfile'], values['calf'], values['frange'])
            else:
                self.acqmodel.set_calibration(None)
            self.calvals = values

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
            self.display.set_spec_args(**argdict)
            self.exvocal.set_spec_args(**argdict)
            QtGui.QApplication.processEvents()
            self.spec_args = argdict

    def update_calfile(self, filename):
        self.calvals['calfile'] = filename
        self.calvals['use_calfile'] = True

    def wavfile_selected(self, model_index):
        """ On double click of wav file, load into display """
        # display spectrogram of file
        spath = self.exvocal.current_wav_file

        self.display.update_spec(spath)
        sr, wavdata = wv.read(spath)
        self.display_stim(wavdata, sr)

        if self.ui.tab_group.currentWidget().objectName() == 'tab_explore':
            winsz = float(self.ui.windowsz_spnbx.value())*self.tscale

            self.display.set_xlimits((0,winsz))
        self.selected_wav_file = spath
        self.on_update()

    def relay_cmap_change(self, cmap):
        self.exvocal.update_colormap()
        self.spec_args['colormap'] = cmap

    def set_calibration_duration(self):
        winsz = float(self.ui.windowsz_spnbx.value())
        # I shouldn't have to do both of these...
        self.acqmodel.set_calibration_duration(winsz*self.tscale)
        self.ui.calibration_widget.set_duration(winsz)

    def update_thresh(self, thresh):
        self.ui.thresh_spnbx.setValue(thresh)
        self.acqmodel.set_threshold(thresh)

    def set_plot_thresh(self):
        thresh = self.ui.thresh_spnbx.value()
        self.display.spiketrace_plot.set_threshold(thresh)
        self.acqmodel.set_threshold(thresh)

    def tab_changed(self, tab_index):
        if self.ui.tab_group.tabText(tab_index).lower() == 'calibration':
            self.stashed_aisr = self.ui.aisr_spnbx.value()
            self.ui.aisr_spnbx.setValue(self.acqmodel.calibration_genrate())
            self.ui.aisr_spnbx.setEnabled(False)
        elif self.prev_tab == 'calibration':
            self.ui.aisr_spnbx.setEnabled(True)
            self.ui.aisr_spnbx.setValue(self.stashed_aisr)
        self.prev_tab = self.ui.tab_group.tabText(tab_index).lower()

    def mode_toggled(self, mode):
        self.current_mode = mode.lower()
        if self.current_mode == "windowed":
            self.ui.start_chart_btn.hide()
            self.ui.stop_chart_btn.hide()
        elif self.current_mode == "chart":
            self.ui.stop_chart_btn.show()
            self.ui.start_chart_btn.show()
        else:
            raise Exception('unknown acquistion mode '+mode)

    def save_explore_toggled(self, save):
        self.save_explore = save

    def show_display(self):
        self.ui.plot_dock.setVisible(True)

    def show_psth(self):
        self.ui.psth_dock.setVisible(True)

    def set_status_msg(self, status):
        self.statusBar().showMessage(status)

    def show_progress(self):
        self.ui.progress_dock.setVisible(True)

    def show_log(self):
        self.ui.log_dock.setVisible(True)

    def closeEvent(self,event):
        # stop any tasks that may be running
        self.on_stop()
        self.acqmodel.close_data()
        super(MainWindow, self).closeEvent(event)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow("controlinputs.json")
    app.setActiveWindow(myapp)
    myapp.show()
    sys.exit(app.exec_())