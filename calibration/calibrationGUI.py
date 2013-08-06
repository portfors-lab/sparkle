from __future__ import division
from __future__ import division
from __future__ import division
from __future__ import division
from __future__ import division
from __future__ import division
from __future__ import division
from __future__ import division
import sys, os
import time
import pickle
import threading

from PyQt4 import QtCore, QtGui

import numpy as np

from audiolab.io.daq_tasks import *
from audiolab.tools.audiotools import *
from audiolab.plotting.plotz import *
from audiolab.plotting.defined_plots import *
from audiolab.config.info import caldata_filename, calfreq_filename

#this package
from calform import Ui_CalibrationWindow
from disp_dlg import DisplayDialog
from scale_dlg import ScaleDialog
from saving_dlg import SavingDialog
from calibration import TonePlayer, ToneCurve
from qthreading import GenericThread, WorkerSignals

#defauts used only if user data not saved
AIPOINTS = 100
CALDB = 100
CALV = 0.175
CALF = int(15000)
DBFACTOR = 20
CALHACK = 0.136
NBPATH = u'C:\\Users\\amy.boyle\\src\\notebooks\\'

XLEN = 5 #seconds, also not used?
SAVE_DATA_CHART = False
SAVE_DATA_TRACES = False
SAVE_FFT_DATA = False
VERBOSE = False
SAVE_OUTPUT = False
PRINT_WARNINGS = False

class CalibrationWindow(QtGui.QMainWindow):
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
        self.red = QtGui.QPalette()
        self.red.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
        self.green = QtGui.QPalette()
        self.green.setColor(QtGui.QPalette.Foreground,QtCore.Qt.green)
        self.ui.running_label.setPalette(self.red)

        self.display = None
        self.ainpts = AIPOINTS # gets overriden (hopefully)
        
        self.fscale = 1000
        self.tscale = 0.001

        self.caldb = None
        self.calv = 0.1
        self.calf = None

        self.savefolder = NBPATH
        self.savename = u"cal"
        self.saveformat = u'npy'

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

                # tab 2
                self.ui.freq_start_spnbx.setValue(inlist[10])
                self.ui.freq_stop_spnbx.setValue(inlist[11])
                self.ui.freq_step_spnbx.setValue(inlist[12])
                self.ui.db_start_spnbx.setValue(inlist[13])
                self.ui.db_stop_spnbx.setValue(inlist[14])
                self.ui.db_step_spnbx.setValue(inlist[15])
                self.ui.dur_spnbx_2.setValue(inlist[16])
                self.ui.risefall_spnbx_2.setValue(inlist[17])
                self.ui.reprate_spnbx.setValue(inlist[18])
                self.ui.sr_spnbx_2.setValue(inlist[19])
                self.ui.nreps_spnbx.setValue(inlist[20])

                self.caldb = inlist[21]
                self.calv = inlist[22]
                self.calf = inlist[23]
                self.savefolder = inlist[24]
                self.savename = inlist[25]
                self.saveformat = inlist[26]
            except:
                print u"failed to find all defaults"
                #raise

        self.set_interval_min()
        # lock for talking to the daq
        self.daq_lock = QtCore.QMutex()
        # lock for updating/ reading stimulus (for on-the-fly gen)
        self.stim_lock = QtCore.QMutex()
        # lock for saving to acquired data structure
        self.response_data_lock = QtCore.QMutex()
        # lock for live acquisition vs. processing data 
        # -- maybe a better way to do this with signals?
        self.live_lock = QtCore.QMutex()
        
        self.apply_calibration = 0

        self.daq_timer = None
        
        self.current_operation = None

        self.acq_thread = None

        self.signals = WorkerSignals()
        self.signals.done.connect(self.display_response)
        self.signals.curve_finished.connect(self.process_caldata)
        self.signals.update_stim_display.connect(self.stim_display)
        self.signals.read_collected.connect(self.calc_spectrum)

        print u'save format ',self.saveformat

    def on_start(self):

        if not self.verify_inputs_valid():
            return
       
        aochan = str(self.ui.aochan_box.currentText())
        aichan = str(self.ui.aichan_box.currentText())

        # depending on currently displayed tab, present
        # tuning curve, or on-the-fly modifyable tone
        if SAVE_OUTPUT:
            self.tone_array = []

        self.apply_calibration = self.ui.applycal_ckbx.isChecked()
        self.save_as_calibration = self.ui.savecal_ckbx.isChecked()

        if self.apply_calibration:
            calibration_vector = np.load(os.path.join(caldata_filename()))
            calibration_freqs = np.load(os.path.join(calfreq_filename()))

        self.halt = False

        self.ngenerated = 0
        self.nacquired = 0

        if self.ui.tabs.currentIndex() == 0 :
            if self.live_lock.tryLock():
                # on the fly
                self.current_operation = 0

                self.ndata = 0
                self.current_line_data = []

                if SAVE_FFT_DATA:
                    self.full_fft_data = []

                try:
                        
                    # write to and start generation task, so it is ready to fire immediately
                    # when the command is given.
                    self.toneplayer = TonePlayer((self.caldb,self.calv))
                    if self.apply_calibration:
                        self.toneplayer.set_calibration(calibration_vector, calibration_freqs)

                    # gets info from UI and creates tone
                    self.update_stim()
                    interval = self.interval

                    self.toneplayer.start(aochan,aichan)

                    self.ui.running_label.setPalette(self.green)
                    self.ui.running_label.setText(u"RUNNING")

                    # spin off a thread that runs a continuous loop, with
                    # an appropriate, adjusted, sleep time between loops

                    self.start_time = time.time()
                    # set last tick to expired time, so first loop iteration doesn't sleep
                    self.last_tick = self.start_time - (interval/self.tscale) 
                    self.acq_thread = threading.Thread(target=self.finite_worker)
                    self.acq_thread.start()

                except:
                    print u'ERROR! TERMINATE!'
                    self.on_stop
                    raise
                
            else:
                print u"start pressed when task already running, updating stimulus..."
                self.update_stim()
 
        else:
            if self.live_lock.tryLock():

                # check that calf and caldb are defined
                if (self.caldb is None) or (self.calf is None):
                    # prompt the user to enter them, if invalid
                    self.launch_display_dlg()

                    # if still not good values, abort
                    if (self.caldb is None) or (self.calf is None):
                        return

                # tuning curve style run-through
                self.current_operation = 1
                self.halt_curve = False

                # grey out interface during curve
                self.ui.tab_2.setEnabled(False)
                self.ui.start_button.setEnabled(False)
                self.ui.label4.setText(u"")

                self.ngenerated = 0
                self.nacquired = 0
            
                try:
                    #scale_factor = 1000
                    f_start = self.ui.freq_start_spnbx.value()*self.fscale
                    f_stop = self.ui.freq_stop_spnbx.value()*self.fscale
                    f_step = self.ui.freq_step_spnbx.value()*self.fscale
                    db_start = self.ui.db_start_spnbx.value()
                    db_stop = self.ui.db_stop_spnbx.value()
                    db_step = self.ui.db_step_spnbx.value()
                    dur = self.ui.dur_spnbx_2.value()*self.tscale
                    rft = self.ui.risefall_spnbx_2.value()*self.tscale
                    reprate = self.ui.reprate_spnbx.value()
                    sr = self.ui.sr_spnbx_2.value()*self.fscale
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
                        self.spawn_display()
                    self.display.show()

                    self.tonecurve = ToneCurve(dur, sr, rft, nreps, freqs, intensities, 
                                               (self.caldb, self.calv), calf=self.calf,
                                               filename=os.path.join(self.savefolder,self.savename+'.hdf5'))

                    if self.apply_calibration:
                        self.tonecurve.set_calibration(calibration_vector, calibration_freqs)

                    self.tonecurve.assign_signal(self.signals.done)
                    self.calval = self.tonecurve.arm(aochan,aichan)
                    self.ngenerated +=1

                    self.ui.running_label.setText(u"RUNNING")
                    self.ui.running_label.setPalette(self.green)

                    # save these lists for easier plotting later
                    self.freqs = freqs
                    self.intensities = intensities

                    self.livecurve = LiveCalPlot(freqs, intensities)
                    self.livecurve.show()

                    # save the start time and set last tick to expired, so first
                    # acquisition loop iteration executes immediately
                    self.start_time = time.time()
                    self.last_tick = self.start_time - (interval/1000)
                    self.acq_thread = threading.Thread(target=self.curve_worker)
                    self.acq_thread.start()                    

                except:
                    self.live_lock.unlock()
                    print u"handle curve set-up exception"
                    self.ui.tab_2.setEnabled(True)
                    self.ui.start_button.setEnabled(True)
                    raise
            else:
                print u"Operation already in progress"
        

    def curve_worker(self):

        while not self.halt:

            # this thread runs only for the turning curve
            # I don't know what I am suppose to type right now

            # calculate time since last interation and wait to acheive desired interval
            now = time.time()
            elapsed = (now - self.last_tick)*1000
            #print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
            if elapsed < self.interval:
                #print('sleep ', (self.interval-elapsed))
                time.sleep((self.interval-elapsed)/1000)
                now = time.time()
            elif elapsed > self.interval:
                print u"WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed)
            self.last_tick = now

            if not self.tonecurve.haswork():
                # no more work left in the queue, collect last stim written.
                self.halt = True
            else:
                self.ngenerated +=1

            tone, data, times, f, db = self.tonecurve.next()

            self.ui.flabel.setText(u"Frequency : %d" % (f))
            self.ui.dblabel.setText(u"Intensity : %d" % (db))

            self.ui.label0.setText(u"AO Vmax : %.5f" % (np.amax(abs(tone))))

            xfft, yfft = calc_spectrum(tone, self.tonecurve.player.get_samplerate())

            try:
                self.signals.update_stim_display.emit(times, tone, xfft, abs(yfft))
            except:
                print u"WARNING : Problem drawing stim to Window"

            #self.current_line_data = data
            #self.display_response(f,db)
            #self.signals.done.emit(f, db, data[:])

    def process_caldata(self):
        # saving can take a long time if there is alot of data, display indeterminate
        # progess bar so user doesn't think program froze
        progressdlg = QtGui.QProgressDialog(u"Saving data...", u"Abort", 0, 0, self)
        progressdlg.show()
        QtGui.QApplication.processEvents()
        resultant_dB = self.tonecurve.save_to_file(self.calf, self.savefolder, self.savename, 
                                                   keepcal=self.save_as_calibration, 
                                                   saveformat=self.saveformat)

        progressdlg.setLabel(QtGui.QLabel(u"Plotting data..."))
        QtGui.QApplication.processEvents()
        self.tonecurve.caldata.close()
        #plot_cal_curve(resultant_dB, self.freqs, self.intensities, self)
        progressdlg.close()


    def on_stop(self):
        print u'SENDER: ', self.sender()
        if self.current_operation == 0 : 
                
            self.ui.interval_spnbx.setEnabled(True)
            if not self.halt:
                self.ui.running_label.setText(u"STOPPING")

                self.halt = True

                self.acq_thread.join()
                self.ui.running_label.setText(u"BUSY")
                self.ui.running_label.setPalette(self.red)
                QtGui.QApplication.processEvents()
                self.save_speculative_data()
                self.toneplayer.stop()

        elif self.current_operation == 1:

            self.halt = True
            self.ui.tab_2.setEnabled(True)
            self.ui.start_button.setEnabled(True)
            # let thread finish and stop task
            if self.acq_thread is not None:
                self.acq_thread.join()
                self.tonecurve.stop()

            # if this funtion was called by user pushing button,
            # go ahead and close data file
            if isinstance(self.sender(), QtGui.QPushButton):
                self.tonecurve.caldata.close()
            
        else:
            print u"No task currently running"

        self.live_lock.unlock()
        self.ui.running_label.setText(u"OFF")
        self.ui.running_label.setPalette(self.red)

    def save_speculative_data(self):
        #print("locking")
        #self.live_lock.lock()
        if SAVE_OUTPUT:
            # due to the method of loading the write, the last tone in
            # tone array was never generated, so delete it
            del self.tone_array[-1]
            print u"saving output tones, shape : ", len(self.tone_array), u', ', len(self.tone_array[0])
            filename = OUTPUT_FNAME
            np.save(filename, self.tone_array)
        if SAVE_FFT_DATA:
            print u"saving fft traces, shape : ", len(self.full_fft_data), u', ', len(self.full_fft_data[0])
            filename = FFT_FNAME
            np.save(filename, self.full_fft_data)
        self.live_lock.unlock()

    def update_stim(self):
        f = self.ui.freq_spnbx.value()*self.fscale
        sr = self.ui.sr_spnbx.value()*self.fscale
        dur = self.ui.dur_spnbx.value()*self.tscale
        db = self.ui.db_spnbx.value()
        rft = self.ui.risefall_spnbx.value()*self.tscale
        aisr =  self.ui.aisr_spnbx.value()*self.fscale

        tone, timevals = self.toneplayer.set_tone(f,db,dur,rft,sr)
        
        npts = tone.size

        interval = self.ui.interval_spnbx.value()
        self.interval = interval

        #also plot stim FFT
        freq, spectrum = calc_spectrum(tone,sr)

        self.fdb = (f,db)

        self.statusBar().showMessage(u'npts: {}'.format(npts))
        print u'\n' + u'*'*40 + u'\n'

        self.ui.flabel.setText(u"Frequency : %d" % (f))
        self.ui.dblabel.setText(u"Intensity : %d" % (db))
        self.ui.label0.setText(u"AO Vmax : %.5f" % (np.amax(abs(tone))))

        print u"update_stim"
        # now update the display of the stim
        if self.display == None or not(self.display.active):
            self.spawn_display()
            
        self.stim_display(timevals, tone, freq, abs(spectrum))
        #self.display.ylim_auto([self.display.axs[2]])

    def spawn_display(self):
        self.display = AnimatedWindow(([],[]), ([],[]), 
                                      ([[],[]],[[],[]]), parent=self)
        self.display.show()
        # set axes limits appropriately
        self.display.axs[0].set_title(u"Stimulus")
        self.display.axs[0].set_xlim(0,2)
        self.display.axs[0].set_ylim(-10,10)
        self.display.axs[1].set_title(u"Response")
        self.display.axs[1].set_xlim(0,2)
        self.display.axs[1].set_ylim(-10,10)
        self.display.axs[2].set_title(u"FFTs")
        self.display.axs[2].set_xlim(0,200000)
        self.display.axs[1].lines[0].set_color(u'g')
        #self.display.canvas.draw()

    def stim_display(self, xdata, ydata, xfft, yfft):
        # hard coded for stim in axes 0 and FFT in 2
        try:
            self.display.draw_line(0, 0, xdata, ydata)
            self.display.draw_line(2, 0, xfft, yfft)
        except:
            print u"WARNING : Problem drawing stim to Window"

    def display_response(self, f, db, data, spectrum, freq):
        try:
        
            if self.current_operation == 0:
                sr = self.toneplayer.get_samplerate()
            else:
                sr = self.tonecurve.player.get_samplerate()

            spec_max, max_freq = get_fft_peak(spectrum, freq)
            spec_peak_at_f = spectrum[freq == f]
            if len(spec_peak_at_f) == 0:
                print u"COULD NOT FIND TARGET FREQUENCY ",f
                spec_peak_at_f = -1
                self.on_stop()

            vmax = np.amax(abs(data))
            
            # update GUI info display area
            self.ui.label1.setText(u"AI Vmax : %.5f" % (vmax))
            self.ui.label2.setText(u"FFT peak : %.6f, \t at %d Hz\n" % (np.amax(spectrum), max_freq))
            self.ui.label3.setText(u"FFT peak at %d kHz : %.6f" % (f/1000, spec_peak_at_f))
            if self.current_operation == 0 and self.apply_calibration:
                self.ui.label4.setText(u"Response dB : %.2f" % (calc_db(spec_peak_at_f, self.caldb, CALHACK)))

            if vmax < 0.005:
                if PRINT_WARNINGS:
                    print u"WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR"
                self.statusBar().showMessage(u"WARNING : RESPONSE VOLTAGE BELOW DEVICE FLOOR")
            else:
                self.statusBar().showMessage(u"")

            # tolerance of 1 Hz for frequency matching
            if max_freq < f-1 or max_freq > f+1:
                if PRINT_WARNINGS:
                    print u"WARNING : MAX SPECTRAL FREQUENCY DOES NOT MATCH STIMULUS"
                    print u"\tTarget : {}, Received : {}".format(f, max_freq)
            
            try:
                times = np.arange(len(data))/sr
                self.display.draw_line(1,0, times, data)
                self.display.draw_line(2,1, freq, spectrum)
                if self.current_operation == 1:
                    resultdb = calc_db(vmax, self.caldb, self.calval)
                    self.livecurve.set_point(f,db,resultdb)
            except:
                print u"WARNING : Problem drawing to Window"   
                     

            if self.current_operation == 0:
                if SAVE_FFT_DATA:
                    self.response_data_lock.lock()
                    self.full_fft_data.append(spectrum)
                    self.response_data_lock.unlock()

            self.nacquired +=1
        except:
            print u"Error processing response data"
            #self.on_stop()
            raise   

        #print('generated ', self.ngenerated, ', acquired ', self.nacquired, ', halted ', self.halt)
        
        if self.halt and self.ngenerated == self.nacquired:
            print u"Finished collecting, wrapping up..."
            self.live_lock.unlock()
                
            if self.current_operation == 1:
                # or should I emit a signal to execute this? 
                # I don't think it matters in the main thread
                self.on_stop()
                self.process_caldata()

    def finite_worker(self):
        #print("finite worker")
        while not self.halt:
            now = time.time()
            elapsed = (now - self.last_tick)*1000
            #print(self.last_tick, now)
            #print("interval %d, time from start %d \n" % (elapsed, (now - self.start_time)*1000))
            if elapsed < self.interval:
                #print('sleep ', (self.interval-elapsed))
                time.sleep((self.interval-elapsed)/1000)
                now = time.time()
            elif elapsed > self.interval:
                print u"WARNING: PROVIDED INTERVAL EXCEEDED, ELAPSED TIME %d" % (elapsed)
            self.last_tick = now

            self.ngenerated +=1
            data = self.toneplayer.read()
            self.toneplayer.reset()

            f, db = self.fdb
            self.signals.read_collected.emit(f, db, data[:])

    def calc_spectrum(self, f, db, data):
        try:
            if self.current_operation == 0:
                sr = self.toneplayer.get_samplerate()
            else:
                sr = self.tonecurve.player.get_samplerate()

            # extract information from acquired tone, and save
            freq, spectrum = calc_spectrum(data, sr)

            # take the abs (should I do this?), and get the highest peak
            spectrum = abs(spectrum)
        except:
            raise

        self.signals.done.emit(f, db, data, spectrum, freq)


    def set_interval_min(self):
        dur = self.ui.dur_spnbx.value()
        interval = self.ui.interval_spnbx.value()
        if interval < dur:
            print u"interval less than duration, increasing interval"
            self.ui.interval_spnbx.setValue(dur)
        if interval == dur:
            print u"Warning: No interval down-time, consider using continuous acquisition to avoid failure."

    def set_dur_max(self):
        dur = self.ui.dur_spnbx_2.value()
        reprate = self.ui.reprate_spnbx.value()
        if reprate < (dur/1000):
            self.ui.dur_spnbx_2.setValue(reprate*1000)

    def xor_applycal(self,checked):
        if checked:
            self.ui.applycal_ckbx.setChecked(False)

    def xor_savecal(self,checked):
        if checked:
            self.ui.savecal_ckbx.setChecked(False)

    def launch_display_dlg(self):
        field_vals = {u'chunksz' : self.ainpts, u'caldb': self.caldb, u'calv': self.calv, u'calf' : self.calf}
        dlg = DisplayDialog(default_vals=field_vals)
        if dlg.exec_():
            ainpts, caldb, calv, calf = dlg.get_values()
            if ainpts is not None:
                self.ainpts = ainpts
                self.caldb = caldb
                self.calv = calv
                self.calf = calf

    def launch_scaledlg(self):
        field_vals = {u'fscale' : self.fscale, u'tscale' : self.tscale}
        dlg = ScaleDialog(default_vals=field_vals)
        if dlg.exec_():
            fscale, tscale = dlg.get_values()
            self.fscale = fscale
            self.tscale = tscale
        self.update_unit_labels()

    def launch_savedlg(self):
        field_vals = {u'savefolder' : self.savefolder, u'savename' : self.savename, u'saveformat' : self.saveformat}
        dlg = SavingDialog(default_vals = field_vals)
        if dlg.exec_():
            savefolder, savename, saveformat = dlg.get_values()
            self.savefolder = savefolder
            self.savename = savename
            self.saveformat = saveformat

    def verify_inputs_valid(self):
        if self.ui.tabs.currentIndex() == 0 :
            f = self.ui.freq_spnbx.value()*self.fscale
            sr = self.ui.sr_spnbx.value()*self.fscale
            if sr < f*2:
                QtGui.QMessageBox.warning(self, u"Invalid parameter", u"Samplerate, %d Hz, must be at least 2x the maximum frequency, %d Hz" % (sr, f))
                return 0
            dur = self.ui.dur_spnbx.value()*self.tscale
            interval = self.ui.interval_spnbx.value()*self.tscale
            if dur > interval:
                QtGui.QMessageBox.warning(self, u"Invalid parameter", u"Duration, %.3f s, exceeds interval, %.3f s" % (dur, interval))
                return 0
        else:
            # verify that the calbration frequency and intensity are included in the curve
            f_start = self.ui.freq_start_spnbx.value()*self.fscale
            f_stop = self.ui.freq_stop_spnbx.value()*self.fscale
            f_step = self.ui.freq_step_spnbx.value()*self.fscale
            if self.calf not in range(f_start, f_stop+1, f_step):
                QtGui.QMessageBox.warning(self, u"Invalid parameter", u"Frequency range must include the specified calibration frequency, %d Hz" % (self.calf))
                return 0
            sr = self.ui.sr_spnbx_2.value()*self.fscale
            if sr < f_stop*2:
                QtGui.QMessageBox.warning(self, u"Invalid parameter", u"Samplerate, %d Hz,  must be at least 2x the maximum frequency, %d Hz" % (sr, f_stop))
                return 0
            reprate = self.ui.reprate_spnbx.value()
            dur = self.ui.dur_spnbx_2.value()*self.tscale
            if dur*reprate > 1:
                QtGui.QMessageBox.warning(self, u"Invalid parameter", u"Duration, %.3f s, exceeds interval allowed by reptition rate, %.2f reps/s" % (dur, reprate))
                return 0
        return 1

    def update_unit_labels(self):
        if self.fscale == 1000:
            self.ui.f_units.setText(u'kHz')
            self.ui.sr_units.setText(u'kHz')
            self.ui.aisr_units.setText(u'kHz')
        elif self.fscale == 1:
            self.ui.f_units.setText(u'Hz')
            self.ui.sr_units.setText(u'Hz')
            self.ui.aisr_units.setText(u'Hz')
        else:
            print self.fscale
            raise Exception(u"Invalid frequency scale")
            
        if self.tscale == 0.001:
            self.ui.dur_units.setText(u'ms')
            self.ui.interval_units.setText(u'ms')
            self.ui.risefall_units.setText(u'ms')
        elif self.tscale == 1:
            self.ui.dur_units.setText(u's')
            self.ui.interval_units.setText(u's')
            self.ui.risefall_units.setText(u's')
        else:
            print self.tscale
            raise Exception(u"Invalid time scale")
            
    def keyPressEvent(self,event):
        print u"keypress from calibrator"
        #print(event.text())
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            if self.current_operation == 0:
                if self.verify_inputs_valid():
                    self.update_stim()
            self.setFocus()
        elif event.key () == QtCore.Qt.Key_Escape:
            self.setFocus()
        elif event.text() == u'r':
            print u"redraw"
            self.display.redraw()
        
    def closeEvent(self,event):
        # halt acquisition loop
        self.on_stop()

        outlist = []
        #save inputs into file to load up next time - order is important
        outlist.append(self.ui.freq_spnbx.value())
        outlist.append(self.ui.sr_spnbx.value())
        outlist.append(self.ui.dur_spnbx.value())
        outlist.append(self.ui.db_spnbx.value())
        outlist.append(self.ui.risefall_spnbx.value())
        outlist.append(self.ui.aochan_box.currentIndex())
        outlist.append(self.ui.aichan_box.currentIndex())
        outlist.append(self.ainpts)
        outlist.append(self.ui.aisr_spnbx.value())
        outlist.append(self.ui.interval_spnbx.value())

        outlist.append(self.ui.freq_start_spnbx.value())
        outlist.append(self.ui.freq_stop_spnbx.value())
        outlist.append(self.ui.freq_step_spnbx.value())
        outlist.append(self.ui.db_start_spnbx.value())
        outlist.append(self.ui.db_stop_spnbx.value())
        outlist.append(self.ui.db_step_spnbx.value())
        outlist.append(self.ui.dur_spnbx_2.value())
        outlist.append(self.ui.risefall_spnbx_2.value())
        outlist.append(self.ui.reprate_spnbx.value())
        outlist.append(self.ui.sr_spnbx_2.value())
        outlist.append(self.ui.nreps_spnbx.value())

        outlist.append(self.caldb)
        outlist.append(self.calv)
        outlist.append(self.calf)
        outlist.append(self.savefolder)
        outlist.append(self.savename)
        outlist.append(self.saveformat)

        save_inputs(outlist)

        QtGui.QMainWindow.closeEvent(self,event)

def load_inputs():
    cfgfile = "inputs.cfg"
    try:
        with open(cfgfile, 'rb') as cfo:
            input_list = pickle.load(cfo)
    except:
        print("error loading user inputs file")
        #raise
        input_list = []
    return input_list

def save_inputs(savelist):
    #should really do this with a dict
    cfgfile = "inputs.cfg"
    with open(cfgfile, 'wb') as cfo:
        pickle.dump(savelist,cfo)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = CalibrationWindow(devName)
    myapp.show()
    sys.exit(app.exec_())
